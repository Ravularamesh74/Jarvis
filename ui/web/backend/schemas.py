from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# -----------------------------------
# Base Response Schema
# -----------------------------------

class BaseResponse(BaseModel):
    success: bool = True
    error: Optional[str] = None


# -----------------------------------
# Chat Schemas (CORE)
# -----------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)


class ChatResponse(BaseResponse):
    response: str


# -----------------------------------
# Tool Schemas
# -----------------------------------

class ToolRequest(BaseModel):
    tool: str = Field(..., min_length=1)
    input: Dict[str, Any]


class ToolResponse(BaseResponse):
    tool: str
    result: Optional[Any] = None


# -----------------------------------
# Memory Schemas
# -----------------------------------

class MemoryItem(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseResponse):
    memory: List[MemoryItem] = []


# -----------------------------------
# System / Status Schemas
# -----------------------------------

class StatusResponse(BaseModel):
    status: str
    ai: str = "JARVIS"
    version: Optional[str] = "1.0.0"


# -----------------------------------
# Error Schema (Standardized)
# -----------------------------------

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


# -----------------------------------
# Streaming (Future Upgrade)
# -----------------------------------

class StreamChunk(BaseModel):
    token: str
    finished: bool = False