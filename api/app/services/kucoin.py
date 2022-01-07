import base64
import hashlib
import hmac
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict
from typing import List

import requests as r
from pydantic import BaseModel

from ..config import Settings
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
    s = Settings().get_kucoin_credentials()

    # See https://docs.kucoin.com/#authentication.
    now_time = int(time.time()) * 1000
    method = "GET"
    uri_path = "/api/v1/accounts"
    url = KUCOIN_HOST + uri_path
    str_to_sign = str(now_time) + method + uri_path
    sign = base64.b64encode(
        hmac.new(
            s.kucoin_secret.encode("utf-8"), str_to_sign.encode("utf-8"), hashlib.sha256
        ).digest()
    )
    passphrase = base64.b64encode(
        hmac.new(
            s.kucoin_secret.encode("utf-8"),
            s.kucoin_passphrase.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    )

    headers = {
        "KC-API-SIGN": sign,
        "KC-API-TIMESTAMP": str(now_time),
        "KC-API-KEY": s.kucoin_api_key,
        "KC-API-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
        "KC-API-KEY-VERSION": "2",
    }

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
