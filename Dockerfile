FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Note: CMD is overridden by docker-compose.yml command
# This is just a fallback if run without docker-compose
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]


