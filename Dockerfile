FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY ml/ ./ml/
COPY gemini/ ./gemini/
COPY data/ ./data/

# Bake the synthetic demo dataset into the image (generation is seeded, so
# this is reproducible). DB_BACKEND defaults to "local" at this point (unset),
# so this seeds local_data/db.json - lets the image run standalone on a
# platform like Render with no attached database. Ignored at runtime if
# DB_BACKEND=firestore is set instead.
RUN python -m data.seed.generate_synthetic_data && python -m data.seed.seed

RUN useradd --create-home --shell /bin/false appuser && chown -R appuser:appuser /app
USER appuser

ENV PORT=8080
EXPOSE 8080

# Render/Cloud Run both inject $PORT; uvicorn must bind to it (shell form so $PORT expands)
CMD exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT}
