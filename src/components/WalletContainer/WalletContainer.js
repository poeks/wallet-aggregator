import React from 'react';
import './WalletContainer.css';
import { PieChart } from 'react-minimal-pie-chart';
import Typography from '@material-ui/core/Typography';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import { USDFormatter } from '../../lib/currencyConverters';


const defaultLabelStyle = {
    fontSize: '5px',
    fontFamily: 'sans-serif',
  };

const getRandomColor = () => {
    const maxColorNumber = 16777215;
    const color = Math.floor(Math.random() * maxColorNumber);
    return '#' + color.toString(16);
}

const getPieChartDataEntries = (asset) => {
    return ({title: asset.asset, value: asset.amount, color: getRandomColor()});
}

const calculateEstimatedValue = (asset) => {
    // TODO Fetch price from API (could also be done in backend)
    const price = 10;
    return asset.amount * price;
}

const sortAndGroupWalletAssets = (wallet) => {
    const assets = wallet.assets;
    assets.sort((a, b) => {
        return b.amount - a.amount;
    })
    const smallBalances = assets.splice(5);
    const smallBalancesAmount = smallBalances.reduce((acc, cur) => acc + cur.amount, 0);

    assets.push({asset: 'other', amount: smallBalancesAmount})
    return wallet
}

const generateListItems = (assets) => {

    return (
        assets.map((asset, index) => {
            return (
                <ListItem key={index}>
                    <ListItemText
                        primary={asset.asset}
                        secondary={USDFormatter.format(asset.amount)}
                    />
                </ListItem>
            )
        })
    )
}

const InteractiveList = ({wallet}) => {
    return (
        <>
            <Typography variant="h6">
                Asset overview
            </Typography>
            <div>
                <List dense={true} disablePadding={true}>
                    {generateListItems(wallet.assets)}
                </List>
            </div>
        </>
    );
}

const WalletContainer = ({wallet}) => {

    const totalAmount = wallet.assets.reduce((acc, cur) => acc + calculateEstimatedValue(cur), 0);
    const walletWithGroupedAssets = sortAndGroupWalletAssets(wallet);

    return (
        <div className='container'>
            <PieChart
                className='pie-chart'
                label={({dataEntry}) => {return Math.round(dataEntry.percentage) + '%'}}
                data={walletWithGroupedAssets.assets.map(asset => getPieChartDataEntries(asset))}
                animate={true}
                labelStyle={defaultLabelStyle}
            />
            <div className='origin text'>
                {walletWithGroupedAssets.origin}
            </div>
            <div className='list'>
                <InteractiveList wallet={walletWithGroupedAssets}/>
            </div>
            <div className='estimated-value text'>
                Estimated value: {USDFormatter.format(totalAmount)}
            </div>
        </div>
    )
}

export default WalletContainer;
