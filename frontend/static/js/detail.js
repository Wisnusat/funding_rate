document.addEventListener('DOMContentLoaded', () => {
    const chartWrapper = document.getElementById("chart-section");

    // Function to get URL parameters
    const getUrlParameter = (name) => {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    };

    const coinSymbol = getUrlParameter('coin') || 'BTC'; // Default to BTC if no parameter is provided

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
