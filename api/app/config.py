from typing import Dict
from typing import Optional

from pydantic import BaseSettings


class IncompleteCredentialsError(ValueError):
    pass


class BinanceCredentials(BaseSettings):
    api_key: str
    secret: str

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "X-MBX-APIKEY": self.api_key,
        }


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
    binance_api_key: Optional[str] = None
    binance_secret: Optional[str] = None

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
            raise IncompleteCredentialsError("No CoinMarketcap API key available")
        return CoinMarketCapCredentials(api_key=self.coinmarketcap_api_key)

    def get_amberdata_credentials(self) -> AmberDataCredentials:
        if self.amberdata_api_key is None:
            raise IncompleteCredentialsError("No Amber API key available")
        return AmberDataCredentials(api_key=self.amberdata_api_key)

    def get_ethereum_wallet_address(self) -> str:
        if self.ethereum_wallet_address is None:
            raise IncompleteCredentialsError("No ethereum wallet address available")
        return self.ethereum_wallet_address

    def get_binance_credentials(self) -> BinanceCredentials:
        if not all({self.binance_api_key, self.binance_secret}):
            raise IncompleteCredentialsError("Binance credentials incomplete")

        return BinanceCredentials(
            api_key=self.binance_api_key,
            secret=self.binance_secret,
        )

    def get_kucoin_credentials(self) -> KuCoinCredentials:
        if not all({self.kucoin_api_key, self.kucoin_secret, self.kucoin_passphrase}):
            raise IncompleteCredentialsError("Kucoin credentials incomplete")

        return KuCoinCredentials(
            kucoin_api_key=self.kucoin_api_key,
            kucoin_secret=self.kucoin_secret,
            kucoin_passphrase=self.kucoin_passphrase,
        )
