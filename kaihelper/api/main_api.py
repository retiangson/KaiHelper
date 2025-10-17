"""
FastAPI entry point for KaiHelper (Lambda-ready, stage-aware).
"""

import os
from fastapi import FastAPI
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware

# -----------------------------------------------------------
# .env loading (local/dev only). In Lambda, use env vars.
# -----------------------------------------------------------
try:
    from dotenv import load_dotenv  # optional dependency
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ENV_PATH = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH)
except Exception:
    # If python-dotenv isn't installed or any issue occurs, just continue.
    pass

# -----------------------------------------------------------
# Stage-aware root path for API Gateway (e.g., "/Prod" or "/v1")
# Make sure template.yaml sets FASTAPI_ROOT_PATH to your stage.
# -----------------------------------------------------------
ROOT_PATH = os.getenv("FASTAPI_ROOT_PATH", "").rstrip("/")  # e.g. "/Prod" or ""

# Optional: if you want docs under the stage explicitly
OPENAPI_URL = f"{ROOT_PATH}/openapi.json" if ROOT_PATH else "/openapi.json"
DOCS_URL = f"{ROOT_PATH}/docs" if ROOT_PATH else "/docs"
REDOC_URL = f"{ROOT_PATH}/redoc" if ROOT_PATH else "/redoc"

app = FastAPI(
    title="KaiHelper API",
    version="1.0",
    description="Grocery Budgeting App Backend",
    root_path=ROOT_PATH,
    openapi_url=OPENAPI_URL,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
)

# -----------------------------------------------------------
# CORS (adjust allow_origins for tighter security in prod)
# -----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # TODO: replace with your web/app origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# KaiHelper imports (after env is loaded)
# -----------------------------------------------------------
from kaihelper.business.services.service_installer import ServiceInstaller
from kaihelper.domain.domain_installer import DomainInstaller
from kaihelper.domain.core.database import Base, engine

# Routers
from kaihelper.api.routes.user_api import router as user_routes
from kaihelper.api.routes.category_api import router as category_router
from kaihelper.api.routes.grocery_api import router as grocery_router
from kaihelper.api.routes.budget_api import router as budget_router
from kaihelper.api.routes.expense_api import router as expense_router
from kaihelper.api.routes.receipt_api import router as receipt_router

# -----------------------------------------------------------
# Dependency Injection setup
# -----------------------------------------------------------
domain = DomainInstaller()
services = ServiceInstaller(domain)
app.state.domain = domain
app.state.services = services

# -----------------------------------------------------------
# Startup (consider migrations instead of create_all in prod)
# Lambda will run this on cold starts only.
# -----------------------------------------------------------
@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("[KaiHelper API] Database initialized.")
        print("[KaiHelper DI] Services wired.")
    except Exception as e:
        # Avoid crashing on init—surface a clear log
        print(f"[KaiHelper API] Startup error: {e}")

# -----------------------------------------------------------
# Routes
# -----------------------------------------------------------
app.include_router(user_routes, prefix="/api/users", tags=["Users"])
app.include_router(category_router, prefix="/api/categories", tags=["Categories"])
app.include_router(grocery_router, prefix="/api/groceries", tags=["Groceries"])
app.include_router(budget_router, prefix="/api/budgets", tags=["Budgets"])
app.include_router(expense_router, prefix="/api/expenses", tags=["Expenses"])
app.include_router(receipt_router, prefix="/api/receipts", tags=["Receipts"])

@app.get("/")
def root():
    return {"message": "Welcome to KaiHelper API!"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

# Lambda adapter
handler = Mangum(app)
