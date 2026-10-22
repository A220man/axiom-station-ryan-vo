from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, contradictions
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Axiom Station API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
    app.include_router(contradictions.router, prefix="/api/v1/contradictions", tags=["contradictions"])

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "1.0.0"}

    return app


app = create_app()