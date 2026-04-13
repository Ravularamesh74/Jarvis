import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Routes
from ui.web.backend.routes import router

# Core system
from core.orchestrator import Orchestrator
from memory.memory_manager import MemoryManager
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.vector_store import VectorStore


# -----------------------------------
# Logging Setup
# -----------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("jarvis.web")


# -----------------------------------
# System Builder
# -----------------------------------

def build_system():
    """
    Initialize JARVIS core components
    """
    short_term = ShortTermMemory(max_size=10)
    long_term = LongTermMemory(db=None)  # plug DB later
    vector_store = VectorStore()

    memory = MemoryManager(
        short_term=short_term,
        long_term=long_term,
        vector_store=vector_store,
    )

    from core.registry import CentralRegistry
    registry = CentralRegistry(brain=None, memory=memory, context=None)

    orchestrator = Orchestrator(memory=memory, registry=registry)

    return orchestrator


# -----------------------------------
# Lifespan Events
# -----------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting JARVIS Web API...")

    # Build system once
    app.state.orchestrator = build_system()

    yield

    logger.info("Shutting down JARVIS Web API...")


# -----------------------------------
# App Factory
# -----------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title="JARVIS Web API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS (allow frontend)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # change in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(router, prefix="/api")

    # -----------------------------------
    # Global Exception Handler
    # -----------------------------------

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {str(exc)}")

        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": str(exc)},
        )

    # -----------------------------------
    # Health Check
    # -----------------------------------

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "JARVIS API"
        }

    return app


# -----------------------------------
# App Instance (for uvicorn)
# -----------------------------------

app = create_app()