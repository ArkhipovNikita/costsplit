from src.domain.models.expense import Expense
from src.domain.repositories.expense import ExpenseRepository
from src.domain.schemes.expense import ExpenseCreateScheme, ExpenseUpdateScheme
from src.domain.services import BaseService


class ExpenseService(
    BaseService[
        Expense,
        ExpenseRepository,
        ExpenseCreateScheme,
        ExpenseUpdateScheme,
    ],
):
    def __init__(self, expense_repository: ExpenseRepository):
        super().__init__(expense_repository)
        self.expense_repository = expense_repository
