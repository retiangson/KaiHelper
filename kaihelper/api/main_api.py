"""
FastAPI entry point for KaiHelper (Lambda + API Gateway).
Docs are served at root (/docs,/openapi.json) so API Gateway stage (/Prod) just works.
API routes stay under /api/*.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from mangum import Mangum

# ---- App: docs at root (no stage prefix here) ----
app = FastAPI(
    title="KaiHelper API",
    version="1.0",
    description="Grocery Budgeting App Backend",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc",
    # DO NOT set root_path; Mangum supplies /Prod at runtime
)

# CORS (tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Wire services & routers ----
from kaihelper.business.services.service_installer import ServiceInstaller  # noqa: E402
from kaihelper.domain.domain_installer import DomainInstaller  # noqa: E402
from kaihelper.domain.core.database import Base, engine  # noqa: E402

from kaihelper.api.routes.user_api import router as user_routes  # noqa: E402
from kaihelper.api.routes.category_api import router as category_router  # noqa: E402
from kaihelper.api.routes.grocery_api import router as grocery_router  # noqa: E402
from kaihelper.api.routes.budget_api import router as budget_router  # noqa: E402
from kaihelper.api.routes.expense_api import router as expense_router  # noqa: E402
from kaihelper.api.routes.receipt_api import router as receipt_router  # noqa: E402

domain = DomainInstaller()
services = ServiceInstaller(domain)
app.state.domain = domain
app.state.services = services

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("[KaiHelper API] Database initialized.")
    except Exception as e:  # pylint: disable=broad-except
        print(f"[KaiHelper API] Startup error: {e}")

# ---- API routes remain under /api/* ----
app.include_router(user_routes,     prefix="/api/users",      tags=["Users"])
app.include_router(category_router, prefix="/api/categories", tags=["Categories"])
app.include_router(grocery_router,  prefix="/api/groceries",  tags=["Groceries"])
app.include_router(budget_router,   prefix="/api/budgets",    tags=["Budgets"])
app.include_router(expense_router,  prefix="/api/expenses",   tags=["Expenses"])
app.include_router(receipt_router,  prefix="/api/receipts",   tags=["Receipts"])

# ---- Root / health ----
@app.get("/")
def root():
    return {"message": "Welcome to KaiHelper API!"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

# ---- Explicit OpenAPI endpoint (same as openapi_url) ----
@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    # Make "Try it out" use the stage-aware base (API Gateway injects /Prod)
    schema["servers"] = [{"url": "/"}]
    app.openapi_schema = schema
    return app.openapi_schema

# ---- Optional debug endpoints (remove later) ----
@app.get("/_debug/info", include_in_schema=False)
def debug_info(request: Request):
    return {
        "root_path_seen_by_app": request.scope.get("root_path"),
        "docs_url": app.docs_url,
        "openapi_url": app.openapi_url,
    }

handler = Mangum(app)
