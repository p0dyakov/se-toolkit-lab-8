"""Async clients for VictoriaLogs and VictoriaTraces APIs."""

from __future__ import annotations

from collections import Counter
import json
from typing import cast

import httpx

from mcp_obs.models import ErrorCount, LogRecord, TraceDetail, TraceSummary


class ObservabilityClient:
    def __init__(
        self,
        victorialogs_url: str,
        victoriatraces_url: str,
        *,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.victorialogs_url = victorialogs_url.rstrip("/")
        self.victoriatraces_url = victoriatraces_url.rstrip("/")
        self._owns_client = http_client is None
        self._http = http_client or httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> "ObservabilityClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    @staticmethod
    def _to_float(value: object) -> float:
        if isinstance(value, bool):
            return float(int(value))
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        return 0.0

    async def logs_search(
        self,
        *,
        keyword: str = "",
        minutes: int = 60,
        service: str = "",
        severity: str = "",
        limit: int = 20,
    ) -> list[LogRecord]:
        terms = [f"_time:{minutes}m"]
        if service:
            terms.append(f'service.name:"{service}"')
        if severity:
            terms.append(f"severity:{severity.upper()}")
        if keyword:
            terms.append(keyword)
        query = " ".join(terms)
        response = await self._http.get(
            f"{self.victorialogs_url}/select/logsql/query",
            params={"query": query, "limit": limit},
        )
        response.raise_for_status()
        records: list[LogRecord] = []
        for line in response.text.splitlines():
            if not line.strip():
                continue
            payload = cast(dict[str, object], json.loads(line))
            records.append(
                LogRecord(
                    timestamp=str(payload.get("_time", "")),
                    severity=str(payload.get("severity", "")),
                    service=str(payload.get("service.name", "")),
                    event=str(payload.get("event", "")),
                    message=str(payload.get("_msg", payload.get("body", ""))),
                    trace_id=str(payload.get("trace_id", "")),
                    raw=payload,
                )
            )
        return records

    async def logs_error_count(
        self,
        *,
        minutes: int = 60,
        service: str = "",
    ) -> list[ErrorCount]:
        records = await self.logs_search(
            minutes=minutes,
            service=service,
            severity="ERROR",
            limit=200,
        )
        counter = Counter(record.service or "unknown" for record in records)
        return [ErrorCount(service=name, errors=count) for name, count in counter.items()]

    async def traces_list(
        self,
        *,
        service: str,
        limit: int = 10,
    ) -> list[TraceSummary]:
        response = await self._http.get(
            f"{self.victoriatraces_url}/select/jaeger/api/traces",
            params={"service": service, "limit": limit},
        )
        response.raise_for_status()
        payload = cast(dict[str, object], response.json())
        traces = cast(list[dict[str, object]], payload.get("data", []))
        result: list[TraceSummary] = []
        for item in traces:
            spans = cast(list[dict[str, object]], item.get("spans", []))
            root = spans[0] if spans else {}
            process = cast(dict[str, object], root.get("process", {}))
            result.append(
                TraceSummary(
                    trace_id=str(item.get("traceID", "")),
                    service=str(process.get("serviceName", service)),
                    operation=str(root.get("operationName", "")),
                    start_time=cast(int | None, root.get("startTime")),
                    duration_ms=self._to_float(root.get("duration", 0)) / 1000.0,
                    span_count=len(spans),
                )
            )
        return result

    async def traces_get(self, *, trace_id: str) -> TraceDetail:
        response = await self._http.get(
            f"{self.victoriatraces_url}/select/jaeger/api/traces/{trace_id}"
        )
        response.raise_for_status()
        payload = cast(dict[str, object], response.json())
        data = cast(list[dict[str, object]], payload.get("data", []))
        trace = data[0] if data else {}
        processes = cast(dict[str, dict[str, object]], trace.get("processes", {}))
        spans = cast(list[dict[str, object]], trace.get("spans", []))
        services = sorted(
            {
                str(
                    processes.get(str(span.get("processID", "")), {}).get(
                        "serviceName", ""
                    )
                )
                for span in spans
                if processes.get(str(span.get("processID", "")), {}).get(
                    "serviceName", ""
                )
            }
        )
        normalized_spans: list[dict[str, object]] = []
        for span in spans:
            process = processes.get(str(span.get("processID", "")), {})
            normalized_spans.append(
                {
                    "span_id": span.get("spanID", ""),
                    "operation": span.get("operationName", ""),
                    "service": process.get("serviceName", ""),
                    "start_time": span.get("startTime"),
                    "duration_ms": self._to_float(span.get("duration", 0)) / 1000.0,
                    "tags": span.get("tags", []),
                    "references": span.get("references", []),
                }
            )
        root_operation = str(normalized_spans[0]["operation"]) if normalized_spans else ""
        return TraceDetail(
            trace_id=trace_id,
            services=services,
            root_operation=root_operation,
            spans=normalized_spans,
        )
