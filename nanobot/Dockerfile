ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0 UV_NO_DEV=1
WORKDIR /app
COPY --from=workspace pyproject.toml uv.lock /app/
COPY pyproject.toml /app/nanobot/pyproject.toml
COPY --from=workspace mcp/mcp-lms/pyproject.toml /app/mcp/mcp-lms/pyproject.toml
COPY --from=workspace mcp/mcp-obs/pyproject.toml /app/mcp/mcp-obs/pyproject.toml
COPY --from=workspace nanobot-websocket-channel/pyproject.toml /app/nanobot-websocket-channel/pyproject.toml
COPY --from=workspace nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml /app/nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml
COPY --from=workspace nanobot-websocket-channel/mcp-webchat/pyproject.toml /app/nanobot-websocket-channel/mcp-webchat/pyproject.toml
COPY --from=workspace nanobot-websocket-channel/nanobot-webchat/pyproject.toml /app/nanobot-websocket-channel/nanobot-webchat/pyproject.toml
COPY --from=workspace nanobot-websocket-channel/client-telegram-bot/pyproject.toml /app/nanobot-websocket-channel/client-telegram-bot/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package nanobot
COPY . /app/nanobot
COPY --from=workspace mcp /app/mcp
COPY --from=workspace nanobot-websocket-channel /app/nanobot-websocket-channel
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot

FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm
ARG APP_UID=1000
ARG APP_GID=1000
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LANG=C.UTF-8
RUN groupadd --gid ${APP_GID} appgroup \
    && useradd --uid ${APP_UID} --gid ${APP_GID} --create-home appuser
COPY --from=builder --chown=${APP_UID}:${APP_GID} /app /app
ENV PATH="/app/.venv/bin:$PATH"
USER appuser
WORKDIR /app
CMD ["python", "/app/nanobot/entrypoint.py"]
