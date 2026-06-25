# --- Build a small production image for the API ---
FROM python:3.12-slim

# Don't write .pyc files; flush stdout/stderr immediately (better logs).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first so Docker can cache this layer when only code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY app/ ./app/

# Render/Railway/Fly inject a PORT env var; default to 8000 locally.
ENV PORT=8000
EXPOSE 8000

# Start the server.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
