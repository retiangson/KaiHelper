"""
Grocery endpoints: add, list, get, update, delete
"""
from fastapi import APIRouter, HTTPException, Request
from kaihelper.contracts.grocery_dto import GroceryDTO

router = APIRouter()

@router.post("/", response_model=dict)
def add_grocery(dto: GroceryDTO, request: Request):
    """Add a new grocery item."""
    service = request.app.state.services.get_grocery_service()
    result = service.add_grocery(dto)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.get("/user/{user_id}", response_model=dict)
def list_groceries(user_id: int, request: Request):
    """Get all groceries for a specific user."""
    service = request.app.state.services.get_grocery_service()
    result = service.list_groceries(user_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.get("/expense/{expense_id}", response_model=dict)
def list_groceries_by_expense(expense_id: int, request: Request):
    """Get groceries belonging to a specific expense."""
    service = request.app.state.services.get_grocery_service()
    result = service.get_by_expense_id(expense_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.get("/{grocery_id}", response_model=dict)
async def get_grocery(grocery_id: int, request: Request):
    """Get a single grocery item by ID."""
    service = request.app.state.services.get_grocery_service()
    result = service.get_by_grocery_id(grocery_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.put("/update")
async def update_grocery(grocery: GroceryDTO, request: Request = None):
    """Update grocery details using ID inside DTO."""
    service = request.app.state.services.get_grocery_service()
    if not grocery.grocery_id:
        raise HTTPException(status_code=400, detail="Missing grocery_id in body.")
    result = service.update(grocery)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.delete("/delete/{grocery_id}", response_model=dict)
def delete_grocery(grocery_id: int, request: Request):
    """Delete grocery item."""
    service = request.app.state.services.get_grocery_service()
    result = service.delete(grocery_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return {"success": True, "message": result.message}
