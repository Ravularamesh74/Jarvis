import os
import base64
import asyncio
from typing import Dict, List, Optional

import requests

from utils.logger import get_logger

logger = get_logger("GitHub")


class GitHubClient:
    """
    🐙 GitHub Integration

    Features:
    - Create repo
    - Push files
    - Create issues
    """

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        }

    # =============================
    # 📦 CREATE REPOSITORY
    # =============================
    def create_repo(self, name: str, private: bool = False) -> Dict:
        url = f"{self.base_url}/user/repos"

        data = {
            "name": name,
            "private": private
        }

        try:
            response = requests.post(url, json=data, headers=self.headers)
            return response.json()

        except Exception as e:
            logger.error(f"Create repo failed: {e}")
            return {"error": "Failed to create repo"}

    # =============================
    # 📁 CREATE / UPDATE FILE
    # =============================
    def push_file(
        self,
        repo: str,
        path: str,
        content: str,
        message: str = "update file",
        branch: str = "main"
    ) -> Dict:

        url = f"{self.base_url}/repos/{repo}/contents/{path}"

        encoded_content = base64.b64encode(content.encode()).decode()

        data = {
            "message": message,
            "content": encoded_content,
            "branch": branch
        }

        try:
            # Check if file exists
            existing = requests.get(url, headers=self.headers)

            if existing.status_code == 200:
                sha = existing.json()["sha"]
                data["sha"] = sha

            response = requests.put(url, json=data, headers=self.headers)
            return response.json()

        except Exception as e:
            logger.error(f"Push file failed: {e}")
            return {"error": "Failed to push file"}

    # =============================
    # 🐛 CREATE ISSUE
    # =============================
    def create_issue(
        self,
        repo: str,
        title: str,
        body: str = ""
    ) -> Dict:

        url = f"{self.base_url}/repos/{repo}/issues"

        data = {
            "title": title,
            "body": body
        }

        try:
            response = requests.post(url, json=data, headers=self.headers)
            return response.json()

        except Exception as e:
            logger.error(f"Issue creation failed: {e}")
            return {"error": "Failed to create issue"}

    # =============================
    # 📋 LIST REPOS
    # =============================
    def list_repos(self) -> List[Dict]:
        url = f"{self.base_url}/user/repos"

        try:
            response = requests.get(url, headers=self.headers)
            return response.json()

        except Exception as e:
            logger.error(f"List repos failed: {e}")
            return []

    # =============================
    # ⚡ ASYNC WRAPPERS
    # =============================
    async def create_repo_async(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.create_repo(*args, **kwargs)
        )

    async def push_file_async(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.push_file(*args, **kwargs)
        )

    async def create_issue_async(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.create_issue(*args, **kwargs)
        )