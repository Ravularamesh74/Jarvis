import asyncio
from typing import Optional, Dict, List

import requests
from bs4 import BeautifulSoup

from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger("ResearchAgent")


class ResearchAgent(BaseAgent):
    """
    🔍 Research Agent

    Capabilities:
    - Web search
    - Content scraping
    - Summarization via LLM
    """

    def __init__(self, brain, memory=None, context=None):
        super().__init__("ResearchAgent", memory, context)
        self.brain = brain

    # =============================
    # 🧠 MAIN LOGIC
    # =============================
    async def run(self, task: str, metadata: Optional[Dict] = None) -> str:
        logger.info(f"[ResearchAgent] Task: {task}")

        # Step 1: Search
        links = await self.search_web(task)

        if not links:
            return "No results found."

        # Step 2: Scrape top results
        contents = await self.scrape_links(links[:3])

        # Step 3: Summarize
        summary = await self.summarize(task, contents)

        return summary

    # =============================
    # 🌐 SEARCH (Simple Google Scrape)
    # =============================
    async def search_web(self, query: str) -> List[str]:
        try:
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": "Mozilla/5.0"}

            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            links = []
            for a in soup.select("a"):
                href = a.get("href")
                if href and "http" in href:
                    links.append(href)

            logger.info(f"Found {len(links)} links")
            return links[:5]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    # =============================
    # 📄 SCRAPE CONTENT
    # =============================
    async def scrape_links(self, links: List[str]) -> List[str]:
        contents = []

        for link in links:
            try:
                html = await self.fetch_page(link)
                text = self.extract_text(html)
                contents.append(text[:2000])  # limit size

            except Exception as e:
                logger.warning(f"Failed to scrape {link}: {e}")

        return contents

    async def fetch_page(self, url: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: requests.get(url).text)

    def extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for script in soup(["script", "style"]):
            script.decompose()

        return soup.get_text(separator=" ", strip=True)

    # =============================
    # 🧠 SUMMARIZATION
    # =============================
    async def summarize(self, query: str, contents: List[str]) -> str:
        combined = "\n\n".join(contents)

        prompt = f"""
You are a research assistant.

Query:
{query}

Content:
{combined}

Task:
- Summarize key insights
- Keep it concise but informative
"""

        try:
            return await self.brain.ask_async(prompt)

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Failed to summarize results."