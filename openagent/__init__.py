"""
OpenAgent - Agente de IA Local 100% Open Source
"""

__version__ = "1.0.0"
__author__ = "OpenAgent Team"
__email__ = "contact@openagent.ai"

from .core import OpenAgent
from .model_manager import ModelManager
from .llm_server import LLMServer
from .tools import ToolRegistry

__all__ = [
    "OpenAgent",
    "ModelManager", 
    "LLMServer",
    "ToolRegistry"
]