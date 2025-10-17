"""
FastAPI entry point for KaiHelper (Lambda + API Gateway).
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Optional: load .env locally only
try:
    from dotenv import load_dotenv
    import pathlib
    env_path = pathlib.Path(__file__).parents[2] / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except Exception:
    pass

# ---- Stage/base path awareness ----
# We’ll inject STAGE_BASE as "/Prod" (or "/v1") from the SAM template.
#BASE_PATH = os.getenv("STAGE_BASE", "").rstrip("/")
#DOCS_URL = f"{BASE_PATH}/docs" if BASE_PATH else "/docs"
#OPENAPI_URL = f"{BASE_PATH}/openapi.json" if BASE_PATH else "/openapi.json"
#REDOC_URL = f"{BASE_PATH}/redoc" if BASE_PATH else "/redoc"

# Do NOT set root_path; let Mangum handle that via api_gateway_base_path.
#app = FastAPI(
#    title="KaiHelper API",
#    version="1.0",
#    description="Grocery Budgeting App Backend",
#    docs_url=DOCS_URL,
#    redoc_url=REDOC_URL,
#    openapi_url=OPENAPI_URL,
#)

app = FastAPI(
    title="KaiHelper API",
    version="1.0",
    description="Grocery Budgeting App Backend",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc",
)


# CORS (tighten origins later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- KaiHelper wiring ----
from kaihelper.business.services.service_installer import ServiceInstaller
from kaihelper.domain.domain_installer import DomainInstaller
from kaihelper.domain.core.database import Base, engine

from kaihelper.api.routes.user_api import router as user_routes
from kaihelper.api.routes.category_api import router as category_router
from kaihelper.api.routes.grocery_api import router as grocery_router
from kaihelper.api.routes.budget_api import router as budget_router
from kaihelper.api.routes.expense_api import router as expense_router
from kaihelper.api.routes.receipt_api import router as receipt_router

domain = DomainInstaller()
services = ServiceInstaller(domain)
app.state.domain = domain
app.state.services = services

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("[KaiHelper API] Database initialized.")
    except Exception as e:
        print(f"[KaiHelper API] Startup error: {e}")

# Routes
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

# Mangum: tell it the API Gateway base path so it fixes root_path internally.
#handler = Mangum(app, api_gateway_base_path=BASE_PATH or None)

STAGE_BASE = os.getenv("STAGE_BASE")  # e.g. "/Prod"
handler = Mangum(app, api_gateway_base_path=STAGE_BASE)
