from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Dict
from typing import List
from typing import Tuple

import requests as r

from ..config import IncompleteSettingsError
from ..config import Settings
from ..schemas import Balance
from ..schemas import Wallet

AMBERDATA_HOST = "https://web3api.io"


def get_ethereum_wallet() -> Wallet:
    """Gets the ETH and all ERC20 token balances of the wallet address"""
    s = Settings()
    credentials = s.get_amberdata_credentials()
    address = s.get_ethereum_wallet_address()

    balances: List[Balance] = []
    # Get ETH balance.
    balances.append(_get_ethereum_balance(address, headers=credentials.headers))

    # Get ERC20 tokens.
    tokens = _get_erc20_tokens_balances(address, headers=credentials.headers)
    balances.extend(tokens)

    return Wallet(name="Ethereum", date=datetime.now(), balances=balances)


def _convert_wei_to_eth(value: float) -> float:
    return value * 1e-18


def _get_ethereum_balance(address: str, headers: Dict[str, str]) -> Balance:
    url = AMBERDATA_HOST + f"/api/v2/addresses/{address}/account-balances/latest"
    res = r.get(url, headers=headers)
    if not res.ok:
        raise ValueError

    data = res.json()

    return Balance(
        symbol="ETH", amount=_convert_wei_to_eth(float(data["payload"]["value"]))
    )


def _get_erc20_tokens_balances(address: str, headers: Dict[str, str]) -> List[Balance]:
    url = AMBERDATA_HOST + f"/api/v2/addresses/{address}/token-balances/latest"
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


def health_check() -> Tuple[bool, str]:
    s = Settings()
    credentials = s.get_amberdata_credentials()

    try:
        s.get_coinmarketcap_credentials()
    except IncompleteSettingsError as e:
        return False, str(e)

    url = AMBERDATA_HOST + "/health"
    res = r.get(url, headers={})

    from pprint import pprint

    data = res.json()
    pprint(data)

    if not res.ok:
        return False, res.reason

    required_api = AMBERDATA_HOST + "/api/v2"
    for endpoint in data:
        if endpoint["baseUrl"] == required_api:
            if not endpoint["status"] == "up":
                return False, endpoint["status"]
            else:
                break
    else:
        return False, "API version not found"

    # /health does not check if the API key is valid.
    # Therefore, a random API point is talked to.
    url = "https://web3api.io/api/v2/blocks/0"  # Data of first mined Ethereum block.
    res = r.get(url, headers=credentials.headers)

    if not res.ok:
        if res.reason == "Forbidden":
            return False, "Access Forbidden: check API key"
        return False, "Response from AmberData not ok"

    return True, "ok"
