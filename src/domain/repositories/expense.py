from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.domain.models import Part
from src.domain.models.expense import Expense
from src.domain.repositories import BaseRepository
from src.domain.schemes.expense import ExpenseCreateScheme, ExpenseUpdateScheme


class ExpenseRepository(BaseRepository[Expense, ExpenseCreateScheme, ExpenseUpdateScheme]):
    async def get_full(self, expense_id: int) -> Expense:
        """Get `Expense` object with payer, parts and debtors info loaded."""
        query = (
            select(Expense)
            .where(Expense.id == expense_id)
            .options(
                joinedload(Expense.payer),
                joinedload(Expense.parts).joinedload(Part.debtor),
            )
        )

        res = await self._session.execute(query)
        res = res.scalars().first()

        return res
