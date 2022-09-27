from datetime import timedelta

from pydantic import BaseSettings


class Settings(BaseSettings):

    secret: str

    admin_email: str

    db_dsn: str

    is_bare: bool

    jwt_delta: int # token expire minutes

    sec_algorithm: str

    invite_delta: int # new invite delay hours

    max_complaints: int = 9

    max_list: int = 25

    class Config:
        env_file = "app/.env"


settings = Settings()
settings.jwt_delta = timedelta(minutes=settings.jwt_delta)
settings.invite_delta = timedelta(hours=settings.invite_delta)
