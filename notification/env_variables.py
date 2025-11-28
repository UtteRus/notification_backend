from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvVariables(BaseSettings):
    # SECRET_KEY: str
    DEBUG: bool = False
    BACKEND_HOST: str = 'localhost'
    ALLOWED_HOSTS: list[str] = ['localhost']
    SERVICE_TOKEN: str = ''
    SWAGGER_URL_PROTOCOL: str = 'http'

    # Databases
    POSTGRES_HOSTNAME: str
    POSTGRES_DB_NAME: str

    POSTGRES_DB_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int

    # Cache
    CACHE_URL: str

    # Simple JWT
    ACCESS_TOKEN_LIFETIME: int = 60
    REFRESH_TOKEN_LIFETIME: int = 60
    MAX_INACTIVE_DAY: int = 30


    # SMTP server
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str
    EMAIL_USE_TLS: bool
    DEFAULT_FROM_EMAIL: str


    model_config = SettingsConfigDict(
        env_file='.environment',
        env_file_encoding='utf-8',
        extra='ignore',
    )


env_variables = EnvVariables()
