"""Typed models for observability MCP responses."""

from __future__ import annotations

from pydantic import BaseModel


class LogRecord(BaseModel):
    timestamp: str = ""
    severity: str = ""
    service: str = ""
    event: str = ""
    message: str = ""
    trace_id: str = ""
    raw: dict[str, object] = {}


class ErrorCount(BaseModel):
    service: str
    errors: int


class TraceSummary(BaseModel):
    trace_id: str
    service: str = ""
    operation: str = ""
    start_time: int | None = None
    duration_ms: float | None = None
    span_count: int = 0


class TraceDetail(BaseModel):
    trace_id: str
    services: list[str]
    root_operation: str = ""
    spans: list[dict[str, object]]
