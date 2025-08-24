import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class SpotMCPClient:
    def __init__(self, host="127.0.0.1", port=8080, api_key="test"):
        self.host = host
        self.port = port
        self.api_key = api_key
        self.endpoint = f"http://{host}:{port}/api"

    def _request(self, method, path, params=None, data=None, headers=None):
        import requests

        url = f"{self.endpoint}/{path}"
        request_headers = {"X-API-KEY": self.api_key}
        if headers:
            request_headers.update(headers)

        try:
            response = requests.request(
                method, url, params=params, json=data, headers=request_headers
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during request to {url}: {e}")
            return None

    def get_price(self, symbol):
        return self._request("GET", f"spot/price/{symbol}")

    def get_depth(self, symbol, limit=5):
        return self._request("GET", f"spot/depth/{symbol}", params={"limit": limit})

    def get_kline(self, symbol, interval="1m", limit=100):
        return self._request(
            "GET", f"spot/kline/{symbol}", params={"interval": interval, "limit": limit}
        )

    def get_symbols(self):
        return self._request("GET", "spot/symbols")

    def get_account(self):
        return self._request("GET", "spot/account")

    def create_order(self, symbol, order_type, price, quantity):
        data = {
            "symbol": symbol,
            "type": order_type,
            "price": price,
            "quantity": quantity,
        }
        return self._request("POST", "spot/order", data=data)

    def cancel_order(self, order_id):
        return self._request("DELETE", f"spot/order/{order_id}")