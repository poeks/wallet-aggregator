from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import date


class Balance(BaseModel):
    symbol: str = Field(..., description='Symbol refering to the asset, based on CoinMarketCap symbol.')
    amount: float = Field(..., description='Amount of the token balance.')


class Wallet(BaseModel):
    name: str = Field(..., description='Name of the wallet.')
    date: date
    balances: List[Balance] = Field(..., description='List of balances')


class QuotedBalance(Balance):
    price: float = Field(..., description='Unit price')
    value: float = Field(None, description='Value of the balance (amount * unit price)')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # if https://github.com/samuelcolvin/pydantic/pull/2625 is merged, ComputedField can be used
        object.__setattr__(self, 'value', self.amount * self.price)

    @classmethod
    def from_balance(cls, balance: Balance, price: float) -> 'QuotedBalance':
        return cls(**balance.dict(), price=price)


class QuotedWallet(Wallet):
    currency: str = Field(..., description='Currency following ISO 8601 currency code')
    balances: List[QuotedBalance]

    class Config:
        """
        Prevent changes in balances so total value will not get affected.
        Create a new object if balances are to be updated.
        """
        allow_mutation = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # if https://github.com/samuelcolvin/pydantic/pull/2625 is merged, ComputedField can be used
        # TODO see if properties can be included in serialization of Pydantic models.
        object.__setattr__(self, 'total_value', sum(balance.value for balance in self.balances))


class WalletsCurrent(BaseModel):
    data: List[QuotedWallet] = Field(..., description='Collection of wallets (can be actual wallet addresses or exchange wallets).')

    class Config:
        schema_extra = {
            "example": {
                "data": [
                    {
                    "name": "Binance",
                    "date": "2021-10-05",
                    "currency": "USD",
                    "balances": [
                        {
                        "symbol": "BTC",
                        "amount": 0.10,
                        "price": 50000,
                        "value": 5000
                        },
                        {
                        "symbol": "USDC",
                        "amount": 2000,
                        "price": 1,
                        "value": 2000
                        },
                    ],
                    "total_value": 7000
                    }
                ]
                
            }
        }
