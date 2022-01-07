import React, { useState, useEffect } from 'react';
import './WalletFeed.css';
import WalletContainer from '../WalletContainer/WalletContainer';
import CircularProgress from '@material-ui/core/CircularProgress';

const fetchAndSetWalletData = async (setWallets) => {

    const url = '/wallets/current';
    const res = await fetch(url);
    const data = await res.json();
    setWallets(data.data);
}

const WalletFeed = () => {

    const [wallets, setWallets] = useState([]);

    useEffect(() => {
        try {
            fetchAndSetWalletData(setWallets);
        } catch (err) {
            console.log(err);
        }
    }, []
    )

    return (
        <div className="WalletFeed">
            {wallets.length > 0 ? wallets.map((wallet, index) => <WalletContainer key={index} wallet={wallet}/>) : <CircularProgress/>}
        </div>
    )
}

export default WalletFeed;
