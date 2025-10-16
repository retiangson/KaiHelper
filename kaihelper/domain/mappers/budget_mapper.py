from kaihelper.domain.models.budget import Budget
from kaihelper.contracts.budget_dto import BudgetDTO

class BudgetMapper:
    @staticmethod
    def to_dto(model: Budget) -> BudgetDTO:
        return BudgetDTO(
            budget_id=model.budget_id,
            user_id=model.user_id,
            total_budget=model.total_budget,
            start_date=model.start_date,
            end_date=model.end_date,
            remaining_balance=model.remaining_balance,
        )

    @staticmethod
    def to_model(dto: BudgetDTO) -> Budget:
        model = Budget()
        model.user_id = dto.user_id
        model.total_budget = dto.total_budget
        model.start_date = dto.start_date
        model.end_date = dto.end_date
        model.remaining_balance = dto.remaining_balance
        return model
