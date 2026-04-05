FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-install-project
COPY . .
RUN uv sync --frozen --no-cache

EXPOSE 8080
CMD [".venv/bin/uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8080"]
