FROM mcr.microsoft.com/playwright/python:v1.57.0-noble

WORKDIR /app

# Install Node.js (not included in Playwright Python image)
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy TypeScript config files
COPY playwright.config.ts tsconfig.json ./

# Copy application code
COPY . .

EXPOSE 7860

# Gradio must listen on all interfaces for Docker
ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["python", "src/app.py"]