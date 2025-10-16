FROM python:3.11-slim AS base
WORKDIR /app
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir uv
RUN uv pip install --system -r <(python - <<'PY'\nimport tomllib,sys;print('\n'.join(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']))\nPY)
COPY backend/app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]