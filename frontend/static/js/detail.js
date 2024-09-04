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
        const coinData = data[coinSymbol];
        const marketCap = coinData.self_reported_market_cap || "-";
        const circulatingSupply = `${coinData.self_reported_circulating_supply || "-"} ${coinData.self_reported_circulating_supply ? coinSymbol : ''}`; // 'APT' or other dynamic coin symbol
        const dateAdded = new Date(coinData.date_added).toLocaleDateString() || "-"; // Formatting date of when coin was added
        const website = coinData.urls.website[0] || "-"; // Official website URL
        const description = coinData.description || "-";


        document.getElementById("market-cap").innerText = marketCap;
        document.getElementById("circulating-supply").innerText = circulatingSupply;
        document.getElementById("date-added").innerText = dateAdded;
        document.getElementById("website").innerText = website;
        document.getElementById("description").innerText = description || "-";
    }

    const renderDetailFailed = (error) => {
        console.error("Error fetching coin data:", error);
        document.getElementById("market-cap").innerText = "-";
        document.getElementById("circulating-supply").innerText = "-";
        document.getElementById("date-added").innerText = "-";
        document.getElementById("website").innerText = "-";
        document.getElementById("description").innerText = "-";
    }

    fetchDetailCoin(coinSymbol)
        .then(data => renderDetailData(data))
        .catch(error => renderDetailFailed(error));
});