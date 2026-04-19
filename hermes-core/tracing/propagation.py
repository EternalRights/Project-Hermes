from .trace_id import TraceContext


class TracePropagator:

    TRACE_ID_HEADER = "X-Trace-ID"
    SPAN_ID_HEADER = "X-Span-ID"
    PARENT_SPAN_ID_HEADER = "X-Parent-Span-ID"

    def inject(self, headers: dict, context: TraceContext) -> dict:
        headers[self.TRACE_ID_HEADER] = context.trace_id
        headers[self.SPAN_ID_HEADER] = context.span_id
        if context.parent_span_id:
            headers[self.PARENT_SPAN_ID_HEADER] = context.parent_span_id
        return headers

    def extract(self, headers: dict) -> TraceContext:
        trace_id = headers.get(self.TRACE_ID_HEADER)
        span_id = headers.get(self.SPAN_ID_HEADER)
        parent_span_id = headers.get(self.PARENT_SPAN_ID_HEADER)

        context = TraceContext(trace_id=trace_id)
        if span_id:
            context.span_id = span_id
        if parent_span_id:
            context.parent_span_id = parent_span_id
        return context
