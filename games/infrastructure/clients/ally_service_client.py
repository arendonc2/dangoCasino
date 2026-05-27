import requests
from django.conf import settings


class AllyServiceClient:
    def __init__(self, base_url=None, timeout=3):
        self.base_url = (base_url or settings.ALLY_SERVICE_BASE_URL).rstrip("/")
        self.timeout = timeout

    def get_status(self):
        if settings.ALLY_SERVICE_MOCK:
            return {
                "source": "ally-service-mock",
                "status": "available",
                "team": "equipo-aliado",
                "message": "Datos aliados simulados disponibles",
                "data": {
                    "recommendation": "Play responsibly",
                    "external_score": 87,
                },
            }

        if not self.base_url:
            return self._fallback_response()

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/status",
                timeout=self.timeout,
            )
        except requests.Timeout:
            return self._fallback_response()
        except requests.RequestException:
            return self._fallback_response()

        if response.status_code != 200:
            return self._fallback_response()

        try:
            data = response.json()
        except ValueError:
            return self._fallback_response()

        return {
            "source": "ally-service",
            "status": "available",
            "team": data.get("team", "equipo-aliado"),
            "message": data.get("message", "Servicio aliado disponible"),
            "data": data.get("data"),
        }

    @staticmethod
    def _fallback_response():
        return {
            "source": "ally-service-fallback",
            "status": "unavailable",
            "message": "El servicio aliado no esta disponible temporalmente.",
            "data": None,
        }
