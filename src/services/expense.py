from src.models.expense import Expense
from src.repositories.expense import ExpenseRepository
from src.services import BaseService


class ExpenseService(BaseService[Expense, ExpenseRepository]):
    def __init__(self, expense_repository: ExpenseRepository):
        super().__init__(expense_repository)
        self.expense_repository = expense_repository
