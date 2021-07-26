import React from 'react';
import './WalletContainer.css';
import { PieChart } from 'react-minimal-pie-chart';
import Typography from '@material-ui/core/Typography';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import { USDFormatter } from '../../lib/currencyConverters';


const getPieChartDataEntries = (asset) => {
    return ({title: asset.asset, value: parseFloat(asset.free) + parseFloat(asset.locked), color: asset.color});
}

const calculateEstimatedValue = (asset) => {
    // TODO Fetch price from API (could also be done in backend)
    const price = 10;
    return (parseFloat(asset.free) + parseFloat(asset.locked)) * price;
}

const generateListItem = (wallet) => {
    return (
        wallet.balances.map((asset, index) => {
            console.log(index)
            return (
                <ListItem key={index}>
                    <ListItemText
                        primary={asset.asset}
                        secondary={USDFormatter.format(asset.free)}
                    />
                </ListItem>
            )
        })
    )
}

const InteractiveList = ({ wallet }) => {

    return (
        <>
            <Typography variant="h6">
                Asset overview
            </Typography>
            <div>
                <List dense={false}>
                    {generateListItem(wallet)}
                </List>
            </div>
        </>
    );
}

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
                <InteractiveList wallet={wallet}/>
            </div>
            <div className='estimated-value text'>
                Estimated value: {USDFormatter.format(totalAmount)}
            </div>
        </div>
    )
}

export default WalletContainer;
