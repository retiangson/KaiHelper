"""
Grocery endpoints: add, list
"""
from fastapi import APIRouter, HTTPException, Request
from kaihelper.contracts.grocery_dto import GroceryDTO

router = APIRouter()

@router.post("/")
def add_grocery(dto: GroceryDTO, request: Request):
    service = request.app.state.services.get_grocery_service()
    result = service.add_grocery(dto)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.get("/user/{user_id}")
def list_groceries(user_id: int, request: Request):
    service = request.app.state.services.get_grocery_service()
    result = service.list_groceries(user_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.get("/expense/{expense_id}")
def get_grocery_by_expense_id(expense_id: int, request: Request):
    service = request.app.state.services.get_grocery_service()
    result = service.get_by_expense_id(expense_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}
