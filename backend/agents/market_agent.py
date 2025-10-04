import requests
from ..config.settings import settings

class MarketAgent:
    def fetch(self, symbol=None, company_name=None):
        """
        Uses symbol if available; falls back to resolving symbol from company_name.
        Returns market data dictionary.
        """
        if symbol:
            return self._fetch_by_symbol(symbol)
        elif company_name:
            resolved_symbol = self._resolve_symbol_from_name(company_name)
            if resolved_symbol:
                return self._fetch_by_symbol(resolved_symbol)
        return {}

    def _fetch_by_symbol(self, symbol):
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={settings.ALPHA_VANTAGE_API_KEY}"
        resp = requests.get(url)
        return resp.json() if resp.ok else {}

    def _resolve_symbol_from_name(self, company_name):
        search_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company_name}&apikey={settings.ALPHA_VANTAGE_API_KEY}"
        resp = requests.get(search_url).json()
        matches = resp.get("bestMatches", [])
        return matches[0].get("1. symbol") if matches else None
