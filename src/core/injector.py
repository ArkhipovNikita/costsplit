from dependency_injector import containers, providers

from src.core.db.session import async_scoped_session_factory
from src.domain.repositories import (
    ExpenseRepository,
    ParticipantRepository,
    PartRepository,
    TripRepository,
)
from src.domain.services import (
    ExpenseService,
    ParticipantService,
    PartService,
    TripService,
)


class Container(containers.DeclarativeContainer):
    session = providers.Factory(async_scoped_session_factory)

    trip_repository = providers.Factory(TripRepository, session=session)
    participant_repository = providers.Factory(ParticipantRepository, session=session)
    expense_repository = providers.Factory(ExpenseRepository, session=session)
    part_repository = providers.Factory(PartRepository, session=session)

    trip_service = providers.Factory(TripService, trip_repository=trip_repository)
    participant_service = providers.Factory(
        ParticipantService,
        participant_repository=participant_repository,
    )
    expense_service = providers.Factory(ExpenseService, expense_repository=expense_repository)
    part_service = providers.Factory(PartService, part_repository=part_repository)


def init_container() -> Container:
    container = Container()
    container.init_resources()
    container.wire(packages=['src.app.handlers'])
    return container
