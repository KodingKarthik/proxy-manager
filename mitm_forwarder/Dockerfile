FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy addon files
COPY . .

# Create directory for mitmproxy config
RUN mkdir -p /tmp/mitmproxy

# Expose mitmproxy port
EXPOSE 8080

# Set environment variable for port (can be overridden)
ENV MITM_LISTEN_PORT=8080

# Run mitmdump with the addon
ENTRYPOINT ["sh", "-c", "mitmdump -s mitm_forwarder_addon.py -p ${MITM_LISTEN_PORT} --set confdir=/tmp/mitmproxy"]

