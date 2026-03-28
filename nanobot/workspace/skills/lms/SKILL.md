---
name: lms
description: Use LMS MCP tools for live LMS backend data and concise LMS answers
always: true
---

# LMS Skill

Use the `lms` MCP server whenever the user asks about labs, learners, scores, pass rates, completion, groups, top learners, timelines, backend health, or LMS data freshness.

## Available LMS tools

- `mcp_lms_lms_health`: check LMS health and report backend status or item count
- `mcp_lms_lms_labs`: list labs
- `mcp_lms_lms_learners`: list learners
- `mcp_lms_lms_pass_rates`: per-task pass rates for a lab
- `mcp_lms_lms_timeline`: submission timeline for a lab
- `mcp_lms_lms_groups`: group performance for a lab
- `mcp_lms_lms_top_learners`: top learners for a lab
- `mcp_lms_lms_completion_rate`: lab completion rate
- `mcp_lms_lms_sync_pipeline`: trigger LMS sync when data is missing or stale

## Strategy

- Prefer live LMS tools over guessing from repository docs.
- If the user asks what labs are available, call `mcp_lms_lms_labs`.
- If the user asks whether the backend is healthy, call `mcp_lms_lms_health`.
- If the user asks about scores, pass rates, completion, groups, timelines, or top learners without naming a lab, first call `mcp_lms_lms_labs` and ask the user to choose a lab.
- When a lab choice is needed, use clear labels like `lab-01`, `lab-02`, `lab-03`.
- If a tool reports no labs or empty data, consider calling `mcp_lms_lms_sync_pipeline` once and then retrying the relevant read tool.
- For comparisons such as "which lab has the lowest pass rate", gather the labs first and then inspect the relevant lab metrics before answering.
- Keep answers concise and factual.

## Formatting

- Show percentages with one decimal place when useful.
- Use short bullet lists for multiple labs or grouped metrics.
- Do not dump raw JSON unless the user explicitly asks for it.

## Limits

- If live LMS tools are unavailable, say that you cannot access live LMS data right now.
- Do not pretend repository docs are live backend results.
