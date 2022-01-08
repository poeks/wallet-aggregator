from typing import Dict
from typing import Optional

from pydantic import BaseSettings


class IncompleteSettingsError(ValueError):
    pass


class KuCoinCredentials(BaseSettings):
    kucoin_api_key: str
    kucoin_secret: str
    kucoin_passphrase: str


class AmberDataCredentials(BaseSettings):
    api_key: str

    @property
    def headers(self) -> Dict[str, str]:
        return {"x-api-key": self.api_key}


class CoinMarketCapCredentials(BaseSettings):
    api_key: str

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json",
        }


class Settings(BaseSettings):
    # TODO cache loading Settings when scaling to avoid reading .env frequently
    # Price platform API keys.
    coinmarketcap_api_key: Optional[str] = None
    amberdata_api_key: Optional[str] = None

    # Wallet API keys.
    binance_api_key: str
    binance_secret: str

    celsius_api_key: str
    celsius_partner_token: str

    kucoin_api_key: Optional[str] = None
    kucoin_secret: Optional[str] = None
    kucoin_passphrase: Optional[str] = None

    ethereum_wallet_address: Optional[str] = None

    class Config:
        env_file = ".env"

    def get_coinmarketcap_credentials(self) -> CoinMarketCapCredentials:
        if self.coinmarketcap_api_key is None:
            raise IncompleteSettingsError("No CoinMarketcap API key available")
        return CoinMarketCapCredentials(api_key=self.coinmarketcap_api_key)

    def get_amberdata_credentials(self) -> AmberDataCredentials:
        if self.amberdata_api_key is None:
            raise IncompleteSettingsError("No Amber API key available")
        return AmberDataCredentials(api_key=self.amberdata_api_key)

    def get_ethereum_wallet_address(self) -> str:
        if self.ethereum_wallet_address is None:
            raise IncompleteSettingsError("No ethereum wallet address available")
        return self.ethereum_wallet_address

    def get_kucoin_credentials(self) -> KuCoinCredentials:
        if not all({self.kucoin_api_key, self.kucoin_secret, self.kucoin_passphrase}):
            raise IncompleteSettingsError("Kucoin credentials incomplete")

        return KuCoinCredentials(
            kucoin_api_key=self.kucoin_api_key,
            kucoin_secret=self.kucoin_secret,
            kucoin_passphrase=self.kucoin_passphrase,
        )
