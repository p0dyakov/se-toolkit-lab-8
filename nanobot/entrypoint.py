from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
RESOLVED_PATH = ROOT / "config.resolved.json"
WORKSPACE_PATH = ROOT / "workspace"


def _set_if_present(target: dict[str, object], key: str, env_name: str) -> None:
    value = os.environ.get(env_name, "").strip()
    if value:
        target[key] = value


def _set_port_if_present(target: dict[str, object], key: str, env_name: str) -> None:
    value = os.environ.get(env_name, "").strip()
    if value:
        target[key] = int(value)


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text())

    agents = config.setdefault("agents", {}).setdefault("defaults", {})
    providers = config.setdefault("providers", {}).setdefault("custom", {})
    gateway = config.setdefault("gateway", {})
    channels = config.setdefault("channels", {})
    webchat = channels.setdefault("webchat", {})
    tools = config.setdefault("tools", {})
    mcp_servers = tools.setdefault("mcpServers", {})
    lms = mcp_servers.setdefault("lms", {"command": "python", "args": ["-m", "mcp_lms"], "env": {}})
    mcp_obs = mcp_servers.setdefault("obs", {"command": "python", "args": ["-m", "mcp_obs"], "env": {}})
    mcp_webchat = mcp_servers.setdefault("webchat", {"command": "python", "args": ["-m", "mcp_webchat"], "env": {}})

    _set_if_present(providers, "apiKey", "LLM_API_KEY")
    _set_if_present(providers, "apiBase", "LLM_API_BASE_URL")
    _set_if_present(agents, "model", "LLM_API_MODEL")

    _set_if_present(gateway, "host", "NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    _set_port_if_present(gateway, "port", "NANOBOT_GATEWAY_CONTAINER_PORT")

    webchat["enabled"] = True
    webchat["allowFrom"] = ["*"]
    _set_if_present(webchat, "host", "NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    _set_port_if_present(webchat, "port", "NANOBOT_WEBCHAT_CONTAINER_PORT")

    lms_env = lms.setdefault("env", {})
    _set_if_present(lms_env, "NANOBOT_LMS_BACKEND_URL", "NANOBOT_LMS_BACKEND_URL")
    _set_if_present(lms_env, "NANOBOT_LMS_API_KEY", "NANOBOT_LMS_API_KEY")

    obs_env = mcp_obs.setdefault("env", {})
    _set_if_present(obs_env, "NANOBOT_VICTORIALOGS_URL", "NANOBOT_VICTORIALOGS_URL")
    _set_if_present(obs_env, "NANOBOT_VICTORIATRACES_URL", "NANOBOT_VICTORIATRACES_URL")

    relay_host = os.environ.get("NANOBOT_UI_RELAY_HOST", "127.0.0.1").strip() or "127.0.0.1"
    relay_port = os.environ.get("NANOBOT_UI_RELAY_PORT", "8766").strip() or "8766"
    relay_token = os.environ.get("NANOBOT_UI_RELAY_TOKEN", os.environ.get("NANOBOT_ACCESS_KEY", "")).strip()
    os.environ["NANOBOT_UI_RELAY_HOST"] = relay_host
    os.environ["NANOBOT_UI_RELAY_PORT"] = relay_port
    if relay_token:
        os.environ["NANOBOT_UI_RELAY_TOKEN"] = relay_token

    webchat["relayHost"] = relay_host
    webchat["relayPort"] = int(relay_port)

    webchat_env = mcp_webchat.setdefault("env", {})
    webchat_env["NANOBOT_UI_RELAY_URL"] = os.environ.get(
        "NANOBOT_UI_RELAY_URL", f"http://{relay_host}:{relay_port}"
    )
    webchat_env["NANOBOT_UI_RELAY_TOKEN"] = relay_token

    RESOLVED_PATH.write_text(json.dumps(config, indent=2) + "\n")

    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            str(RESOLVED_PATH),
            "--workspace",
            str(WORKSPACE_PATH),
        ],
    )


if __name__ == "__main__":
    main()
