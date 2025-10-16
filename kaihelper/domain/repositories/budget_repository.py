from kaihelper.domain.core.database import SessionLocal
from kaihelper.domain.models.budget import Budget
from kaihelper.domain.mappers.budget_mapper import BudgetMapper
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.budget_dto import BudgetDTO

class BudgetRepository:
    """Repository for CRUD operations on Budget."""

    def __init__(self):
        self.db = SessionLocal()

    def create(self, dto: BudgetDTO) -> ResultDTO:
        try:
            model = BudgetMapper.to_model(dto)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return ResultDTO(True, "Budget created successfully", BudgetMapper.to_dto(model))
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Failed to create budget: {e}")
        finally:
            self.db.close()

    def get_active_budgets(self, user_id: int) -> ResultDTO:
        try:
            budgets = self.db.query(Budget).filter_by(user_id=user_id).all()
            data = [BudgetMapper.to_dto(b) for b in budgets]
            return ResultDTO(True, "Budgets retrieved successfully", data)
        except Exception as e:
            return ResultDTO(False, f"Failed to retrieve budgets: {e}")
        finally:
            self.db.close()
            
