from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings, SettingsConfigDict


env_path = Path().cwd() / '.env' # Путь до .env-файла (.env-файл лежит рядом с main.py).

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=env_path)

  POSTGRES_DRIVER: str
  POSTGRES_DB: str
  POSTGRES_USER: str
  POSTGRES_PASSWORD: str
  PORT_DB: str
  POSTGRES_IP: str

  def get_url(self):
    return f'postgresql+{self.POSTGRES_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_IP}:{self.PORT_DB}/{self.POSTGRES_DB}'

settings = Settings() # pyright: ignore[reportCallIssue]

engine = create_engine(settings.get_url(), echo=False) # Движок.

Session = sessionmaker(engine, autoflush=False) # Конструктор класса сессии.

Base = declarative_base() # Класс, наследуясь от которого, получаем классы, связанные с таблицами в БД.
