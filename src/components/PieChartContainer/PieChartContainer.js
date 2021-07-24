import React from 'react';
import { PieChart } from 'react-minimal-pie-chart';


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
            "asset":"USDT",
            "free":"5.89109409",
            "locked":"0.00000000",
            "color": "#C13C37",
        }
    ]
}


const getPieChartDataEntries = (asset) => {
    console.log('asset: ', asset)
    return ({title: asset.asset, value: parseFloat(asset.free) + parseFloat(asset.locked), color: asset.color});
}


const PieChartContainer = () => {

  const walletData = [mockWalletData1, mockWalletData2];

    return (
        <div>
            {walletData.map(wallet => {
                console.log('wallet: ', wallet)
                return (
                    <div>
                        <PieChart
                        style={{height: '300px'}}
                        label={({dataEntry}) => {return Math.round(dataEntry.percentage) + '%'}}
                        data={wallet.balances.map(asset => getPieChartDataEntries(asset))}
                        />
                        {wallet.origin}
                    </div>

                )
            }
            )
            }

        </div>

    )

}

export default PieChartContainer;
