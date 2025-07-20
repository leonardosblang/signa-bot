FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for crawl4ai and playwright
RUN apt-get update && apt-get install -y \
    # Build essentials
    gcc \
    g++ \
    git \
    # Browser dependencies for crawl4ai/playwright
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Setup crawl4ai and playwright browsers
RUN crawl4ai-setup && \
    python -m playwright install --with-deps chromium

COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV DISPLAY=:99
ENV CRAWL4AI_BROWSER_TYPE=chromium

# Expose ports for API and Streamlit
EXPOSE 8000 8501

# Create comprehensive startup script
RUN echo '#!/bin/bash\n\
# Start virtual display for headless browsers\n\
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\n\
\n\
case "$1" in\n\
    "api")\n\
        echo "Starting FastAPI server..."\n\
        python run_api.py\n\
        ;;\n\
    "web")\n\
        echo "Starting Streamlit interface..."\n\
        python run_web.py\n\
        ;;\n\
    "cli")\n\
        echo "Starting CLI interface..."\n\
        python main.py\n\
        ;;\n\
    "setup")\n\
        echo "Running setup and tests..."\n\
        crawl4ai-setup\n\
        python -c "import crawl4ai; print(\"Crawl4AI version:\", crawl4ai.__version__)"\n\
        ;;\n\
    *)\n\
        echo "Signa Chatbot - Multi-Interface"\n\
        echo "Usage: docker run <image> [api|web|cli|setup]"\n\
        echo ""\n\
        echo "Interfaces:"\n\
        echo "  api   - FastAPI server on port 8000"\n\
        echo "  web   - Streamlit interface on port 8501"\n\
        echo "  cli   - Interactive CLI interface"\n\
        echo "  setup - Verify crawl4ai installation"\n\
        echo ""\n\
        echo "Environment variables:"\n\
        echo "  OPENAI_API_KEY - Required OpenAI API key"\n\
        echo "  DEBUG_MODE     - Enable debug logging (default: False)"\n\
        ;;\n\
esac' > /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

CMD ["/app/docker-entrypoint.sh", "api"]