---
name: observability
description: Investigate LMS and backend failures using VictoriaLogs and VictoriaTraces tools
always: true
---

# Observability Skill

Use observability tools whenever the user asks about errors, traces, incidents, failures, outages, request health, or what went wrong.

## Available tools

- `mcp_obs_logs_error_count`: count recent errors per service
- `mcp_obs_logs_search`: inspect recent logs and extract evidence such as `trace_id`, service name, event, and error message
- `mcp_obs_traces_list`: list recent traces for a service
- `mcp_obs_traces_get`: inspect a specific trace by trace ID

## Investigation flow

- For questions like `Any LMS backend errors in the last 10 minutes?`, start with `mcp_obs_logs_error_count` using a narrow recent window.
- If there are recent errors, call `mcp_obs_logs_search` for the relevant service and extract the newest useful `trace_id`.
- If a `trace_id` exists, call `mcp_obs_traces_get` and inspect the failing path before answering.
- For `What went wrong?` or `Check system health`, summarize both log evidence and trace evidence in one short answer.
- For `What went wrong?`, explicitly mention the affected service, the failing operation, the key error from logs, and what the trace shows.
- Prefer the LMS backend and closely related services over older unrelated system errors.
- Use the freshest evidence possible. Narrow the time window rather than summarizing stale history.

## Proactive checks

- If the user asks to create a recurring health check for the current chat, use the built-in `cron` tool.
- Health-check jobs should inspect recent LMS and backend errors over the requested time window, then inspect a trace if a relevant `trace_id` exists.
- Each scheduled report should post a short in-chat summary. If no recent backend errors are found, say the system looks healthy.
- If the user asks to list, update, or remove scheduled jobs, use the `cron` tool instead of describing jobs hypothetically.

## Response style

- Keep answers concise and operational.
- Mention the affected service, the failing operation, and the likely root cause.
- Do not dump raw JSON unless the user explicitly asks for it.
- If there are no recent backend errors, say the system looks healthy.
