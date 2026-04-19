import requests


class HttpResponse:

    def __init__(self, status_code, headers, body, elapsed, encoding="utf-8"):
        self.status_code = status_code
        self.headers = dict(headers) if headers else {}
        self.body = body
        self._elapsed = elapsed
        self.encoding = encoding

    @property
    def elapsed(self):
        return self._elapsed

    @property
    def text(self):
        if isinstance(self.body, str):
            return self.body
        if isinstance(self.body, bytes):
            return self.body.decode(self.encoding, errors="replace")
        return str(self.body)

    def json(self):
        import json
        if isinstance(self.body, (dict, list)):
            return self.body
        return json.loads(self.text)


class HttpClient:

    def __init__(self, timeout=30, verify_ssl=True, proxies=None):
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.proxies = proxies
        self._session = requests.Session()

    def send(self, method, url, headers=None, params=None, body=None, json=None, files=None):
        resp = self._session.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            data=body,
            json=json,
            files=files,
            timeout=self.timeout,
            verify=self.verify_ssl,
            proxies=self.proxies,
        )
        elapsed_ms = resp.elapsed.total_seconds() * 1000
        return HttpResponse(
            status_code=resp.status_code,
            headers=resp.headers,
            body=resp.content,
            elapsed=elapsed_ms,
            encoding=resp.encoding or "utf-8",
        )
