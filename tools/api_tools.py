import requests
import asyncio
import aiohttp
import time
from typing import Any, Dict, Optional
from tools.base_tool import BaseTool


class APITool(BaseTool):
    """
    Generic API Tool for handling HTTP requests.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retries: int = 3
    ):
        super().__init__(name=name, description=f"{method} {base_url}")

        self.base_url = base_url
        self.method = method.upper()
        self.headers = headers or {}
        self.timeout = timeout
        self.retries = retries

    # -----------------------------------
    # Sync Execution
    # -----------------------------------

    def _execute(self, input_data: Dict[str, Any], **kwargs) -> Any:
        url = self.base_url
        params = input_data.get("params", {})
        data = input_data.get("data", {})
        json_data = input_data.get("json", {})

        for attempt in range(self.retries):
            try:
                response = requests.request(
                    method=self.method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    data=data,
                    json=json_data,
                    timeout=self.timeout
                )

                return self._handle_response(response)

            except requests.exceptions.RequestException as e:
                if attempt == self.retries - 1:
                    raise Exception(f"API request failed: {str(e)}")
                time.sleep(2 ** attempt)  # exponential backoff

    # -----------------------------------
    # Async Execution
    # -----------------------------------

    async def _aexecute(self, input_data: Dict[str, Any], **kwargs) -> Any:
        url = self.base_url
        params = input_data.get("params", {})
        json_data = input_data.get("json", {})

        for attempt in range(self.retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=self.method,
                        url=url,
                        headers=self.headers,
                        params=params,
                        json=json_data,
                        timeout=self.timeout
                    ) as response:

                        return await self._handle_async_response(response)

            except Exception as e:
                if attempt == self.retries - 1:
                    raise Exception(f"Async API failed: {str(e)}")
                await asyncio.sleep(2 ** attempt)

    # -----------------------------------
    # Response Handling
    # -----------------------------------

    def _handle_response(self, response: requests.Response) -> Any:
        if response.status_code >= 400:
            raise Exception(
                f"API Error {response.status_code}: {response.text}"
            )

        try:
            return response.json()
        except Exception:
            return response.text

    async def _handle_async_response(self, response: aiohttp.ClientResponse) -> Any:
        if response.status >= 400:
            text = await response.text()
            raise Exception(f"API Error {response.status}: {text}")

        try:
            return await response.json()
        except Exception:
            return await response.text()


# -----------------------------------
# Specialized Tools (JARVIS USE CASES)
# -----------------------------------

class WeatherAPITool(APITool):
    """
    Example: Weather API Tool
    """

    def __init__(self, api_key: str):
        super().__init__(
            name="weather_api",
            base_url="https://api.openweathermap.org/data/2.5/weather",
            method="GET",
            headers={"Content-Type": "application/json"}
        )
        self.api_key = api_key

    def _execute(self, input_data: Dict[str, Any], **kwargs):
        city = input_data.get("city")

        if not city:
            raise ValueError("City is required")

        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        return super()._execute({"params": params})


class NewsAPITool(APITool):
    """
    Example: News API Tool
    """

    def __init__(self, api_key: str):
        super().__init__(
            name="news_api",
            base_url="https://newsapi.org/v2/top-headlines",
            method="GET"
        )
        self.api_key = api_key

    def _execute(self, input_data: Dict[str, Any], **kwargs):
        query = input_data.get("query", "technology")

        params = {
            "q": query,
            "apiKey": self.api_key,
            "pageSize": 5
        }

        return super()._execute({"params": params})


class GitHubAPITool(APITool):
    """
    Example: GitHub API Tool
    """

    def __init__(self, token: Optional[str] = None):
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"

        super().__init__(
            name="github_api",
            base_url="https://api.github.com",
            method="GET",
            headers=headers
        )

    def _execute(self, input_data: Dict[str, Any], **kwargs):
        endpoint = input_data.get("endpoint")

        if not endpoint:
            raise ValueError("Endpoint required")

        self.base_url = f"https://api.github.com{endpoint}"

        return super()._execute({})