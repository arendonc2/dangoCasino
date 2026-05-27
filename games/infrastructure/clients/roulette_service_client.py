import requests
from django.conf import settings


class RouletteServiceClient:
    def __init__(self, base_url=None, timeout=3):
        self.base_url = (base_url or settings.ROULETTE_SERVICE_URL).rstrip("/")
        self.timeout = timeout

    def play_roulette(self, payload):
        url = f"{self.base_url}/api/v2/roulette/play"

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
        except requests.RequestException as exc:
            return {
                "ok": False,
                "error": f"connection_error: {exc}",
            }

        if response.status_code != 200:
            return {
                "ok": False,
                "error": f"upstream_status_{response.status_code}",
                "upstream_body": response.text,
            }

        try:
            data = response.json()
        except ValueError:
            return {
                "ok": False,
                "error": "invalid_json_response",
            }

        if data.get("status") != "success":
            return {
                "ok": False,
                "error": data.get("message", "upstream_error"),
                "upstream_data": data,
            }

        return {
            "ok": True,
            "data": data,
        }
