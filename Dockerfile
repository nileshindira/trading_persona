FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed data/reports

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

# Expose port (if running as service)
EXPOSE 5000

# Default command
CMD ["python", "main.py", "--help"]
