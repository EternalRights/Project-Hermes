from unittest.mock import MagicMock, patch
from datetime import timedelta

import pytest

from hermes_core.executor.http_client import HttpClient, HttpResponse


class TestHttpResponse:

    def test_init_with_all_params(self):
        headers = {"Content-Type": "application/json"}
        resp = HttpResponse(status_code=200, headers=headers, body="ok", elapsed=50.0, encoding="utf-8")
        assert resp.status_code == 200
        assert resp.headers == {"Content-Type": "application/json"}
        assert resp.body == "ok"
        assert resp.elapsed == 50.0
        assert resp.encoding == "utf-8"

    def test_init_default_encoding(self):
        resp = HttpResponse(status_code=200, headers={}, body="ok", elapsed=10.0)
        assert resp.encoding == "utf-8"

    def test_init_none_headers(self):
        resp = HttpResponse(status_code=200, headers=None, body="ok", elapsed=10.0)
        assert resp.headers == {}

    def test_text_with_str_body(self):
        resp = HttpResponse(status_code=200, headers={}, body="hello", elapsed=10.0)
        assert resp.text == "hello"

    def test_text_with_bytes_body(self):
        resp = HttpResponse(status_code=200, headers={}, body=b"hello", elapsed=10.0)
        assert resp.text == "hello"

    def test_text_with_bytes_body_utf8(self):
        data = "héllo".encode("utf-8")
        resp = HttpResponse(status_code=200, headers={}, body=data, elapsed=10.0, encoding="utf-8")
        assert resp.text == "héllo"

    def test_text_with_bytes_body_latin1(self):
        data = "héllo".encode("latin-1")
        resp = HttpResponse(status_code=200, headers={}, body=data, elapsed=10.0, encoding="latin-1")
        assert "h" in resp.text

    def test_text_with_non_str_non_bytes_body(self):
        resp = HttpResponse(status_code=200, headers={}, body=123, elapsed=10.0)
        assert resp.text == "123"

    def test_text_with_bytes_body_replace_errors(self):
        bad_bytes = b"\xff\xfe"
        resp = HttpResponse(status_code=200, headers={}, body=bad_bytes, elapsed=10.0, encoding="ascii")
        result = resp.text
        assert isinstance(result, str)

    def test_json_with_dict_body(self):
        body = {"key": "value"}
        resp = HttpResponse(status_code=200, headers={}, body=body, elapsed=10.0)
        assert resp.json() == {"key": "value"}

    def test_json_with_list_body(self):
        body = [1, 2, 3]
        resp = HttpResponse(status_code=200, headers={}, body=body, elapsed=10.0)
        assert resp.json() == [1, 2, 3]

    def test_json_with_str_body(self):
        resp = HttpResponse(status_code=200, headers={}, body='{"key": "value"}', elapsed=10.0)
        assert resp.json() == {"key": "value"}

    def test_json_with_bytes_body(self):
        resp = HttpResponse(status_code=200, headers={}, body=b'{"key": "value"}', elapsed=10.0)
        assert resp.json() == {"key": "value"}

    def test_elapsed_property(self):
        resp = HttpResponse(status_code=200, headers={}, body="ok", elapsed=42.5)
        assert resp.elapsed == 42.5

    def test_headers_are_copied(self):
        original = {"X-Custom": "val"}
        resp = HttpResponse(status_code=200, headers=original, body="ok", elapsed=10.0)
        original["X-Custom"] = "changed"
        assert resp.headers["X-Custom"] == "val"


class TestHttpClient:

    def test_init_defaults(self):
        client = HttpClient()
        assert client.timeout == 30
        assert client.verify_ssl is True
        assert client.proxies is None

    def test_init_custom(self):
        client = HttpClient(timeout=60, verify_ssl=False, proxies={"http": "http://proxy:8080"})
        assert client.timeout == 60
        assert client.verify_ssl is False
        assert client.proxies == {"http": "http://proxy:8080"}

    @patch("hermes_core.executor.http_client.requests.Session")
    def test_send_returns_http_response(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "application/json"}
        mock_resp.content = b'{"result": true}'
        mock_resp.elapsed = timedelta(seconds=0.5)
        mock_resp.encoding = "utf-8"
        mock_session.request.return_value = mock_resp

        client = HttpClient(timeout=10, verify_ssl=True)
        result = client.send("GET", "http://example.com/api")

        assert isinstance(result, HttpResponse)
        assert result.status_code == 200
        assert result.headers == {"Content-Type": "application/json"}
        assert result.body == b'{"result": true}'
        assert result.elapsed == 500.0
        assert result.encoding == "utf-8"

    @patch("hermes_core.executor.http_client.requests.Session")
    def test_send_passes_method_uppercase(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {}
        mock_resp.content = b""
        mock_resp.elapsed = timedelta(seconds=0.1)
        mock_resp.encoding = "utf-8"
        mock_session.request.return_value = mock_resp

        client = HttpClient()
        client.send("post", "http://example.com")

        mock_session.request.assert_called_once()
        call_kwargs = mock_session.request.call_args
        assert call_kwargs[1]["method"] == "POST"

    @patch("hermes_core.executor.http_client.requests.Session")
    def test_send_passes_all_params(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.headers = {}
        mock_resp.content = b"created"
        mock_resp.elapsed = timedelta(seconds=0.2)
        mock_resp.encoding = "utf-8"
        mock_session.request.return_value = mock_resp

        client = HttpClient(timeout=15, verify_ssl=False, proxies={"http": "http://proxy"})
        client.send(
            "POST",
            "http://example.com/api",
            headers={"Authorization": "Bearer token"},
            params={"page": 1},
            body="data",
            json={"key": "val"},
            files={"file": ("f.txt", b"content")},
        )

        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["headers"] == {"Authorization": "Bearer token"}
        assert call_kwargs["params"] == {"page": 1}
        assert call_kwargs["data"] == "data"
        assert call_kwargs["json"] == {"key": "val"}
        assert call_kwargs["files"] == {"file": ("f.txt", b"content")}
        assert call_kwargs["timeout"] == 15
        assert call_kwargs["verify"] is False
        assert call_kwargs["proxies"] == {"http": "http://proxy"}

    @patch("hermes_core.executor.http_client.requests.Session")
    def test_send_fallback_encoding(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {}
        mock_resp.content = b"ok"
        mock_resp.elapsed = timedelta(seconds=0.1)
        mock_resp.encoding = None
        mock_session.request.return_value = mock_resp

        client = HttpClient()
        result = client.send("GET", "http://example.com")
        assert result.encoding == "utf-8"
