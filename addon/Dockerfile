ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip

# Set working directory
WORKDIR /app

# Copy requirements
COPY server/requirements.txt .

# Install Python dependencies
# Use --break-system-packages since this is an isolated container
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy server code
COPY server/ ./server/

# Copy run script
COPY run.sh /
RUN chmod +x /run.sh

# Run script
CMD ["/run.sh"]
