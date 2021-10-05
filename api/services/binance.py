import hashlib
import hmac
import os
from datetime import datetime
from typing import Dict
from typing import List
from typing import Union
from urllib.parse import urlencode

import requests as r
from pydantic import BaseModel

from config import Settings
from schemas import Balance
from schemas import Wallet


class _BinanceAsset(BaseModel):
    asset: str
    free: float
    locked: float


BINANCE_HOST = "https://api.binance.com"
ACCOUNT_SNAPSHOT_PATH = "/sapi/v1/accountSnapshot"
INVALID_SYMBOLS = {"LDBNB"}  # Locked BNB

settings = Settings()


def get_binance_wallet() -> Wallet:
    s = Settings()

    url = BINANCE_HOST + ACCOUNT_SNAPSHOT_PATH

    payload: Dict[str, Union[str, int]] = {
        "type": "SPOT",
        "timestamp": _get_timestamp_in_seconds(),
    }

    message = urlencode(payload).replace("%40", "@")
    payload["signature"] = _get_hmac(message)

    headers = {
        "X-MBX-APIKEY": s.binance_api_key,
    }

    res = r.get(url, params=payload, headers=headers)
    json = res.json()

    if not res.ok:
        raise ValueError(json)

    # Multiple snapshots are stored in the response under the 'snapshotVos' key. Latest snapshot is the most up to date.
    balances = [_BinanceAsset(**b) for b in json["snapshotVos"][-1]["data"]["balances"]]
    balances = _filter_invalid_balances(balances)

    return _convert_binance_assets(balances)


def _filter_invalid_balances(balances: List[_BinanceAsset]) -> List[_BinanceAsset]:
    """Filters invalid symbols and balances without an amount"""
    filtered_balances = []
    for balance in balances:
        if balance.asset in INVALID_SYMBOLS:
            print(balance.free)  # check if this is BNB
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


def _get_hmac(message: str) -> str:
    """
    param message: Message must be the
    """
    h = hmac.new(settings.binance_secret.encode(), message.encode(), hashlib.sha256)
    return h.hexdigest()


def _get_timestamp_in_seconds() -> int:
    return int(datetime.timestamp(datetime.now()) * 1000)
