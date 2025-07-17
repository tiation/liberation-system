import requests
import os

class APIClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data=None, json=True):
        url = f"{self.base_url}/{endpoint}"
        headers = self.headers
        headers['Content-Type'] = 'application/json' if json else 'application/x-www-form-urlencoded'
        response = requests.post(url, headers=headers, json=data if json else None, data=data if not json else None)
        response.raise_for_status()
        return response.json()

# Example usage:
# api_client = APIClient(base_url="https://api.example.com", api_key=os.getenv("API_KEY"))
# response = api_client.get("some/endpoint")
