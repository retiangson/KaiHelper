"""
Expense endpoints: add, list
"""
from fastapi import APIRouter, HTTPException, Request
from kaihelper.contracts.expense_dto import ExpenseDTO

router = APIRouter()

@router.post("/")
def add_expense(dto: ExpenseDTO, request: Request):
    service = request.app.state.services.get_expense_service()
    result = service.add_expense(dto)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.get("/user/{user_id}")
def list_expenses(user_id: int, request: Request):
    service = request.app.state.services.get_expense_service()
    result = service.list_expenses(user_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}
