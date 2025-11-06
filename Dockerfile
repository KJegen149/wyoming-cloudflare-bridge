FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ ./server/

# Expose Wyoming protocol port
EXPOSE 10300

# Run the server
ENTRYPOINT ["python", "-m", "server"]
