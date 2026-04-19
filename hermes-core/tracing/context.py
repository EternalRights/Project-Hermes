import threading

from .trace_id import TraceContext, TraceIDGenerator


class TraceContextManager:

    _local = threading.local()

    @classmethod
    def set_current(cls, context: TraceContext):
        cls._local.context = context

    @classmethod
    def get_current(cls) -> TraceContext:
        return getattr(cls._local, "context", None)

    @classmethod
    def clear(cls):
        if hasattr(cls._local, "context"):
            del cls._local.context

    @classmethod
    def new_trace(cls) -> TraceContext:
        context = TraceContext()
        cls.set_current(context)
        return context

    @classmethod
    def new_span(cls) -> TraceContext:
        current = cls.get_current()
        if current is None:
            return cls.new_trace()
        child = TraceContext(trace_id=current.trace_id)
        child.parent_span_id = current.span_id
        cls.set_current(child)
        return child
