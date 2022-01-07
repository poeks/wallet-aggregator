from datetime import datetime
from typing import Dict

import requests
from pydantic import BaseModel

from ..config import Settings
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

    s = Settings()
    url = CELSIUS_HOST + "/wallet/balance"

    headers = {
        "X-Cel-Partner-Token": s.celsius_partner_token,
        "X-Cel-Api-Key": s.celsius_api_key,
    }

    response = requests.request("GET", url, headers=headers)
    celcius_wallet = _CelsiusWallet(**response.json())
    return celcius_wallet.get_wallet()
