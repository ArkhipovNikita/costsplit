from pydantic import BaseModel


class BaseScheme(BaseModel):
    class Config:
        error_msg_templates = {
            'value_error.number.not_gt': 'Число должно быть больше {limit_value}',
            'type_error.float': 'Неверный формат',
            'value_error.any_str.max_length': 'Максимальное число символов {limit_value}'
        }


class DBBaseScheme(BaseScheme):
    id: int

    class Config:
        orm_mode = True
