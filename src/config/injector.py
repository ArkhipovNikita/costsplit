from dependency_injector import containers, providers

from src.db.session import async_scoped_session_factory


class Container(containers.DeclarativeContainer):
    session = providers.Factory(async_scoped_session_factory)


def init_container() -> Container:
    container = Container()
    container.init_resources()
    container.wire(packages=['src.handlers'])
    return container
