ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0 UV_NO_DEV=1
WORKDIR /app
COPY pyproject.toml uv.lock /app/
COPY nanobot-websocket-channel/client-telegram-bot/pyproject.toml /app/nanobot-websocket-channel/client-telegram-bot/pyproject.toml
COPY nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml /app/nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package client-telegram-bot
COPY nanobot-websocket-channel/client-telegram-bot /app/nanobot-websocket-channel/client-telegram-bot
COPY nanobot-websocket-channel/nanobot-channel-protocol /app/nanobot-websocket-channel/nanobot-channel-protocol
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package client-telegram-bot

FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LANG=C.UTF-8
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot
COPY --from=builder --chown=nonroot:nonroot /app /app
ENV PATH="/app/.venv/bin:$PATH"
USER nonroot
WORKDIR /app
CMD ["opentelemetry-instrument", "python", "-m", "client_telegram_bot"]
