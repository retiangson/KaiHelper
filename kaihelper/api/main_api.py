"""
FastAPI entry point for KaiHelper.
"""
from fastapi import FastAPI
from kaihelper.business.service.service_installer import ServiceInstaller
from kaihelper.domain.domain_installer import DomainInstaller
from kaihelper.api.routes import user_routes
from kaihelper.domain.core.database import Base, engine

app = FastAPI(title="KaiHelper API", version="1.0.0")

# DI containers
domain = DomainInstaller()
services = ServiceInstaller(domain)
app.state.domain = domain
app.state.services = services

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    print("[KaiHelper API] Database initialized.")
    print("[KaiHelper DI] IUserService wired.")

# Routes
app.include_router(user_routes.router, prefix="/api/users", tags=["Users"])

@app.get("/")
def root():
    return {"message": "Welcome to KaiHelper API!"}

print("[KaiHelper API] Initialized. Swagger: /docs")
