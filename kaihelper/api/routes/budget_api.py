"""
Budget endpoints: create, list
"""
from fastapi import APIRouter, HTTPException, Request
from kaihelper.contracts.budget_dto import BudgetDTO

router = APIRouter()

@router.post("/")
def create_budget(dto: BudgetDTO, request: Request):
    service = request.app.state.services.get_budget_service()
    result = service.create_budget(dto)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.get("/user/{user_id}")
def list_budgets(user_id: int, request: Request):
    service = request.app.state.services.get_budget_service()
    result = service.list_budgets(user_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}
