from src.models.expense import Expense
from src.repositories import BaseRepository
from src.schemes.expense import ExpenseCreateScheme, ExpenseUpdateScheme


class ExpenseRepository(BaseRepository[Expense, ExpenseCreateScheme, ExpenseUpdateScheme]):
    pass
