from src.domain.models.expense import Expense
from src.domain.repositories import BaseRepository
from src.domain.schemes.expense import ExpenseCreateScheme, ExpenseUpdateScheme


class ExpenseRepository(BaseRepository[Expense, ExpenseCreateScheme, ExpenseUpdateScheme]):
    pass
