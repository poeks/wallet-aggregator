import React, { useState } from 'react';
import { PieChart } from 'react-minimal-pie-chart';
import _ from 'lodash';
import './WalletContainer.css';
import Typography from '@material-ui/core/Typography';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Checkbox from '@material-ui/core/Checkbox';
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
    return ({title: asset.symbol, value: asset.value, color: getRandomColor()});
}

const groupSmallBalances = (assets) => {
    const newAssets = _.cloneDeep(assets);
    const splitIndex = newAssets.findIndex(asset => asset.value < 10);
    if (splitIndex === -1) {
        return newAssets;
    }
    const smallBalances = newAssets.splice(splitIndex);
    const smallBalancesAmount = smallBalances.reduce((acc, cur) => acc + cur.value, 0);
    newAssets.push({symbol: 'Other', value: smallBalancesAmount})
    return newAssets;
}

const generateListItems = (assets) => {

    return (
        assets.map((asset, index) => {
            return (
                <ListItem key={index}>
                    <ListItemText
                        primary={asset.symbol}
                        secondary={USDFormatter.format(asset.value)}
                    />
                </ListItem>
            )
        })
    )
}

const InteractiveList = ({assets, onCheckBoxClick}) => {
    return (
        <>
            <Typography variant="h6">
                Asset overview
            </Typography>
            <div className='checkbox-container'>
                <Checkbox onChange={onCheckBoxClick}/>
                <Typography variant="subtitle2">
                    Show small balances
                </Typography>
            </div>
            <div>
                <List className='list' dense={true} disablePadding={true}>
                    {generateListItems(assets)}
                </List>
            </div>
        </>
    );
}

const WalletContainer = ({wallet}) => {

    const [showSmallBalances, setShowSmallBalances] = useState(false);

    const onCheckBoxClick = (event) => {
        console.log(event.target.checked)
        setShowSmallBalances(event.target.checked);
    }

    const totalAmount = wallet.assets.reduce((acc, asset) => acc + asset.value, 0);
    const assets = showSmallBalances ? wallet.assets : groupSmallBalances(wallet.assets);

    return (
        <div className='container'>
            <PieChart
                className='pie-chart'
                label={({dataEntry}) => {return Math.round(dataEntry.percentage) + '%'}}
                data={assets.map(asset => getPieChartDataEntries(asset))}
                animate={true}
                labelStyle={defaultLabelStyle}
                labelPosition={110}
            />
            <div className='origin text'>
                {wallet.origin}
            </div>
            <div className='list-container'>
                <InteractiveList assets={assets} onCheckBoxClick={onCheckBoxClick}/>
            </div>
            <div className='estimated-value text'>
                Estimated value: {USDFormatter.format(totalAmount)}
            </div>
        </div>
    )
}

export default WalletContainer;
