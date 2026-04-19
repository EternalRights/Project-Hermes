import re

from hermes_core.tracing.trace_id import TraceIDGenerator, TraceContext
from hermes_core.tracing.context import TraceContextManager
from hermes_core.tracing.propagation import TracePropagator

import pytest


def test_trace_id_generate():
    trace_id = TraceIDGenerator.generate()
    assert trace_id.startswith("hermes-")
    parts = trace_id.split("-")
    assert len(parts) >= 3
    hex_part = parts[1]
    assert len(hex_part) == 16
    assert re.match(r"^[0-9a-f]{16}$", hex_part)


def test_trace_context_to_headers():
    ctx = TraceContext(trace_id="hermes-abc12345678901234-1234567890")
    headers = ctx.to_headers()
    assert "X-Trace-ID" in headers
    assert headers["X-Trace-ID"] == "hermes-abc12345678901234-1234567890"
    assert "X-Span-ID" in headers
    assert headers["X-Span-ID"].startswith("span-")


def test_trace_context_manager_new_trace():
    TraceContextManager.clear()
    ctx = TraceContextManager.new_trace()
    assert ctx is not None
    assert ctx.trace_id.startswith("hermes-")
    assert ctx.span_id.startswith("span-")
    assert ctx.parent_span_id is None
    current = TraceContextManager.get_current()
    assert current is ctx
    TraceContextManager.clear()


def test_trace_context_manager_new_span():
    TraceContextManager.clear()
    parent_ctx = TraceContextManager.new_trace()
    child_ctx = TraceContextManager.new_span()
    assert child_ctx.trace_id == parent_ctx.trace_id
    assert child_ctx.parent_span_id == parent_ctx.span_id
    assert child_ctx.span_id != parent_ctx.span_id
    current = TraceContextManager.get_current()
    assert current is child_ctx
    TraceContextManager.clear()


def test_trace_propagation_inject_extract():
    propagator = TracePropagator()
    ctx = TraceContext(trace_id="hermes-abcdef1234567890-1234567890")
    ctx.parent_span_id = "span-parent01"
    headers = propagator.inject({}, ctx)
    assert headers["X-Trace-ID"] == "hermes-abcdef1234567890-1234567890"
    assert headers["X-Span-ID"] == ctx.span_id
    assert headers["X-Parent-Span-ID"] == "span-parent01"
    extracted = propagator.extract(headers)
    assert extracted.trace_id == ctx.trace_id
    assert extracted.span_id == ctx.span_id
    assert extracted.parent_span_id == "span-parent01"
