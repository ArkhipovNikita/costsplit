from typing import Optional

from pydantic import BaseModel, PositiveFloat


class ExpenseManualIn(BaseModel):
    amount: Optional[PositiveFloat]

    class Config:
        error_msg_templates = {
            'value_error.number.not_gt': 'Число должно быть больше 0',
            'type_error.float': 'Неверный формат',
        }
