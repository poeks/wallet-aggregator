import base64
import hashlib
import hmac
import time
from typing import Dict
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import BaseSettings


class IncompleteCredentialsError(ValueError):
    pass


class BinanceCredentials(BaseModel):
    api_key: str
    secret: str

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "X-MBX-APIKEY": self.api_key,
        }


class KuCoinCredentials(BaseModel):
    api_key: str
    secret: str
    passphrase: str

    def headers(self, uri_path: str) -> Dict[str, Union[str, bytes]]:
        """Generates General headers, suitaible for most GET requests.

        See https://docs.kucoin.com/#authentication.
        """
        now_time = int(time.time()) * 1000
        method = "GET"
        str_to_sign = str(now_time) + method + uri_path
        sign = base64.b64encode(
            hmac.new(
                self.secret.encode("utf-8"), str_to_sign.encode("utf-8"), hashlib.sha256
            ).digest()
        )
        passphrase = base64.b64encode(
            hmac.new(
                self.secret.encode("utf-8"),
                self.passphrase.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        )

        return {
            "KC-API-SIGN": sign,
            "KC-API-TIMESTAMP": str(now_time),
            "KC-API-KEY": self.api_key,
            "KC-API-PASSPHRASE": passphrase,
            "Content-Type": "application/json",
            "KC-API-KEY-VERSION": "2",
        }


class AmberDataCredentials(BaseModel):
    api_key: str

    @property
    def headers(self) -> Dict[str, str]:
        return {"x-api-key": self.api_key}


class CoinMarketCapCredentials(BaseModel):
    api_key: str

    @property
    def headers(self) -> Dict[str, str]:
        """See https://documenter.getpostman.com/view/15615753/TzeTJ9VL#authentication"""
        return {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json",
        }


class CelciusCredentials(BaseModel):
    api_key: str
    partner_token: str

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "X-Cel-Api-Key": self.api_key,
            "X-Cel-Partner-Token": self.partner_token,
        }


class Settings(BaseSettings):
    # TODO cache loading Settings when scaling to avoid reading .env frequently
    # Price platform API keys.
    coinmarketcap_api_key: Optional[str] = None
    amberdata_api_key: Optional[str] = None

    # Wallet API keys.
    binance_api_key: Optional[str] = None
    binance_secret: Optional[str] = None

    celsius_api_key: Optional[str] = None
    celsius_partner_token: Optional[str] = None

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
            raise IncompleteCredentialsError("KuCoin credentials incomplete")

        return KuCoinCredentials(
            api_key=self.kucoin_api_key,
            secret=self.kucoin_secret,
            passphrase=self.kucoin_passphrase,
        )

    def get_celcius_credentials(self) -> CelciusCredentials:
        if not all({self.celsius_api_key, self.celsius_partner_token}):
            raise IncompleteCredentialsError("Celcius credentials incomplete")

        return CelciusCredentials(
            api_key=self.celsius_api_key,
            partner_token=self.celsius_partner_token,
        )
