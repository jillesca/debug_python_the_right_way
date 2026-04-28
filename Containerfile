# ---- builder stage ----
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-cache

COPY answer/get_interfaces.py ./

# ---- runtime stage ----
FROM python:3.10-slim-bookworm AS runtime

RUN useradd --create-home appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/get_interfaces.py ./

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

CMD ["python", "get_interfaces.py"]
