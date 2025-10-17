"""
FastAPI entry point for KaiHelper (Lambda + API Gateway).
Places Swagger/OpenAPI under /api/* so API Gateway forwards them.
Adds explicit /api/openapi.json route and debug helpers.
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from mangum import Mangum

# Optional: load .env locally only (ignored in Lambda)
try:
    from dotenv import load_dotenv
    import pathlib
    env_path = pathlib.Path(__file__).parents[2] / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except Exception:  # pylint: disable=broad-except
    pass

# Keep docs/schema under /api/* (Gateway usually proxies /api/{proxy+})
API_BASE = "/api"

app = FastAPI(
    title="KaiHelper API",
    version="1.0",
    description="Grocery Budgeting App Backend",
    docs_url=f"{API_BASE}/docs",
    openapi_url=f"{API_BASE}/openapi.json",
    redoc_url=f"{API_BASE}/redoc",
    # DO NOT set root_path here; Mangum injects stage (/Prod) automatically.
)

# CORS (tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- KaiHelper wiring ----
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

# Routes (already under /api/*)
app.include_router(user_routes,     prefix="/api/users",      tags=["Users"])
app.include_router(category_router, prefix="/api/categories", tags=["Categories"])
app.include_router(grocery_router,  prefix="/api/groceries",  tags=["Groceries"])
app.include_router(budget_router,   prefix="/api/budgets",    tags=["Budgets"])
app.include_router(expense_router,  prefix="/api/expenses",   tags=["Expenses"])
app.include_router(receipt_router,  prefix="/api/receipts",   tags=["Receipts"])

@app.get("/")
def root():
    return {"message": "Welcome to KaiHelper API!"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

# --- Explicit openapi endpoint (hardens availability under /api/*) ---
@app.get("/api/openapi.json", include_in_schema=False)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    # Make "Try it out" use the correct stage-aware base path
    schema["servers"] = [{"url": "/"}]  # Mangum injects /Prod at runtime
    app.openapi_schema = schema
    return app.openapi_schema

# --- Debug helpers (remove later) ---
@app.get("/api/_debug/info", include_in_schema=False)
def debug_info(request: Request):
    return {
        "root_path_seen_by_app": request.scope.get("root_path"),
        "docs_url": app.docs_url,
        "openapi_url": app.openapi_url,
        "routes_count": len(app.routes),
    }

@app.get("/api/_debug/routes", include_in_schema=False)
def debug_routes():
    return sorted([getattr(r, "path", str(r)) for r in app.routes])

# Let Mangum infer stage root_path from the event (no manual base path)
handler = Mangum(app)
