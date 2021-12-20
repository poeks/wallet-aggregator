from datetime import datetime
from typing import Dict
from typing import List

import requests as r

from ..config import Settings
from ..schemas import Balance
from ..schemas import Wallet

AMBERDATA_HOST = "https://web3api.io/"


def get_ethereum_wallet() -> Wallet:
    """Gets the ETH and all ERC20 token balances of the wallet address"""
    s = Settings()
    address = s.get_ethereum_wallet_address()
    headers = {"x-api-key": s.get_amberdata_api_key()}

    balances: List[Balance] = []
    # Get ETH balance.
    balances.append(_get_ethereum_balance(address, headers=headers))

    # Get ERC20 tokens.
    tokens = _get_erc20_tokens_balances(address, headers=headers)
    balances.extend(tokens)

    return Wallet(name="Ethereum", date=datetime.now(), balances=balances)


def _convert_wei_to_eth(value: float) -> float:
    return value * 1e-18


def _get_ethereum_balance(address: str, headers: Dict[str, str]) -> Balance:
    url = AMBERDATA_HOST + f"api/v2/addresses/{address}/account-balances/latest"
    res = r.get(url, headers=headers)
    if not res.ok:
        raise ValueError

    data = res.json()

    return Balance(
        symbol="ETH", amount=_convert_wei_to_eth(float(data["payload"]["value"]))
    )


def _get_erc20_tokens_balances(address: str, headers: Dict[str, str]) -> List[Balance]:
    url = AMBERDATA_HOST + f"api/v2/addresses/{address}/token-balances/latest"
    res = r.get(url, headers=headers)
    if not res.ok:
        raise ValueError

    data = res.json()

    balances: List[Balance] = []
    for record in data["payload"]["records"]:
        amount = _convert_wei_to_eth(float(record["amount"]))
        symbol = record["symbol"]
        if record["isERC20"] and float(amount) > 0:
            balances.append(Balance(symbol=symbol, amount=amount))
    return balances
