# Fixing GitHub Repository Error

You're getting this error:
```
fatal: could not read Username for 'https://github.com': No such device or address
```

This means your repository is **private** or the structure is incorrect.

## Solution 1: Make Repository Public (Recommended)

### Step 1: Check if Repository is Private

1. Go to https://github.com/KJegen149/wyoming-cloudflare-bridge
2. Look at the top - does it say "Public" or "Private"?
3. If it says "Private", continue below

### Step 2: Make Repository Public

1. Go to your repository: https://github.com/KJegen149/wyoming-cloudflare-bridge
2. Click **Settings** (top right)
3. Scroll to bottom → **Danger Zone**
4. Click **Change visibility**
5. Select **Make public**
6. Confirm by typing the repository name
7. Click **I understand, change repository visibility**

### Step 3: Add repository.json

You need this file at the root of your repository for Home Assistant to recognize it as an add-on repository.

```bash
# In your local repository
cd wyoming-cloudflare-bridge

# repository.json is already created for you!
# Just commit and push it:
git add repository.json
git commit -m "Add repository.json for Home Assistant"
git push
```

### Step 4: Try Adding to Home Assistant Again

1. Settings → Add-ons → Add-on Store → ⋮ → Repositories
2. Remove the old repository if it's listed
3. Add: `https://github.com/KJegen149/wyoming-cloudflare-bridge`
4. It should work now!

## Solution 2: Keep Repository Private (Complex)

If you want to keep it private, you have two options:

### Option A: Use GitHub Personal Access Token

This is complex and not recommended for add-ons. Better to use Solution 3.

### Option B: Use Local Add-on Instead

Install directly without GitHub:

#### Step 1: Enable SSH

1. Install "Terminal & SSH" add-on
2. Configure password:
   ```yaml
   password: "YOUR_PASSWORD"
   ```
3. Start add-on
4. SSH in: `ssh root@YOUR_HA_IP -p 22222`

#### Step 2: Copy Add-on Files

From your computer:

```bash
# Copy add-on to Home Assistant
scp -P 22222 -r addon root@YOUR_HA_IP:/addons/local/wyoming-cloudflare-bridge/
scp -P 22222 -r server root@YOUR_HA_IP:/addons/local/wyoming-cloudflare-bridge/
```

#### Step 3: Reload Add-ons

1. Settings → Add-ons
2. Click ⋮ → Check for updates
3. Your add-on should appear under "Local add-ons"

## Solution 3: Quick Test Without Add-on (Fastest)

Skip the add-on entirely and test with Terminal:

Follow: [QUICK_HAOS_WORKAROUND.md](QUICK_HAOS_WORKAROUND.md)

This works immediately while you figure out GitHub.

## Checking Repository Structure

Home Assistant expects this structure:

```
wyoming-cloudflare-bridge/
├── repository.json          ← Required! (I created this for you)
├── addon/
│   ├── config.yaml         ← Required
│   ├── Dockerfile          ← Required
│   ├── run.sh              ← Required
│   ├── build.yaml
│   ├── README.md
│   └── DOCS.md
├── server/
│   ├── __init__.py
│   ├── __main__.py
│   ├── handler.py
│   └── requirements.txt
└── workers/
    └── ...
```

## Verify Your Repository

1. Go to: https://github.com/KJegen149/wyoming-cloudflare-bridge
2. Check these files exist:
   - ✅ `repository.json` (at root)
   - ✅ `addon/config.yaml`
   - ✅ `addon/Dockerfile`
   - ✅ `addon/run.sh`

If missing, commit and push:

```bash
git add repository.json addon/
git commit -m "Add repository.json and add-on structure"
git push
```

## Quick Diagnostic

Run this to check your repo status:

```bash
cd wyoming-cloudflare-bridge

# Check if repository.json exists
ls -la repository.json

# If not, it's already created - just commit it
git add repository.json
git commit -m "Add repository.json"
git push

# Check add-on structure
ls -la addon/

# Make sure these exist:
# - config.yaml
# - Dockerfile
# - run.sh
# - build.yaml
```

## Try This Order

1. **Make repository public** (easiest)
2. **Add repository.json** (already done)
3. **Commit and push changes**
4. **Try adding to Home Assistant again**

If still having issues:

```bash
# From your computer, verify you can clone it
git clone https://github.com/KJegen149/wyoming-cloudflare-bridge test-clone
cd test-clone
ls -la

# You should see:
# - repository.json
# - addon/ directory
# - server/ directory
# - workers/ directory
```

## Alternative: Test Without GitHub

While you sort out GitHub, test the functionality:

1. Use Terminal & SSH add-on
2. Follow [QUICK_HAOS_WORKAROUND.md](QUICK_HAOS_WORKAROUND.md)
3. Verify everything works
4. Then come back to fix GitHub

This way you can test the voice assistant while fixing the repository!

## Still Having Issues?

1. **Verify repository is public**: Check https://github.com/KJegen149/wyoming-cloudflare-bridge
2. **Check repository.json exists**: Look at files in GitHub web interface
3. **Verify add-on structure**: Check addon/ directory exists
4. **Try the workaround**: Use QUICK_HAOS_WORKAROUND.md to test without add-on

Let me know what you see and I can help further!
