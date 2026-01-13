FROM mcr.microsoft.com/playwright/python:v1.57.0-noble

LABEL maintainer="QA Team"
LABEL description="LM Studio QA Agent"

WORKDIR /app

# Install Node.js (not included in Playwright Python image)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Playwright-related environment variables
# This ensures that the pre-installed browsers in the base image are used
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
# Gradio settings
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7860
# Python settings
ENV PYTHONUNBUFFERED=1

# Install Node.js dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy configuration files
COPY playwright.config.ts tsconfig.json ./

# Copy application code
COPY . .

EXPOSE 7860

CMD ["python", "src/app.py"]