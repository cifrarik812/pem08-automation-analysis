"""Local configuration. Credentials are loaded only from an external .env."""
import logging
import os
from pathlib import Path
from typing import Literal
from dotenv import dotenv_values
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent
logger = logging.getLogger('competitor_monitor')

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra='ignore')
    api_host: Literal['127.0.0.1', 'localhost'] = '127.0.0.1'
    api_port: int = 8008
    history_file: str = str(ROOT / 'outputs' / 'history.json')
    max_history_items: int = 10
    parser_timeout: int = 30
    parser_user_agent: str = 'PEM08-Educational-Research/1.0'
    gigachat_authorization_key: SecretStr = SecretStr('')
    gigachat_scope: str = 'GIGACHAT_API_PERS'
    gigachat_model: str = 'GigaChat-2'
    gigachat_vision_model: str = 'GigaChat-2-Pro'
    gigachat_ca_bundle: str = ''
    gigachat_api_base: str = 'https://gigachat.devices.sberbank.ru/api'
    gigachat_timeout: float = Field(90, gt=0, le=180)
    competitor_urls: tuple[str, ...] = ('https://n8n.io/', 'https://www.make.com/en', 'https://albato.ru/')

    @property
    def openai_model(self):
        return self.gigachat_model

    @property
    def openai_vision_model(self):
        return self.gigachat_vision_model

def load_settings():
    values = {}
    external = os.environ.get('PEM08_ENV_FILE')
    if external:
        if not Path(external).is_file():
            raise ValueError('PEM08_ENV_FILE не найден')
        env = dotenv_values(external)
        for name in ('GIGACHAT_AUTHORIZATION_KEY', 'GIGACHAT_SCOPE', 'GIGACHAT_MODEL', 'GIGACHAT_CA_BUNDLE'):
            if env.get(name) and name not in os.environ:
                values[name.lower()] = env[name]
    return Settings(**values)

settings = load_settings()
