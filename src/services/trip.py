from src.models import Trip
from src.repositories import TripRepository
from src.services.base import BaseService


class TripService(BaseService[Trip, TripRepository]):
    def __init__(self, trip_repository: TripRepository):
        super().__init__(trip_repository)
        self.participant_repository = trip_repository
