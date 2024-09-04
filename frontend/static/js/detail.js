import {
    fetchDetailCoin
} from "../../config/apiService.js";

document.addEventListener("DOMContentLoaded", () => {
    const chartWrapper = document.getElementById("chart-section");

    const getUrlParameter = (name, defaultValue = '') => {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name) || defaultValue;
    };

    const coinSymbol = getUrlParameter('coin', 'BTC');
    const coinName = getUrlParameter('name', 'BTC');

    const renderChart = (symbol) => {
        const tradingViewConfig = {
            autosize: true,
            symbol: `${symbol}USDT`,
            interval: "D",
            timezone: "Etc/UTC",
            theme: "light",
            style: "1",
            locale: "ja",
            allow_symbol_change: true,
            calendar: false,
            support_host: "https://www.tradingview.com"
        };

        chartWrapper.innerHTML = `
            <div class="tradingview-widget-container" style="height:100%;width:100%">
                <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
            </div>
        `;

        const script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
        script.async = true;
        script.innerHTML = JSON.stringify(tradingViewConfig);

        chartWrapper.querySelector('.tradingview-widget-container').appendChild(script);
    };

    const updateCoinDetails = (coin, logo) => {
        if (coin) {
            document.getElementById('crypto-title').textContent = coin;
        }

        if (logo) {
            const logoElement = document.getElementById('crypto-logo');
            logoElement.src = logo;
            logoElement.alt = `${coin} Logo`;
        }
    };

    const coin = getUrlParameter('coin');
    const logo = getUrlParameter('logo');

    updateCoinDetails(coin, logo);
    renderChart(coinSymbol);

    const renderDetailData = (data) => {
        const price = `$${data.market_data.current_price.usd.toLocaleString()}`;
        const marketCap = `$${data.market_data.market_cap.usd.toLocaleString()}`;
        const volume = `$${data.market_data.total_volume.usd.toLocaleString()}`;
        const circulatingSupply = `${data.market_data.circulating_supply.toLocaleString()} ${coin}`;
        const totalSupply = `${data.market_data.total_supply.toLocaleString()} ${coin}`;
        const marketCapRank = `#${data.market_data.market_cap_rank}`;
        const ath = `$${data.market_data.ath.usd.toLocaleString()}`;
        const atl = `$${data.market_data.atl.usd.toLocaleString()}`;

        document.getElementById("price").innerText = price;
        document.getElementById("market-cap").innerText = marketCap;
        document.getElementById("volume").innerText = volume;
        document.getElementById("circulating-supply").innerText = circulatingSupply;
        document.getElementById("total-supply").innerText = totalSupply;
        document.getElementById("market-cap-rank").innerText = marketCapRank;
        document.getElementById("ath").innerText = ath;
        document.getElementById("atl").innerText = atl;
    }

    const renderDetailFailed = (error) => {
        console.error("Error fetching coin data:", error);
        // In case of any other errors, display "-"
        document.getElementById("price").innerText = "-";
        document.getElementById("market-cap").innerText = "-";
        document.getElementById("volume").innerText = "-";
        document.getElementById("circulating-supply").innerText = "-";
        document.getElementById("total-supply").innerText = "-";
        document.getElementById("market-cap-rank").innerText = "-";
        document.getElementById("ath").innerText = "-";
        document.getElementById("atl").innerText = "-";
    }

    fetchDetailCoin(coinName)
        .then(data => renderDetailData(data))
        .catch(error => renderDetailFailed(error));
});