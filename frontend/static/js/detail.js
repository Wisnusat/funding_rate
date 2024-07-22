document.addEventListener('DOMContentLoaded', () => {
    const coinData = [
        { rank: 1, coin: "Bitcoin BTC", logo: "https://cryptologos.cc/logos/bitcoin-btc-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 2, coin: "Ethereum ETH", logo: "https://cryptologos.cc/logos/ethereum-eth-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 3, coin: "Cardano ADA", logo: "https://cryptologos.cc/logos/cardano-ada-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 4, coin: "Binance BNB", logo: "https://cryptologos.cc/logos/binance-coin-bnb-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 5, coin: "Tether USDT", logo: "https://cryptologos.cc/logos/tether-usdt-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 6, coin: "XRP XRP", logo: "https://cryptologos.cc/logos/xrp-xrp-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 7, coin: "Polkadot DOT", logo: "https://cryptologos.cc/logos/polkadot-new-dot-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" }
    ];

    const chartWrapper = document.getElementById("chart-section");

    // Function to get URL parameters
    const getUrlParameter = (name) => {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    };

    const coinSymbol = getUrlParameter('coin') || 'BTC'; // Default to BTC if no parameter is provided

    // Find the coin data based on the abbreviation
    const coin = coinData.find(c => c.coin.includes(coinSymbol));

    if (coin) {
        const [name, abbreviation] = coin.coin.split(' ');

        // Update the header with the coin data
        document.querySelector('.crypto-logo').src = coin.logo;
        document.querySelector('.crypto-logo').alt = `${name} Logo`;
        document.querySelector('.crypto-details h1').innerHTML = `${name} <span class="badge">${abbreviation}</span>`;
        // You can update other details like price and percentage change if needed
    } else {
        console.error('Coin not found');
    }

    const renderChart = () => {
        chartWrapper.innerHTML = `
            <div class="tradingview-widget-container" style="height:100%;width:100%">
                <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
            </div>
        `;

        const script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
        script.async = true;
        script.innerHTML = JSON.stringify({
            "autosize": true,
            "symbol": `CRYPTOCAP:${coinSymbol}`,
            "interval": "D",
            "timezone": "Etc/UTC",
            "theme": "light",
            "style": "1",
            "locale": "ja",
            "allow_symbol_change": true,
            "calendar": false,
            "support_host": "https://www.tradingview.com"
        });

        chartWrapper.querySelector('.tradingview-widget-container').appendChild(script);
    };

    renderChart();
});
