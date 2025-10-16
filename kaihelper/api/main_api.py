"""
FastAPI entry point for KaiHelper.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI

# ===========================================================
# ✅ Load .env before any KaiHelper imports
# ===========================================================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")

if not os.path.exists(ENV_PATH):
    print(f"❌ .env file not found at: {ENV_PATH}")
else:
    load_dotenv(ENV_PATH)
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not found after load_dotenv()")
    else:
        print(f"✅ OPENAI_API_KEY loaded ({os.getenv('OPENAI_API_KEY')[:8]}...)")

# ===========================================================
# KaiHelper imports (after env is loaded)
# ===========================================================
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


# ===========================================================
# FastAPI app
# ===========================================================
app = FastAPI(
    title="KaiHelper API",
    version="1.0",
    description="Grocery Budgeting App Backend"
)

# ===========================================================
# Dependency Injection setup
# ===========================================================
domain = DomainInstaller()
services = ServiceInstaller(domain)
app.state.domain = domain
app.state.services = services

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    print("[KaiHelper API] Database initialized.")
    print("[KaiHelper DI] IUserService wired.")


# ===========================================================
# Routes
# ===========================================================
app.include_router(user_routes, prefix="/api/users", tags=["Users"])
app.include_router(category_router, prefix="/api/categories", tags=["Categories"])
app.include_router(grocery_router, prefix="/api/groceries", tags=["Groceries"])
app.include_router(budget_router, prefix="/api/budgets", tags=["Budgets"])
app.include_router(expense_router, prefix="/api/expenses", tags=["Expenses"])
app.include_router(receipt_router, prefix="/api/receipts", tags=["Receipts"])


@app.get("/")
def root():
    return {"message": "Welcome to KaiHelper API!"}


print("[KaiHelper API] Initialized. Swagger: /docs")
