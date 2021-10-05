from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import Wallet, QuotedWallet, WalletsCurrent
from services.binance import get_binance_wallet
from services.coinmarketcap import get_quoted_wallet
app = FastAPI()

origins = [
		'http://localhost',
		'http://localhost:3000',
]

app.add_middleware(
		CORSMiddleware,
		allow_origins=origins
)

@app.get('/wallets')
def wallets():
	"""Returns an overview of activated exchange accounts and wallets"""
	payload = {'test': 'there should be walllet info here'}


@app.get('/wallets/current', response_model=WalletsCurrent)
def current_wallets() -> WalletsCurrent:
	wallet = get_binance_wallet()

	quoted_wallet = get_quoted_wallet(wallet)

	return WalletsCurrent(data=[quoted_wallet])
