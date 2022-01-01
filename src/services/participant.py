from src.models import Participant
from src.repositories import ParticipantRepository
from src.services.base import BaseService


class ParticipantService(BaseService[Participant, ParticipantRepository]):
    def __init__(self, participant_repository: ParticipantRepository):
        super().__init__(participant_repository)
        self.participant_repository = participant_repository
