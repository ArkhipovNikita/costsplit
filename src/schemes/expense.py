from typing import Optional

from pydantic import BaseModel, Field, PositiveFloat


class ExpenseManualIn(BaseModel):
    """Model to validate manual entered fields."""

    amount: Optional[PositiveFloat]
    description: Optional[str] = Field(max_length=255)
    part_amount: Optional[PositiveFloat]

    class Config:
        error_msg_templates = {
            'value_error.number.not_gt': 'Число должно быть больше 0',
            'type_error.float': 'Неверный формат',
            'value_error.any_str.max_length': 'Максимальное число символов {limit_value}'
        }
