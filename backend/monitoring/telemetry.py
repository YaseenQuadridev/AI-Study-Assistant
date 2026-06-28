"""monitoring/telemetry.py — OpenTelemetry tracing and metrics."""
from __future__ import annotations

import os
from contextvars import ContextVar

CORRELATION_ID = ContextVar("correlation_id", default="")


class Telemetry:
    def __init__(self, service_name: str = "adaptive-study-planner"):
        self.service_name = service_name
        self._tracer = None
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            provider = TracerProvider()
            provider.add_span_processor(BatchSpanProcessor(JaegerExporter(
                agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
                agent_port=int(os.getenv("JAEGER_PORT", "6831")),
            )))
            trace.set_tracer_provider(provider)
            self._tracer = trace.get_tracer(service_name)
        except Exception:
            pass

    def start_span(self, name: str, attributes: dict = None):
        if self._tracer:
            return self._tracer.start_as_current_span(name, attributes=attributes)
        return _NoOpSpan()

    def record_metric(self, name: str, value: float, labels: dict = None):
        # In production, use Prometheus or Cloudflare Analytics
        pass


class _NoOpSpan:
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def set_attribute(self, key, value): pass
    def record_exception(self, exc): pass
