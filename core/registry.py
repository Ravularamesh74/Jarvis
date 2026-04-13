import os
from typing import Optional

from utils.logger import get_logger

# 🛠️ Tools
from tools.web_tools import WebTool
from tools.system_tools import SystemTool
from tools.file_tools import FileTool
from tools.code_tools import CodeExecutor, ShellTool, PythonFileRunner
from tools.api_tools import WeatherAPITool, NewsAPITool, GitHubAPITool

# 👁️ Vision
from vision.camera import VisionSystem
from vision.object_detection import ObjectDetector
from vision.face_recognition import FaceRecognitionSystem

# 🔄 Integrations
from integrations.whatsapp import get_whatsapp_client
from integrations.github import GitHubClient
from integrations.email import CalendarManager
from integrations.calendar import EmailClient

logger = get_logger("Registry")

class CentralRegistry:
    """
    🗄️ Central Registry
    Connects all detached data/modules: Tools, Vision, Integrations.
    """
    def __init__(self, brain=None, memory=None, context=None):
        self.brain = brain
        self.memory = memory
        self.context = context

        logger.info("Initializing Central Registry (Connecting all components)...")

        # 1. Base Tools initialization
        self.tools = {
            "web": WebTool(),
            "system": SystemTool(),
            "file": FileTool(),
            "code_exec": CodeExecutor(),
            "shell": ShellTool(),
            "python_runner": PythonFileRunner(),
        }

        # API Tools
        weather_key = os.getenv("WEATHER_API_KEY", "dummy")
        news_key = os.getenv("NEWS_API_KEY", "dummy")
        github_token = os.getenv("GITHUB_TOKEN", None)

        self.tools["weather"] = WeatherAPITool(api_key=weather_key)
        self.tools["news"] = NewsAPITool(api_key=news_key)
        self.tools["github_api"] = GitHubAPITool(token=github_token)

        # 2. Vision Systems
        self.vision = {
            "camera": VisionSystem(),
            "object_detector": ObjectDetector(),
            "face_recognition": FaceRecognitionSystem(),
        }

        # 3. Integrations
        whatsapp = get_whatsapp_client(brain=self.brain, memory=self.memory)
        
        self.integrations = {
            "whatsapp": whatsapp,
            "github": GitHubClient() if hasattr(GitHubClient, "__init__") else None,
            "calendar": CalendarManager(),
            "email": EmailClient(),
        }

    def execute_tool(self, tool_name: str, input_data: dict, **kwargs):
        """Execute a loaded tool by name safely."""
        tool = self.tools.get(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found."}
        
        try:
            return tool.execute(input_data, **kwargs)
        except Exception as e:
            return {"error": str(e)}

    def get_all_tools(self):
        return list(self.tools.keys())

    def get_vision_modules(self):
        return list(self.vision.keys())

    def get_integrations(self):
        return list(self.integrations.keys())
