# core/config.py
# --- Importar SettingsConfigDict ---
from pydantic_settings import BaseSettings, SettingsConfigDict # <--- Añadir SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Reemplazar class Config por model_config ---
    model_config = SettingsConfigDict( # <--- Usar model_config
        env_file=".env"
        # Si necesitas ignorar campos extra en el .env, añade:
        # extra='ignore'
    )
    # --- Eliminar la clase Config antigua ---
    # class Config:             <--- Eliminar esta línea
    #     env_file = ".env"     <--- Eliminar esta línea

settings = Settings() # Esta línea se queda igual