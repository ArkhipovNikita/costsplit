from src.domain.models.part import Part
from src.domain.repositories.part import PartRepository
from src.domain.schemes.part import PartCreateScheme, PartUpdateScheme
from src.domain.services import BaseService


class PartService(
    BaseService[
        Part,
        PartRepository,
        PartCreateScheme,
        PartUpdateScheme,
    ],
):
    def __init__(self, part_repository: PartRepository):
        super().__init__(part_repository)
        self.part_repository = part_repository
