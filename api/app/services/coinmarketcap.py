from copy import deepcopy
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

import requests as r
from pydantic import BaseModel

from ..config import IncompleteCredentialsError
from ..config import Settings
from ..schemas import Balance
from ..schemas import QuotedBalance
from ..schemas import QuotedWallet
from ..schemas import Wallet

credentials = Settings().get_coinmarketcap_credentials()

COINMARKETCAP_HOST = "https://pro-api.coinmarketcap.com"

FIAT_SYMBOLS = {"EUR", "USD"}
UNKNOWN_ASSET_SYMBOLS = {"LDBNB"}


class _CoinMarketCapBaseItem(BaseModel):
    id: int
    name: str
    symbol: str
    slug: str


class CoinMarketCapPlatform(_CoinMarketCapBaseItem):
    token_address: str


class CoinMarketCapQuote(BaseModel):
    price: float
    market_cap: float


class CoinMarketCapAsset(_CoinMarketCapBaseItem):
    is_active: bool
    platform: Optional[CoinMarketCapPlatform] = None


class QuotedCoinMarketCapAsset(CoinMarketCapAsset):
    quote: Dict[str, CoinMarketCapQuote]


class CoinMarketCapMap(BaseModel):
    data: List[CoinMarketCapAsset]

    URL: ClassVar[str] = COINMARKETCAP_HOST + "/v1/cryptocurrency/map"

    def get_asset_ids(self) -> Set[int]:
        return {item.id for item in self.data}

    def get_symbol_id_map(self) -> Dict[str, int]:
        """Maps asset symbols to their CoinMarketCap id."""
        return {item.symbol: item.id for item in self.data}


class CoinMarketCapQuotes(BaseModel):

    URL: ClassVar[str] = COINMARKETCAP_HOST + "/v1/cryptocurrency/quotes/latest"

    data: Dict[str, QuotedCoinMarketCapAsset]  # Keys are asset ids.
    _symbol_asset_map: Dict[str, str]

    def __init__(self, **kwargs):
        # TODO think of a better place where to filter. Why did this came up in the first place, airdrop?
        kwargs["data"] = {
            id: quote
            for id, quote in kwargs["data"].items()
            if None not in quote["quote"]["USD"].values()
        }
        super().__init__(**kwargs)
        # if https://github.com/samuelcolvin/pydantic/pull/2625 is merged, ComputedField can be used
        object.__setattr__(
            self,
            "_symbol_asset_map",
            {asset.symbol: str(asset.id) for asset in self.data.values()},
        )

    def _get_price(self, symbol: str, target_currency: str = "USD") -> float:
        try:
            asset_id = self._symbol_asset_map[symbol]
            return self.data[asset_id].quote[target_currency].price
        except KeyError:
            raise ValueError(f"No quote available for {symbol}")

    def _get_quoted_balance(
        self, balance: Balance, target_currency: str = "USD"
    ) -> QuotedBalance:
        price = self._get_price(balance.symbol, target_currency)
        return QuotedBalance.from_balance(balance, price)

    def get_quoted_wallet(
        self, wallet: Wallet, target_currency: str = "USD"
    ) -> QuotedWallet:

        balances = [self._get_quoted_balance(balance) for balance in wallet.balances]

        return QuotedWallet(
            name=wallet.name,
            date=datetime.now(),  # TODO date of asset fetching and price fetching should be the same
            currency=target_currency,
            balances=balances,
        )


def _get_coinmarketcap_map(symbols: Set[str]) -> CoinMarketCapMap:
    params = {"symbol": ",".join(symbols)}
    res = r.get(CoinMarketCapMap.URL, params=params, headers=credentials.headers)
    return CoinMarketCapMap(**res.json())


def _get_asset_quotes(ids: Set[int]) -> CoinMarketCapQuotes:
    params = {"id": ",".join(map(str, ids))}
    res = r.get(CoinMarketCapQuotes.URL, params=params, headers=credentials.headers)
    return CoinMarketCapQuotes(**res.json())


def _filter_fiat_symbols(id_map: Dict[str, int]) -> Dict[str, int]:
    id_map = deepcopy(id_map)
    for fiat_symbol in FIAT_SYMBOLS:
        id_map.pop(fiat_symbol, None)
    return id_map


def get_quoted_wallet(wallet: Wallet) -> QuotedWallet:

    symbols = {
        balance.symbol
        for balance in wallet.balances
        if balance.symbol not in UNKNOWN_ASSET_SYMBOLS
    }
    coinmarketcap_map = _get_coinmarketcap_map(
        symbols
    )  # TODO might be done via a database lookup

    quotes = _get_asset_quotes(coinmarketcap_map.get_asset_ids())

    return quotes.get_quoted_wallet(wallet)


def health_check() -> Tuple[bool, str]:
    try:
        credentials = Settings().get_coinmarketcap_credentials()
    except IncompleteCredentialsError as e:
        return False, str(e)

    url = COINMARKETCAP_HOST + "/v1/key/info"
    res = r.get(url, headers=credentials.headers)

    if not res.ok:
        try:
            data = res.json()
        except JSONDecodeError:
            return False, f"Response from CoinMarketCap not ok ({res.reason})"
        return False, data["status"]["error_message"]

    data = res.json()["data"]
    usage = data["usage"]
    plan = data["plan"]

    requests_left = usage["current_minute"]["requests_left"]
    if requests_left == 0:
        limit = plan["rate_limit_minute"]
        return False, f"Minute rate limit exceded (limit = {limit})."

    day_credits_left = usage["current_day"]["credits_left"]
    if day_credits_left == 0:
        limit = plan["credit_limit_daily"]
        reset = plan["credit_limit_daily_reset"]
        return False, f"Day credits exceded (limit = {limit}). Reset {reset.lower()}"

    month_credits_exceeded = (
        usage["current_month"]["credits_used"] > usage["current_month"]["credits_left"]
    )
    if month_credits_exceeded:
        limit = plan["credit_limit_monthly"]
        reset = plan["credit_limit_monthly_reset"]
        return False, "Month credits exceded"

    return True, "ok"
