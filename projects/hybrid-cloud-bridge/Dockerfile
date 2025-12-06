FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and foundation
COPY src/ ./src/
# Foundation is mounted via docker-compose volume

ENV PYTHONPATH=/app:/app/foundation

CMD ["python", "-u", "src/bridge.py"]
