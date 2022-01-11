from src.models.expense import Expense
from src.repositories import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    pass
