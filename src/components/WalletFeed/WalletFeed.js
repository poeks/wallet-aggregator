import React from 'react';
import WalletContainer from '../WalletContainer/WalletContainer';


const mockWalletData1 = {
    origin: 'Binance',
    balances: [
        {
           "asset":"BTC",
           "free":"0.09905021",
           "locked":"0.00000000",
           "color": "#E38627",
        },
        {
           "asset":"USDT",
           "free":"1.89109409",
           "locked":"0.00000000",
           "color": "#C13C37",
        }
     ]
  }


const mockWalletData2 = {
    origin: 'Kucoin',
    balances: [
        {
            "asset":"BTC",
            "free":"0.16",
            "locked":"0.00000000",
            "color": "#E38627",
        },
        {
            "asset":"ETH    ",
            "free":"5.89109409",
            "locked":"0.00000000",
            "color": "#918686",
        }
    ]
}


const WalletFeed = () => {

  const walletData = [mockWalletData1, mockWalletData2];

    return (
        <div>
            {walletData.map((wallet, index) => <WalletContainer key={index} wallet={wallet}/>)}
        </div>
    )
}

export default WalletFeed;
