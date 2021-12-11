import re
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base, declared_attr

__all__ = ['BaseTable', 'metadata']

convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}
metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


def classname_to_tablename(name: str) -> str:
    """
    Converts input class name to table name with snake case style
    """
    result: List[str] = []

    last_index = 0
    for match in re.finditer(
            r'(?P<abbreviation>[A-Z]+(?![a-z]))|(?P<word>[A-Za-z][a-z]+)|(?P<digit>\d+)',
            name,
    ):
        if match.start() != last_index:
            raise ValueError(f'Could not translate class name "{name}" to table name')

        last_index = match.end()
        result.append(match.group().lower())

    return '_'.join(result)


class BaseTable(Base):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> Optional[str]:
        return classname_to_tablename(cls.__name__)

    id = sa.Column(sa.Integer(), primary_key=True)
