FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy the entire vallm project
COPY . /vallm
WORKDIR /vallm

# Install additional dependencies
COPY examples/12_ollama_simple_demo/requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install vallm in editable mode
RUN pip install -e ".[llm]"

# Set working directory for demo
WORKDIR /vallm/examples/12_ollama_simple_demo

# Start script
COPY examples/12_ollama_simple_demo/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["bash"]
