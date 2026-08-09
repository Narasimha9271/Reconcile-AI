import logging
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from reconcileai.config import get_settings
from reconcileai.api.routers.identity import router as identity_router
from reconcileai.api.routers.procurement import router as procurement_router
from reconcileai.api.routers.documents import router as documents_router
from reconcileai.api.routers.ai import router as ai_router
from reconcileai.api.routers.google_auth import router as google_auth_router
from reconcileai.api.routers.reconciliation import router as reconciliation_router
from reconcileai.modules.documents.service import LocalDocumentStore
from reconcileai.database import create_database

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Request-Id"] = f"req_{uuid4().hex}"
        return response

def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=logging.INFO)
    app = FastAPI(title="ReconcileAI API", version=settings.version)
    app.state.settings = settings
    app.state.document_store = LocalDocumentStore(settings.document_storage_path)
    app.state.database = create_database()
    app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, same_site="lax", https_only=settings.environment == "production")
    # Local browser dashboard. Production replaces this allow-list with deployed UI origins.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Development-User-Id", "X-Development-Organization-Id", "X-Development-Role"],
    )
    app.add_middleware(CorrelationIdMiddleware)
    app.include_router(identity_router)
    app.include_router(procurement_router)
    app.include_router(documents_router)
    app.include_router(reconciliation_router)
    app.include_router(ai_router)
    app.include_router(google_auth_router)
    @app.get("/healthz", tags=["health"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}
    @app.get("/readyz", tags=["health"])
    async def readyz() -> dict[str, str]:
        return {"status": "ready", "service": settings.service_name, "environment": settings.environment}
    return app

app = create_app()
