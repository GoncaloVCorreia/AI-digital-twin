# Use a slim Python base
FROM python:3.12-slim

# System deps (libpq for psycopg, gcc can be useful if wheels not available)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 gcc curl ca-certificates \
  && update-ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Faster Python, no .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install uv (Astral) to manage deps from pyproject.toml
RUN pip install --no-cache-dir uv

# Copy dependency files first for better build cache
COPY pyproject.toml ./
# Copy uv.lock *if it exists* locally; the wildcard won't break if it doesn't.
COPY uv.lock* ./

# Sync deps into a local venv; if uv.lock is present, it will be used; else it resolves fresh.
RUN PIP_INDEX_URL=https://pypi.org/simple \
    PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu \
    PIP_PREFER_BINARY=1 \
    CUDA_VISIBLE_DEVICES="" \
    uv sync --no-dev --python 3.12

# Make the venv available on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of your source
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Default env values (overridable by docker-compose)
ENV DATABASE_URL=postgresql+psycopg://correia:postgres@db:5432/ai_project_db
ENV CHECKPOINT_URL=postgresql://correia:postgres@db:5432/ai_project_db?options=-c%20client_encoding%3DUTF8

# Dev-friendly run (reload works if you mount the code via volumes)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
