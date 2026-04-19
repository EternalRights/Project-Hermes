import time
import uuid


class TraceIDGenerator:

    @staticmethod
    def generate() -> str:
        hex_part = uuid.uuid4().hex[:16]
        timestamp = str(int(time.time() * 1000))
        return f"hermes-{hex_part}-{timestamp}"


class TraceContext:

    def __init__(self, trace_id=None):
        self.trace_id = trace_id or TraceIDGenerator.generate()
        self.span_id = f"span-{uuid.uuid4().hex[:8]}"
        self.parent_span_id = None
        self.attributes = {}

    def add_attribute(self, key, value):
        self.attributes[key] = value

    def to_headers(self) -> dict:
        return {
            "X-Trace-ID": self.trace_id,
            "X-Span-ID": self.span_id,
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
