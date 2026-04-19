from unittest.mock import MagicMock, patch

import pytest

from hermes_core.executor.retry import RetryPolicy, RetryAttempt, RetryableHttpClient
from hermes_core.executor.http_client import HttpResponse


class TestRetryPolicy:

    def test_default_values(self):
        policy = RetryPolicy()
        assert policy.max_retries == 3
        assert policy.retry_interval == 1.0
        assert policy.retry_on_status == [500, 502, 503, 504]

    def test_custom_values(self):
        policy = RetryPolicy(max_retries=5, retry_interval=2.0, retry_on_status=[503])
        assert policy.max_retries == 5
        assert policy.retry_interval == 2.0
        assert policy.retry_on_status == [503]

    def test_retry_on_status_none_defaults(self):
        policy = RetryPolicy(retry_on_status=None)
        assert policy.retry_on_status == [500, 502, 503, 504]


class TestRetryAttempt:

    def test_init_with_response(self):
        resp = HttpResponse(status_code=200, headers={}, body=b"ok", elapsed=10.0)
        attempt = RetryAttempt(attempt_number=1, response=resp)
        assert attempt.attempt_number == 1
        assert attempt.response is resp
        assert attempt.error is None

    def test_init_with_error(self):
        err = ConnectionError("timeout")
        attempt = RetryAttempt(attempt_number=2, error=err)
        assert attempt.attempt_number == 2
        assert attempt.response is None
        assert attempt.error is err

    def test_init_defaults(self):
        attempt = RetryAttempt(attempt_number=1)
        assert attempt.attempt_number == 1
        assert attempt.response is None
        assert attempt.error is None


class TestRetryableHttpClient:

    def _make_response(self, status_code):
        return HttpResponse(status_code=status_code, headers={}, body=b"ok", elapsed=10.0)

    @patch("hermes_core.executor.retry.time.sleep")
    def test_success_on_first_attempt(self, mock_sleep):
        mock_client = MagicMock()
        mock_client.send.return_value = self._make_response(200)
        policy = RetryPolicy(max_retries=3, retry_interval=0.1)
        retry_client = RetryableHttpClient(mock_client, policy)

        result = retry_client.send_with_retry("GET", "http://example.com")

        assert result.status_code == 200
        assert len(retry_client.attempts) == 1
        assert retry_client.attempts[0].attempt_number == 1
        assert retry_client.attempts[0].response.status_code == 200
        mock_sleep.assert_not_called()

    @patch("hermes_core.executor.retry.time.sleep")
    def test_retry_on_retryable_status_then_success(self, mock_sleep):
        mock_client = MagicMock()
        mock_client.send.side_effect = [
            self._make_response(500),
            self._make_response(200),
        ]
        policy = RetryPolicy(max_retries=3, retry_interval=0.5)
        retry_client = RetryableHttpClient(mock_client, policy)

        result = retry_client.send_with_retry("GET", "http://example.com")

        assert result.status_code == 200
        assert len(retry_client.attempts) == 2
        assert retry_client.attempts[0].response.status_code == 500
        assert retry_client.attempts[1].response.status_code == 200
        mock_sleep.assert_called_once_with(0.5)

    @patch("hermes_core.executor.retry.time.sleep")
    def test_all_retries_exhausted(self, mock_sleep):
        mock_client = MagicMock()
        mock_client.send.return_value = self._make_response(503)
        policy = RetryPolicy(max_retries=3, retry_interval=0.1)
        retry_client = RetryableHttpClient(mock_client, policy)

        result = retry_client.send_with_retry("GET", "http://example.com")

        assert result.status_code == 503
        assert len(retry_client.attempts) == 3
        assert mock_sleep.call_count == 2

    @patch("hermes_core.executor.retry.time.sleep")
    def test_exception_then_success(self, mock_sleep):
        mock_client = MagicMock()
        mock_client.send.side_effect = [
            ConnectionError("timeout"),
            self._make_response(200),
        ]
        policy = RetryPolicy(max_retries=3, retry_interval=0.1)
        retry_client = RetryableHttpClient(mock_client, policy)

        result = retry_client.send_with_retry("GET", "http://example.com")

        assert result.status_code == 200
        assert len(retry_client.attempts) == 2
        assert retry_client.attempts[0].error is not None
        assert retry_client.attempts[1].response.status_code == 200

    @patch("hermes_core.executor.retry.time.sleep")
    def test_exception_on_all_retries(self, mock_sleep):
        mock_client = MagicMock()
        mock_client.send.side_effect = ConnectionError("timeout")
        policy = RetryPolicy(max_retries=3, retry_interval=0.1)
        retry_client = RetryableHttpClient(mock_client, policy)

        with pytest.raises(ConnectionError, match="timeout"):
            retry_client.send_with_retry("GET", "http://example.com")

        assert len(retry_client.attempts) == 3
        for attempt in retry_client.attempts:
            assert attempt.error is not None
            assert attempt.response is None

    @patch("hermes_core.executor.retry.time.sleep")
    def test_non_retryable_status_returns_immediately(self, mock_sleep):
        mock_client = MagicMock()
        mock_client.send.return_value = self._make_response(404)
        policy = RetryPolicy(max_retries=3, retry_interval=0.1)
        retry_client = RetryableHttpClient(mock_client, policy)

        result = retry_client.send_with_retry("GET", "http://example.com")

        assert result.status_code == 404
        assert len(retry_client.attempts) == 1
        mock_sleep.assert_not_called()

    @patch("hermes_core.executor.retry.time.sleep")
    def test_custom_retry_on_status(self, mock_sleep):
        mock_client = MagicMock()
        mock_client.send.side_effect = [
            self._make_response(429),
            self._make_response(200),
        ]
        policy = RetryPolicy(max_retries=3, retry_interval=0.1, retry_on_status=[429])
        retry_client = RetryableHttpClient(mock_client, policy)

        result = retry_client.send_with_retry("GET", "http://example.com")

        assert result.status_code == 200
        assert len(retry_client.attempts) == 2

    @patch("hermes_core.executor.retry.time.sleep")
    def test_attempts_reset_on_new_call(self, mock_sleep):
        mock_client = MagicMock()
        mock_client.send.return_value = self._make_response(200)
        policy = RetryPolicy(max_retries=3, retry_interval=0.1)
        retry_client = RetryableHttpClient(mock_client, policy)

        retry_client.send_with_retry("GET", "http://example.com")
        assert len(retry_client.attempts) == 1

        retry_client.send_with_retry("GET", "http://example.com")
        assert len(retry_client.attempts) == 1

    @patch("hermes_core.executor.retry.time.sleep")
    def test_kwargs_passed_to_send(self, mock_sleep):
        mock_client = MagicMock()
        mock_client.send.return_value = self._make_response(200)
        policy = RetryPolicy(max_retries=3, retry_interval=0.1)
        retry_client = RetryableHttpClient(mock_client, policy)

        retry_client.send_with_retry(
            "POST", "http://example.com",
            headers={"X-Auth": "token"},
            body="data",
        )

        mock_client.send.assert_called_with(
            "POST", "http://example.com",
            headers={"X-Auth": "token"},
            body="data",
        )

    @patch("hermes_core.executor.retry.time.sleep")
    def test_mixed_errors_and_retryable_statuses(self, mock_sleep):
        mock_client = MagicMock()
        mock_client.send.side_effect = [
            ConnectionError("conn error"),
            self._make_response(500),
            self._make_response(200),
        ]
        policy = RetryPolicy(max_retries=3, retry_interval=0.1)
        retry_client = RetryableHttpClient(mock_client, policy)

        result = retry_client.send_with_retry("GET", "http://example.com")

        assert result.status_code == 200
        assert len(retry_client.attempts) == 3
        assert retry_client.attempts[0].error is not None
        assert retry_client.attempts[1].response.status_code == 500
        assert retry_client.attempts[2].response.status_code == 200
