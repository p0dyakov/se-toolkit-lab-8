"""Tool registry for observability MCP."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import TypeVar

from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_obs.client import ObservabilityClient


class LogsSearchQuery(BaseModel):
    keyword: str = Field(default="", description="Keyword or LogsQL fragment to search.")
    minutes: int = Field(default=60, ge=1, le=1440, description="How many recent minutes to search.")
    service: str = Field(default="", description="Optional service.name filter.")
    severity: str = Field(default="", description="Optional severity filter, for example ERROR.")
    limit: int = Field(default=20, ge=1, le=200, description="Maximum number of log lines.")


class ErrorCountQuery(BaseModel):
    minutes: int = Field(default=60, ge=1, le=1440, description="How many recent minutes to inspect.")
    service: str = Field(default="", description="Optional service.name filter.")


class TracesListQuery(BaseModel):
    service: str = Field(description="Service name to query in VictoriaTraces.")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum traces to return.")


class TraceGetQuery(BaseModel):
    trace_id: str = Field(description="Trace ID returned by logs or traces_list.")


ToolPayload = BaseModel | Sequence[BaseModel]
ToolHandler = Callable[[ObservabilityClient, BaseModel], Awaitable[ToolPayload]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    model: type[BaseModel]
    handler: ToolHandler

    def as_tool(self) -> Tool:
        schema = self.model.model_json_schema()
        schema.pop("$defs", None)
        schema.pop("title", None)
        return Tool(name=self.name, description=self.description, inputSchema=schema)


async def _logs_search(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = _require(args, LogsSearchQuery)
    return await client.logs_search(
        keyword=query.keyword,
        minutes=query.minutes,
        service=query.service,
        severity=query.severity,
        limit=query.limit,
    )


async def _logs_error_count(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = _require(args, ErrorCountQuery)
    return await client.logs_error_count(minutes=query.minutes, service=query.service)


async def _traces_list(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = _require(args, TracesListQuery)
    return await client.traces_list(service=query.service, limit=query.limit)


async def _traces_get(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = _require(args, TraceGetQuery)
    return await client.traces_get(trace_id=query.trace_id)


ModelT = TypeVar("ModelT", bound=BaseModel)

def _require(args: BaseModel, model: type[ModelT]) -> ModelT:
    if not isinstance(args, model):
        raise TypeError(f"Expected {model.__name__}, got {type(args).__name__}")
    return args


TOOL_SPECS = (
    ToolSpec(
        "logs_search",
        "Search VictoriaLogs by keyword, time range, service, and severity.",
        LogsSearchQuery,
        _logs_search,
    ),
    ToolSpec(
        "logs_error_count",
        "Count recent error logs per service over a time window.",
        ErrorCountQuery,
        _logs_error_count,
    ),
    ToolSpec(
        "traces_list",
        "List recent traces for a service from VictoriaTraces.",
        TracesListQuery,
        _traces_list,
    ),
    ToolSpec(
        "traces_get",
        "Fetch a specific trace by trace ID from VictoriaTraces.",
        TraceGetQuery,
        _traces_get,
    ),
)
TOOLS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}
