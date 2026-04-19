import time
import logging

logger = logging.getLogger(__name__)


class RetryPolicy:

    def __init__(self, max_retries=3, retry_interval=1.0, retry_on_status=None):
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.retry_on_status = retry_on_status if retry_on_status is not None else [500, 502, 503, 504]


class RetryAttempt:

    def __init__(self, attempt_number, response=None, error=None):
        self.attempt_number = attempt_number
        self.response = response
        self.error = error


class RetryableHttpClient:

    def __init__(self, http_client, retry_policy):
        self.http_client = http_client
        self.retry_policy = retry_policy
        self.attempts = []

    def send_with_retry(self, method, url, **kwargs):
        self.attempts = []
        last_response = None
        for attempt_num in range(1, self.retry_policy.max_retries + 1):
            try:
                response = self.http_client.send(method, url, **kwargs)
                self.attempts.append(RetryAttempt(attempt_num, response=response))
                if response.status_code not in self.retry_policy.retry_on_status:
                    return response
                last_response = response
                logger.info(
                    "Attempt %d: status %d, will retry",
                    attempt_num, response.status_code,
                )
            except Exception as e:
                self.attempts.append(RetryAttempt(attempt_num, error=e))
                logger.info("Attempt %d: error %s, will retry", attempt_num, str(e))
            if attempt_num < self.retry_policy.max_retries:
                time.sleep(self.retry_policy.retry_interval)
        if last_response is not None:
            return last_response
        if self.attempts and self.attempts[-1].error:
            raise self.attempts[-1].error
        return last_response
