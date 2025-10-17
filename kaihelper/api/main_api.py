"""
FastAPI entry point for KaiHelper (Lambda + API Gateway).
Publishes docs & schema with the stage prefix (e.g., /Prod) so Swagger hits the right URL.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from mangum import Mangum

# ---- Stage prefix from Lambda env (set to "/Prod" in your Lambda) ----
BASE_PATH = os.getenv("STAGE_BASE", "").rstrip("/")     # "" locally, "/Prod" in prod
API_BASE  = f"{BASE_PATH}/api" if BASE_PATH else "/api" # stage-aware API prefix

app = FastAPI(
    title="KaiHelper API",
    version="1.0",
    description="Grocery Budgeting App Backend",
    # IMPORTANT: publish docs/schema with the stage prefix
    docs_url=f"{API_BASE}/docs",
    openapi_url=f"{API_BASE}/openapi.json",
    redoc_url=f"{API_BASE}/redoc",
    # DO NOT set root_path; that’s what caused double /Prod earlier
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

# Ensure models are imported before create_all (optional if you use migrations)
import kaihelper.domain.models.user       # noqa: F401,E402
import kaihelper.domain.models.category   # noqa: F401,E402
import kaihelper.domain.models.grocery    # noqa: F401,E402
import kaihelper.domain.models.budget     # noqa: F401,E402
import kaihelper.domain.models.expense    # noqa: F401,E402

domain = DomainInstaller()
services = ServiceInstaller(domain)
app.state.domain = domain
app.state.services = services

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        print(f"[KaiHelper API] BASE_PATH={BASE_PATH!r} API_BASE={API_BASE!r}")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[KaiHelper API] Startup error: {exc}")

# Routes (already under /api/* — these DON’T include BASE_PATH; API GW adds it)
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

# Make the OpenAPI JSON robust (same path as openapi_url)
@app.get(f"{API_BASE}/openapi.json", include_in_schema=False)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    # Make "Try it out" stage-aware
    schema["servers"] = [{"url": BASE_PATH or "/"}]
    app.openapi_schema = schema
    return app.openapi_schema

handler = Mangum(app)
