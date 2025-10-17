"""
FastAPI entry point for KaiHelper (Lambda + API Gateway).
We mount the actual API (with its own docs/schema) under /api to avoid
stage prefix confusion. The root app only serves / and /health.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from mangum import Mangum

# -------- Root app (no docs here) --------
app = FastAPI(
    title="KaiHelper Root",
    version="1.0",
    docs_url=None,
    openapi_url=None,
    redoc_url=None,
)

# CORS (tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Create the real API as a sub-app mounted at /api --------
api = FastAPI(
    title="KaiHelper API",
    version="1.0",
    description="Grocery Budgeting App Backend",
    docs_url="/docs",             # resolves to /api/docs
    openapi_url="/openapi.json",  # resolves to /api/openapi.json
    redoc_url="/redoc",           # resolves to /api/redoc
)

# ---- Wire services & routers into the sub-app ----
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

@api.on_event("startup")
def api_startup():
    try:
        Base.metadata.create_all(bind=engine)
        # attach services only to sub-app that serves /api/*
        api.state.domain = domain
        api.state.services = services
        print("[KaiHelper API] Database initialized.")
    except Exception as e:  # pylint: disable=broad-except
        print(f"[KaiHelper API] Startup error: {e}")

# Sub-app routes (under /api/*)
api.include_router(user_routes,     prefix="/users",      tags=["Users"])
api.include_router(category_router, prefix="/categories", tags=["Categories"])
api.include_router(grocery_router,  prefix="/groceries",  tags=["Groceries"])
api.include_router(budget_router,   prefix="/budgets",    tags=["Budgets"])
api.include_router(expense_router,  prefix="/expenses",   tags=["Expenses"])
api.include_router(receipt_router,  prefix="/receipts",   tags=["Receipts"])

# Optional: make "Try it out" use the stage-aware base automatically
@api.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    if api.openapi_schema:
        return api.openapi_schema
    schema = get_openapi(title=api.title, version=api.version, routes=api.routes)
    schema["servers"] = [{"url": "/"}]  # API Gateway injects /Prod at runtime
    api.openapi_schema = schema
    return api.openapi_schema

# Mount the API under /api on the root app
app.mount("/api", api)

# Root-only endpoints (not under /api/*)
@app.get("/")
def root():
    return {"message": "Welcome to KaiHelper API!"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

# Mangum handler on the root app
handler = Mangum(app)
