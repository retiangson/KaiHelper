"""
BudgetMapper
Converts between Budget ORM models and BudgetDTO objects.
"""

# --- First-party imports ---
from kaihelper.domain.models.budget import Budget
from kaihelper.contracts.budget_dto import BudgetDTO


class BudgetMapper:
    """Mapper for converting between Budget model and BudgetDTO."""

    @staticmethod
    def to_dto(model: Budget) -> BudgetDTO:
        """
        Convert a Budget ORM model to a BudgetDTO.

        Args:
            model (Budget): ORM model instance representing a budget record.

        Returns:
            BudgetDTO: Data transfer object representation of the model.
        """
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
        """
        Convert a BudgetDTO to a Budget ORM model.

        Args:
            dto (BudgetDTO): Data transfer object containing budget details.

        Returns:
            Budget: ORM model instance ready for database persistence.
        """
        model = Budget()
        model.user_id = dto.user_id
        model.total_budget = dto.total_budget
        model.start_date = dto.start_date
        model.end_date = dto.end_date
        model.remaining_balance = dto.remaining_balance
        return model
