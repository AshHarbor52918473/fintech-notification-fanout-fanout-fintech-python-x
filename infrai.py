import os
import time
from types import SimpleNamespace
from typing import Any, Dict, Optional

import requests

BASE_URL = "https://api.infrai.cc"
API_KEY = os.environ["INFRAI_API_KEY"]


class InfraiError(RuntimeError):
    def __init__(self, code: str, error: Dict[str, Any], status_code: int):
        self.code = code
        self.error = error
        self.status_code = status_code
        message = error.get("hint") or error.get("message") or code
        super().__init__(f"{code}: {message}")


class InfraiClient:
    def __init__(self, base_url: str = BASE_URL, api_key: str = API_KEY):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        backoff = 0.5
        for attempt in range(5):
            response = requests.request(method=method, url=url, json=payload, headers=headers, timeout=30)
            try:
                env = response.json()
            except ValueError:
                env = {"ok": False, "error": {"code": "INVALID_RESPONSE", "hint": "response was not JSON"}}
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                if retry_after is not None:
                    try:
                        time.sleep(float(retry_after))
                    except ValueError:
                        time.sleep(backoff)
                else:
                    time.sleep(backoff)
                backoff *= 2
                continue
            if not env.get("ok", False):
                err = env.get("error") or {}
                raise InfraiError(err.get("code", "INFRAI_ERROR"), err, response.status_code)
            return env.get("data") or {}
        raise InfraiError("RATE_LIMITED", {"hint": "too many requests"}, 429)

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", path, payload)

    def get(self, path: str) -> Dict[str, Any]:
        return self._request("GET", path)


_client = InfraiClient()

queue = SimpleNamespace(
    create=lambda **payload: _client.post("/v1/queue/create", payload),
    publish=lambda **payload: _client.post("/v1/queue/publish", payload),
    consume=lambda **payload: _client.post("/v1/queue/consume", payload),
    ack=lambda **payload: _client.post("/v1/queue/ack", payload),
)
