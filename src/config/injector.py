from dependency_injector import containers, providers

from src.db.session import async_scoped_session_factory
from src.repositories import TripRepository
from src.services import TripService


class Container(containers.DeclarativeContainer):
    session = providers.Factory(async_scoped_session_factory)

    trip_repository = providers.Factory(TripRepository, session=session)

    trip_service = providers.Factory(TripService, trip_repository=trip_repository)


def init_container() -> Container:
    container = Container()
    container.init_resources()
    container.wire(packages=['src.handlers'])
    return container
