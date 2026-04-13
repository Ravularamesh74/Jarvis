import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
from typing import Any, Dict, List

from tools.base_tool import BaseTool


# -----------------------------------
# Security Config
# -----------------------------------

BLOCKED_SCHEMES = ["file", "ftp", "ssh"]
BLOCKED_HOSTS = ["localhost", "127.0.0.1"]


def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"]:
        return False

    if parsed.hostname in BLOCKED_HOSTS:
        return False

    return True


# -----------------------------------
# Web Tool
# -----------------------------------

class WebTool(BaseTool):
    """
    Web interaction tool (safe HTTP + scraping).
    """

    def __init__(self):
        super().__init__(
            name="web_tool",
            description="Fetches and parses web content"
        )

        self.headers = {
            "User-Agent": "JARVIS-AI/1.0"
        }

        self.timeout = 10
        self.retries = 3

    # -----------------------------------
    # Core Router
    # -----------------------------------

    def _execute(self, input_data: Dict[str, Any], **kwargs):
        action = input_data.get("action")

        if action == "fetch":
            return self.fetch(input_data.get("url"))

        elif action == "extract_text":
            return self.extract_text(input_data.get("url"))

        elif action == "extract_links":
            return self.extract_links(input_data.get("url"))

        else:
            raise ValueError(f"Unknown action: {action}")

    # -----------------------------------
    # HTTP Fetch
    # -----------------------------------

    def fetch(self, url: str) -> Dict[str, Any]:
        if not url or not is_safe_url(url):
            raise ValueError("Invalid or unsafe URL")

        for attempt in range(self.retries):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )

                return {
                    "status_code": response.status_code,
                    "content": response.text[:5000]  # limit size
                }

            except requests.exceptions.RequestException as e:
                if attempt == self.retries - 1:
                    raise Exception(f"Fetch failed: {str(e)}")
                time.sleep(2 ** attempt)

    # -----------------------------------
    # Extract Text
    # -----------------------------------

    def extract_text(self, url: str) -> str:
        data = self.fetch(url)
        soup = BeautifulSoup(data["content"], "html.parser")

        return soup.get_text(separator=" ", strip=True)[:3000]

    # -----------------------------------
    # Extract Links
    # -----------------------------------

    def extract_links(self, url: str) -> List[str]:
        data = self.fetch(url)
        soup = BeautifulSoup(data["content"], "html.parser")

        links = []

        for a in soup.find_all("a", href=True):
            full_url = urljoin(url, a["href"])

            if is_safe_url(full_url):
                links.append(full_url)

        return list(set(links))[:20]  # limit results