import os
import sys
from datetime import timedelta
from urllib.parse import quote_plus
from colorama import Fore, Style
from pydantic import Field, field_validator, ValidationError
from pydantic_settings import BaseSettings

ENV = os.getenv('FLASK_ENV', 'development')

def load_settings():
    try:
        return Settings()
    except ValidationError as e:
        print(f"\n{Fore.RED}CONFIG ERROR:{Style.RESET_ALL}\n")

        for err in e.errors():
            field = err["loc"][0]
            print(f" - {Fore.YELLOW}{field.upper()} {Fore.RED}missing or invalid{Style.RESET_ALL}")

        print(f"\n{Fore.RED}App startup aborted.{Style.RESET_ALL}\n")
        sys.exit(1)

class Settings(BaseSettings):
    # FRONTEND
    frontend_url: str = Field(..., min_length=1)
    frontend_port: int = Field(..., gt=0)

    # MONGODB
    mongodb_user: str = Field(..., min_length=1)
    mongodb_password: str = Field(..., min_length=1)
    mongodb_host: str = Field(..., min_length=1)
    mongodb_port: int = Field(..., gt=0)
    mongodb_database: str = Field(..., min_length=1)
    mongodb_timeout: int = Field(..., gt=0)

    # JWT
    jwt_secret_key: str = Field(..., min_length=1)
    jwt_access_token_expires: int = Field(..., gt=0)  # in minutes
    jwt_refresh_token_expires: int = Field(..., gt=0) # in days
    jwt_cookie_secure: bool = Field(...)
    jwt_cookie_samesite: str = Field(..., min_length=1)
    jwt_cookie_csrf_protect: bool = Field(...)

    # PATHS
    base_dir: str = os.path.dirname(os.path.abspath(__file__))
    upload_folder: str = os.path.join(base_dir, 'uploads')

    # FILE TYPES
    allowed_audio_file_types: list[str] = ['mp3', 'wma', 'aac', 'flac', 'ogg', 'wav', 'aiff', 'alac', 'amr', 'm4a']
    allowed_image_file_types: list[str] = ['jpg', 'jpeg', 'png', 'gif', 'webp']

    @field_validator("*")
    @classmethod
    def no_empty_strings(cls, value):
        if isinstance(value, str) and not value.strip():
            raise ValueError("Empty string is not allowed")
        return value

    @property
    def mongo_uri(self) -> str:
        password = quote_plus(self.mongodb_password)
        return (
            f"mongodb://{self.mongodb_user}:{password}@"
            f"{self.mongodb_host}:{self.mongodb_port}/"
            f"{self.mongodb_database}"
            f"?authSource={self.mongodb_database}"
            f"&serverSelectionTimeoutMS={self.mongodb_timeout}"
        )

    @property
    def jwt_access_token_expires_delta(self) -> timedelta:
        return timedelta(minutes=self.jwt_access_token_expires)

    @property
    def jwt_refresh_token_expires_delta(self) -> timedelta:
        return timedelta(days=self.jwt_refresh_token_expires)

    class Config:
        env_file = f'./.env.{ENV}'
        case_sensitive = False
