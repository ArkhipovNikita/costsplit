from src.domain.models.part import Part
from src.domain.repositories import BaseRepository
from src.domain.schemes.part import PartCreateScheme, PartUpdateScheme


class PartRepository(BaseRepository[Part, PartCreateScheme, PartUpdateScheme]):
    pass
