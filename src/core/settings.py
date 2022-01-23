from typing import Optional

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


class RedisSettings(BaseSettings):
    host: str
    port: int
    db: Optional[int]
    password: Optional[str]

    class Config:
        env_prefix = 'redis_'


class BotSettings(BaseSettings):
    api_token: str
    api_id: int
    api_hash: str

    class Config:
        env_prefix = 'bot_'


class AppSettings(BaseSettings):
    date_format: str = '%d-%m-%Y'

    class Config:
        env_prefix = 'app_'


postgres_settings = PostgresSettings()
redis_settings = RedisSettings()
bot_settings = BotSettings()
app_settings = AppSettings()
