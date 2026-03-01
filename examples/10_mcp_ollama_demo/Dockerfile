FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Use local Ollama - don't install in container

# Set up working directory
WORKDIR /app

# Copy the entire vallm project
COPY . /vallm
WORKDIR /vallm

# Install additional dependencies
RUN pip install --no-cache-dir code2llm code2logic requests

# Install vallm in editable mode
RUN pip install -e ".[llm]"

# Set working directory for demo
WORKDIR /vallm/examples/10_mcp_ollama_demo

# No need to expose Ollama port - using local instance

# Start Ollama and pull model, then keep running
COPY examples/10_mcp_ollama_demo/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["bash"]
