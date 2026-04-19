import hashlib
import hmac
import base64
import uuid
import random
import string
import time
from datetime import datetime, timezone


class BuiltinFunctions:

    @staticmethod
    def random_int(min_val: int, max_val: int) -> int:
        return random.randint(min_val, max_val)

    @staticmethod
    def random_string(length: int) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def timestamp() -> int:
        return int(time.time())

    @staticmethod
    def uuid() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def md5(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @staticmethod
    def hmac_sha256(key: str, message: str) -> str:
        return hmac.new(
            key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    @staticmethod
    def base64_encode(text: str) -> str:
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")

    @staticmethod
    def base64_decode(text: str) -> str:
        return base64.b64decode(text.encode("utf-8")).decode("utf-8")

    @staticmethod
    def date_format(fmt: str = "%Y-%m-%d") -> str:
        return datetime.now().strftime(fmt)

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()


FUNCTIONS: dict[str, callable] = {
    "random_int": BuiltinFunctions.random_int,
    "random_string": BuiltinFunctions.random_string,
    "timestamp": BuiltinFunctions.timestamp,
    "uuid": BuiltinFunctions.uuid,
    "md5": BuiltinFunctions.md5,
    "hmac_sha256": BuiltinFunctions.hmac_sha256,
    "base64_encode": BuiltinFunctions.base64_encode,
    "base64_decode": BuiltinFunctions.base64_decode,
    "date_format": BuiltinFunctions.date_format,
    "now_iso": BuiltinFunctions.now_iso,
}
