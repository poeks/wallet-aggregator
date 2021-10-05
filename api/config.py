from pydantic import BaseSettings


class Settings(BaseSettings):
    # TODO cache loading Settings when scaling to avoid reading .env frequently
    binance_api_key: str
    binance_secret: str
    coinmarketcap_api_key: str

    class Config:
        env_file = ".env"
