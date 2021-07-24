import React from 'react';
import { PieChart } from 'react-minimal-pie-chart';
import './WalletContainer.css';


const getPieChartDataEntries = (asset) => {
    return ({title: asset.asset, value: parseFloat(asset.free) + parseFloat(asset.locked), color: asset.color});
}

const calculateEstimatedValue = (asset) => {
    // TODO Fetch price from API (could also be done in backend)
    const price = 10;
    return (parseFloat(asset.free) + parseFloat(asset.locked)) * price;
}

const USDFormatter = new Intl.NumberFormat('en-US', {style: 'currency', currency: 'USD'});

const WalletContainer = ({wallet}) => {
    
    const totalAmount = wallet.balances.reduce((acc, cur) => acc + calculateEstimatedValue(cur), 0);

    return (
        <div className='container'>
            <PieChart
                className='pie-chart'
                label={({dataEntry}) => {return Math.round(dataEntry.percentage) + '%'}}
                data={wallet.balances.map(asset => getPieChartDataEntries(asset))}
            />
            <div className='origin text'>
                {wallet.origin}
            </div>
            <div className='list'>
                <ol>
                    {wallet.balances.map(asset => <li>{asset.asset}</li>)}
                </ol>
            </div>
            <div className='estimated-value text'>
                Estimated value: {USDFormatter.format(totalAmount)}
            </div>
        </div>
    )
}

export default WalletContainer;
