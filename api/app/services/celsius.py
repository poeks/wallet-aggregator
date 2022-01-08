from datetime import datetime
from typing import Dict
from typing import Set

import requests as r
from pydantic import BaseModel

from ..config import IncompleteCredentialsError
from ..config import Settings
from ..credentials import CredentialsStatusOut
from ..credentials import WalletCredentialsStatus
from ..schemas import Balance
from ..schemas import Wallet

CELSIUS_HOST = "https://wallet-api.celsius.network"


class _CelsiusWallet(BaseModel):
    balance: Dict[str, float]

    def get_wallet(self, filter_empty_balances: bool = True) -> Wallet:
        balances = [
            Balance(symbol=symbol.upper(), amount=amount)
            for symbol, amount in self.balance.items()
        ]

        if filter_empty_balances:
            balances = [balance for balance in balances if balance.amount > 0]

        return Wallet(
            name="Celsius",
            date=datetime.now(),
            balances=balances,
        )


def get_celsius_wallet() -> Wallet:

    credentials = Settings().get_celcius_credentials()
    url = CELSIUS_HOST + "/wallet/balance"

    response = r.get(url, headers=credentials.headers)
    celcius_wallet = _CelsiusWallet(**response.json())
    return celcius_wallet.get_wallet()


class CelsiusCredentialsStatus(WalletCredentialsStatus):
    @property
    def name(self) -> str:
        return "Celsius"

    @property
    def credential_fields(self) -> Set[str]:
        return {"api_key", "partner_token"}


def get_credentials_status() -> CredentialsStatusOut:
    """
    Verifies:
        - credentials are submitted
        - API key has read access
    """
    try:
        credentials = Settings().get_celcius_credentials()
    except IncompleteCredentialsError:
        return CelsiusCredentialsStatus(reason="Credentials incomplete").response_model()

    status = CelsiusCredentialsStatus(credentials_submitted=True)

    url = CELSIUS_HOST + "/util/supported_currencies"
    # url = CELSIUS_HOST + "/wallet/balance"

    res = r.get(url, headers=credentials.headers)

    if not res.ok:
        return status.response_model(reason=res.reason)

    status.credentials_valid = True

    return status.response_model()
