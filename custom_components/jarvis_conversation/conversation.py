import json
import logging
import re
from typing import Literal

import aiohttp

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, intent
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_LLM_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

_HISTORY: dict[str, list[dict]] = {}

_PRIORITY_DOMAINS = {
    "light", "switch", "climate", "lock", "cover",
    "fan", "media_player", "input_boolean", "input_select",
}
_INFO_DOMAINS = {"sensor", "binary_sensor"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([JarvisConversationEntity(hass, entry)])


class JarvisConversationEntity(conversation.ConversationEntity):
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass     = hass
        self._entry   = entry
        self._llm_url = entry.data[CONF_LLM_URL]
        self._attr_unique_id = entry.entry_id
        self._attr_name      = "Jarvis"

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return "*"

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:

        conv_id = user_input.conversation_id or user_input.device_id or "default"
        history = _HISTORY.get(conv_id, [])

        _LOGGER.debug("Jarvis conv_id=%s history_len=%d text=%s", conv_id, len(history), user_input.text)

        speech, service_call = await self._call_llm(
            text=user_input.text,
            history=history,
            conversation_id=conv_id,
        )

        # Execute the HA service call if the LLM requested one
        if service_call:
            try:
                service_data = {}
                entity_id = service_call.get("entity_id")
                if entity_id:
                    service_data["entity_id"] = entity_id
                service_data.update(service_call.get("data") or {})

                await self.hass.services.async_call(
                    domain=service_call["domain"],
                    service=service_call["service"],
                    service_data=service_data,
                    blocking=True,
                )
                _LOGGER.debug(
                    "Executed %s.%s on %s",
                    service_call["domain"],
                    service_call["service"],
                    entity_id,
                )
            except Exception as exc:
                _LOGGER.error("Service call failed: %s", exc)
                speech += " Though I had trouble executing that — please check the device."

        # Store clean speech text in history (never raw JSON)
        history.append({"role": "user",      "content": user_input.text})
        history.append({"role": "assistant", "content": speech})
        _HISTORY[conv_id] = history[-20:]

        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(speech)

        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=conv_id,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_device_list(self) -> list[dict]:
        """
        Smart entity filtering:
        - Skips unavailable/unknown states
        - Skips diagnostic and config category entities (battery, signal, etc.)
        - Skips disabled entities
        - All controllable devices included without cap
        - Sensors capped at 30 to keep token cost reasonable
        """
        ent_reg   = er.async_get(self.hass)
        priority  = []
        info      = []

        for state in self.hass.states.async_all():
            # Skip useless states
            if state.state in ("unavailable", "unknown"):
                continue

            # Skip diagnostic / config / disabled via entity registry
            reg_entry = ent_reg.async_get(state.entity_id)
            if reg_entry:
                if reg_entry.disabled:
                    continue
                if reg_entry.entity_category in (
                    EntityCategory.DIAGNOSTIC,
                    EntityCategory.CONFIG,
                ):
                    continue

            entry = {
                "name":      state.attributes.get("friendly_name", state.entity_id),
                "entity_id": state.entity_id,
                "state":     state.state,
            }

            if state.domain in _PRIORITY_DOMAINS:
                priority.append(entry)
            elif state.domain in _INFO_DOMAINS:
                info.append(entry)

        _LOGGER.debug(
            "Device list: %d controllable, %d sensors (capped at 30)",
            len(priority), len(info),
        )
        return priority + info[:30]

    @staticmethod
    def _parse_llm_response(raw: str) -> tuple[str, dict | None]:
        """
        Parse the LLM's JSON response.
        Handles markdown code blocks (```json ... ```) that some models add.
        Falls back gracefully to raw text if JSON is malformed.
        """
        # Strip markdown code fences
        text = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text.strip())
        text = text.strip()

        try:
            parsed  = json.loads(text)
            speech  = parsed.get("speech") or raw
            service = parsed.get("service")  # dict or None
            return speech, service
        except (json.JSONDecodeError, TypeError, AttributeError):
            _LOGGER.debug("LLM response was not JSON, using raw text: %s", raw[:80])
            return raw or "I couldn't generate a response.", None

    async def _call_llm(
        self,
        text: str,
        history: list,
        conversation_id: str,
    ) -> tuple[str, dict | None]:
        payload = {
            "text":            text,
            "conversation_id": conversation_id,
            "history":         history,
            "device_list":     self._get_device_list(),
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._llm_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=12),
                ) as resp:
                    if resp.status != 200:
                        _LOGGER.error("LLM worker returned HTTP %s", resp.status)
                        return "I'm having trouble connecting right now.", None

                    data = await resp.json()
                    raw  = data.get("text", "")
                    return self._parse_llm_response(raw)

        except TimeoutError:
            return "That took too long. Please try again.", None
        except Exception as exc:
            _LOGGER.error("Jarvis LLM call failed: %s", exc)
            return "I encountered an error. Please try again.", None
