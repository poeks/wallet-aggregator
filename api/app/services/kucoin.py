from collections import defaultdict
from datetime import datetime
from json import JSONDecodeError
from typing import Dict
from typing import List
from typing import Set

import requests as r
from pydantic import BaseModel

from ..config import IncompleteCredentialsError
from ..config import Settings
from ..credentials import CredentialsStatusOut
from ..credentials import WalletCredentialsStatus
from ..schemas import Balance
from ..schemas import Wallet

KUCOIN_HOST = "https://api.kucoin.com"


class _KucoinAsset(BaseModel):
    currency: str
    available: float
    balance: float
    holds: float
    id: str
    type: str


class KuCoinGETAccountResponse(BaseModel):
    data: List[_KucoinAsset]


def get_kucoin_wallet() -> "Wallet":
    """
    See https://docs.kucoin.com/ for reference.

    All timestamps are in miliseconds.
    """
    credentials = Settings().get_kucoin_credentials()
    uri_path = "/api/v1/accounts"
    url = KUCOIN_HOST + uri_path
    headers = credentials.headers(uri_path=uri_path)
    res = r.get(url, headers=headers)

    if not res.ok:
        raise ValueError(f"Kucoin service unavailable")

    data = res.json()

    # Parse balances.
    # Kucoin has 3 account types: main, trade, and margin.
    balances: Dict[str, float] = defaultdict(int)
    for balance in data["data"]:
        balances[balance["currency"]] += float(balance["balance"])

    aggregated_balances = [
        Balance(symbol=symbol, amount=amount) for symbol, amount in balances.items()
    ]

    return Wallet(name="Kucoin", date=datetime.now(), balances=aggregated_balances)


class KucoinCredentialsStatus(WalletCredentialsStatus):
    @property
    def name(self) -> str:
        return "Kucoin"

    @property
    def credential_fields(self) -> Set[str]:
        return {"api_key", "secret", "passphrase"}


def get_credentials_status() -> CredentialsStatusOut:
    """
    Verifies:
        - credentials are submitted
        - API key has read access
    """
    try:
        credentials = Settings().get_kucoin_credentials()
    except IncompleteCredentialsError as e:
        return KucoinCredentialsStatus().response_model(reason=str(e))

    status = KucoinCredentialsStatus(credentials_submitted=True)

    uri_path = "/api/v1/accounts"
    url = KUCOIN_HOST + uri_path
    headers = credentials.headers(uri_path=uri_path)
    res = r.get(url, headers=headers)

    if not res.ok:
        return status.response_model(reason=res.reason)

    try:
        res.json()
    except JSONDecodeError as e:
        return status.response_model(reason=str(e))

    status.credentials_valid = True

    return status.response_model()
