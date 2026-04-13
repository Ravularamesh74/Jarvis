import logging
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any

from ui.web.backend.schemas import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger("jarvis.routes")


# -----------------------------------
# Chat Endpoint (CORE)
# -----------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    """
    Main JARVIS interaction endpoint
    """
    orchestrator = request.app.state.orchestrator

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        logger.info(f"User input: {req.message}")

        result = orchestrator.handle(req.message)

        logger.info("Response generated successfully")

        return {"response": result}

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# System Status
# -----------------------------------

@router.get("/status")
async def status(request: Request) -> Dict[str, Any]:
    """
    Returns system-level info
    """
    return {
        "status": "running",
        "ai": "JARVIS",
    }


# -----------------------------------
# Memory Endpoint (Debug / Future UI)
# -----------------------------------

@router.get("/memory")
async def get_memory(request: Request):
    """
    Inspect short-term memory (for debugging / UI)
    """
    orchestrator = request.app.state.orchestrator
    memory = getattr(orchestrator, "memory", None)

    if not memory:
        return {"memory": []}

    try:
        data = memory.short_term.get_all()
        return {"memory": data}
    except Exception as e:
        logger.error(f"Memory error: {str(e)}")
        return {"memory": [], "error": str(e)}


# -----------------------------------
# Tool Execution Endpoint (Advanced)
# -----------------------------------

@router.post("/tool")
async def run_tool(payload: Dict[str, Any], request: Request):
    """
    Execute a tool directly (for debugging or UI integration)
    """
    orchestrator = request.app.state.orchestrator

    tool_name = payload.get("tool")
    tool_input = payload.get("input")

    if not tool_name:
        raise HTTPException(status_code=400, detail="Tool name required")

    try:
        # Assumes orchestrator has tool registry
        tool = orchestrator.get_tool(tool_name)

        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")

        result = tool.execute(tool_input)

        return {"tool": tool_name, "result": result}

    except Exception as e:
        logger.error(f"Tool error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# Health Check (Optional Duplicate)
# -----------------------------------

@router.get("/ping")
async def ping():
    return {"message": "pong"}