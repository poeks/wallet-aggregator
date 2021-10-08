from typing import Optional

from pydantic import BaseSettings


class IncompleteSettingsError(ValueError):
    pass


class KuCoinCredentials(BaseSettings):
    kucoin_api_key: str
    kucoin_secret: str
    kucoin_passphrase: str


class Settings(BaseSettings):
    # TODO cache loading Settings when scaling to avoid reading .env frequently
    binance_api_key: str
    binance_secret: str
    coinmarketcap_api_key: str

    kucoin_api_key: Optional[str] = None
    kucoin_secret: Optional[str] = None
    kucoin_passphrase: Optional[str] = None

    class Config:
        env_file = ".env"

    def get_kucoin_credentials(self) -> KuCoinCredentials:
        if not all({self.kucoin_api_key, self.kucoin_secret, self.kucoin_passphrase}):
            raise IncompleteSettingsError("Kucoin credentials incomplete")

        return KuCoinCredentials(
            kucoin_api_key=self.kucoin_api_key,
            kucoin_secret=self.kucoin_secret,
            kucoin_passphrase=self.kucoin_passphrase,
        )
