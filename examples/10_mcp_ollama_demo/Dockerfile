FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

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

# Expose Ollama API port
EXPOSE 11434

# Start Ollama and pull model, then keep running
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["bash"]
