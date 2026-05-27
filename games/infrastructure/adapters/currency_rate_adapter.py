import logging
import requests
from django.conf import settings

from ...application.ports.currency_rate_port import CurrencyRatePort

logger = logging.getLogger(__name__)


class CurrencyRateAdapter(CurrencyRatePort):
    def get_cop_to_usd_rate(self) -> float:
        if settings.EXTERNAL_API_MOCK:
            return 0.00025

        base_url = settings.EXTERNAL_API_BASE_URL.rstrip("/")
        if not base_url:
            logger.warning("EXTERNAL_API_BASE_URL is empty, using fallback rate")
            return 0.00025

        url = f"{base_url}/latest"
        headers = {}
        if settings.EXTERNAL_API_KEY:
            headers["Authorization"] = f"Bearer {settings.EXTERNAL_API_KEY}"

        try:
            response = requests.get(
                url,
                params={"base": "COP", "symbols": "USD"},
                headers=headers,
                timeout=3,
            )
            response.raise_for_status()
            data = response.json()
            rate = float(data.get("rates", {}).get("USD"))
            return rate
        except Exception as exc:
            logger.warning("Currency API unavailable, fallback rate used: %s", exc)
            return 0.00025
