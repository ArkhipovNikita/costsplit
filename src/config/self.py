from pydantic import BaseSettings


class PostgresSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    name: str

    dialect: str = 'postgresql'
    async_driver: str = 'asyncpg'

    class Config:
        env_prefix = 'pg_'

    @property
    def _base_url(self):
        return f'{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'

    @property
    def async_url(self):
        return f'{self.dialect}+{self.async_driver}://{self._base_url}'

    @property
    def sync_url(self):
        return f'{self.dialect}://{self._base_url}'


class BotSettings(BaseSettings):
    api_token: str

    class Config:
        env_prefix = 'bot_'


postgres_settings = PostgresSettings()
bot_settings = BotSettings()
