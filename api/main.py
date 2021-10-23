from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import IncompleteSettingsError
from schemas import QuotedWallet
from schemas import Wallet
from schemas import WalletsCurrent
from services.binance import get_binance_wallet
from services.celsius import get_celsius_wallet
from services.coinmarketcap import get_quoted_wallet
from services.ethereum import get_ethereum_wallet
from services.kucoin import get_kucoin_wallet

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(CORSMiddleware, allow_origins=origins)


@app.get("/wallets")
def wallets():
    """Returns an overview of activated exchange accounts and wallets"""
    payload = {"test": "there should be walllet info here"}


@app.get("/wallets/current", response_model=WalletsCurrent)
def current_wallets() -> WalletsCurrent:

    wallets = (
        get_binance_wallet(),
        get_kucoin_wallet(),
        get_ethereum_wallet(),
        get_celsius_wallet(),
    )

    quoted_wallets = []
    for wallet in wallets:
        try:
            quoted_wallets.append(get_quoted_wallet(wallet))
        except IncompleteSettingsError:
            continue

    quoted_wallets = [get_quoted_wallet(wallet) for wallet in wallets]

    return WalletsCurrent(data=quoted_wallets)
