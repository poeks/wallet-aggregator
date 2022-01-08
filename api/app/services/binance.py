import hashlib
import hmac
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Dict
from typing import List
from typing import Set
from typing import Union
from urllib.parse import urlencode

import requests as r
from pydantic import BaseModel

from ..config import IncompleteCredentialsError
from ..config import Settings
from ..credentials import CredentialsStatusOut
from ..credentials import WalletCredentialsStatus
from ..schemas import Balance
from ..schemas import Wallet

BINANCE_HOST = "https://api.binance.com"
ACCOUNT_SNAPSHOT_PATH = "/sapi/v1/accountSnapshot"
INVALID_SYMBOLS = {"LDBNB"}  # Locked BNB


class _BinanceAsset(BaseModel):
    asset: str
    free: float
    locked: float


def get_binance_wallet() -> Wallet:
    credentials = Settings().get_binance_credentials()

    url = BINANCE_HOST + ACCOUNT_SNAPSHOT_PATH

    payload = _get_payload(credentials.secret, type="SPOT")
    res = r.get(url, params=payload, headers=credentials.headers)
    json = res.json()

    if not res.ok:
        raise ValueError(json)

    # Multiple snapshots are stored in the response under the 'snapshotVos' key. Latest snapshot is the most up to date.
    balances = [_BinanceAsset(**b) for b in json["snapshotVos"][-1]["data"]["balances"]]
    balances = _filter_invalid_balances(balances)

    return _convert_binance_assets(balances)


def _urlencode_payload(payload: Dict[str, Union[str, int]]) -> str:
    return urlencode(payload).replace("%40", "@")


def _get_payload(secret: str, **kwargs: str) -> Dict[str, Union[str, int]]:
    """
    See https://binance-docs.github.io/apidocs/spot/en/#signed-trade-user_data-and-margin-endpoint-security
    """
    payload: Dict[str, Union[str, int]] = {
        "timestamp": _get_timestamp_in_seconds(),
        **kwargs,
    }
    message = _urlencode_payload(payload)
    payload["signature"] = _get_hmac(secret, message)
    return payload


def _filter_invalid_balances(balances: List[_BinanceAsset]) -> List[_BinanceAsset]:
    """Filters invalid symbols and balances without an amount"""
    filtered_balances = []
    for balance in balances:
        if balance.asset in INVALID_SYMBOLS:
            continue
        if balance.free <= 0:
            continue
        filtered_balances.append(balance)

    return filtered_balances


def _convert_binance_assets(data: List[_BinanceAsset]) -> Wallet:
    balances = []
    for balance in data:
        balances.append(Balance(symbol=balance.asset, amount=balance.free))

    return Wallet(name="Binance", date=datetime.now(), balances=balances)


def _get_hmac(secret: str, message: str) -> str:
    """
    :param secret: Binance secret
    :param message: URL encoded payload.
    """
    h = hmac.new(secret.encode(), message.encode(), hashlib.sha256)
    return h.hexdigest()


def _get_timestamp_in_seconds() -> int:
    return int(datetime.timestamp(datetime.now()) * 1000)


class BinanceCredentialsStatus(WalletCredentialsStatus):
    @property
    def name(self) -> str:
        return "Binance"

    @property
    def credential_fields(self) -> Set[str]:
        return {"api_key", "secret"}


def get_credentials_status() -> CredentialsStatusOut:
    """
    Verifies:
        - credentials are submitted
        - API key has read access
    """
    try:
        credentials = Settings().get_binance_credentials()
    except IncompleteCredentialsError:
        return BinanceCredentialsStatus(
            not_valid_reason="Credentials incomplete"
        ).response_model()

    url = BINANCE_HOST + "/sapi/v1/account/apiRestrictions"

    payload = _get_payload(credentials.secret)
    res = r.get(url, params=payload, headers=credentials.headers)

    from pprint import pprint

    status = BinanceCredentialsStatus(credentials_submitted=True)

    if not res.ok:
        status.not_valid_reason = res.reason
        return status.response_model()

    try:
        data = res.json()
    except JSONDecodeError as e:
        status.not_valid_reason = str(e)
        return status

    if data["enableReading"]:
        status.credentials_valid = True

    return status.response_model()
