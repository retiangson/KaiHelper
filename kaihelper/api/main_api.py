"""
FastAPI entry point for KaiHelper (Lambda + API Gateway)
Stage-safe docs: root_path carries /Prod; docs/openapi live under /api/*
No double-prefixing, no moving URLs.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# 1) Stage prefix ONLY in root_path (e.g., set STAGE_BASE=/Prod in Lambda)
STAGE_BASE = os.getenv("STAGE_BASE", "").rstrip("/")  # "" locally, "/Prod" in prod

app = FastAPI(
    title="KaiHelper API",
    version="1.0",
    description="Grocery Budgeting App Backend",
    # 2) DO NOT include stage here; keep them fixed under /api/*
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
    # 3) Put the stage ONLY here
    root_path=STAGE_BASE or "",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ----- Wire services & routes -----
from kaihelper.business.services.service_installer import ServiceInstaller  # noqa: E402
from kaihelper.domain.domain_installer import DomainInstaller  # noqa: E402
from kaihelper.domain.core.database import Base, engine  # noqa: E402

# Ensure models are imported so create_all sees them
import kaihelper.domain.models.user       # noqa: F401,E402
import kaihelper.domain.models.category   # noqa: F401,E402
import kaihelper.domain.models.grocery    # noqa: F401,E402
import kaihelper.domain.models.budget     # noqa: F401,E402
import kaihelper.domain.models.expense    # noqa: F401,E402

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
        print(f"[KaiHelper API] root_path={app.root_path!r}")
        print(f"[KaiHelper API] docs={app.docs_url} openapi={app.openapi_url}")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[KaiHelper API] Startup error: {exc}")

# API routes: under /api/* (NO stage here)
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

# Lambda handler
handler = Mangum(app)
