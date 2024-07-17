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

    const chevronGreen = '/assets/icon/chevron-green.png';
    const chevronRed = '/assets/icon/chevron-red.png';

    const tableBody = document.getElementById('coinTableBody');

    const renderTable = (data) => {
        tableBody.innerHTML = data.map(coin => {
            const [name, abbreviation] = coin.coin.split(' ');

            const renderFundRate = (rate) => {
                const icon = rate.includes('-') ? chevronRed : chevronGreen;
                return `<img src="${icon}" alt="${rate.includes('-') ? 'Down' : 'Up'}" class="chevron-icon"> ${rate}`;
            };

            return `
                <tr>
                    <td>${coin.rank}</td>
                    <td class="sticky-col">
                        <img src="${coin.logo}" alt="${coin.coin} logo" class="coin-logo"> 
                        ${name} <span class="badge">${abbreviation}</span>
                    </td>
                    <td class="${coin.average.includes('-') ? 'down' : 'up'}">${renderFundRate(coin.average)}</td>
                    <td class="${coin.hyperliquid.includes('-') ? 'down' : 'up'}">${renderFundRate(coin.hyperliquid)}</td>
                    <td class="${coin.aevo.includes('-') ? 'down' : 'up'}">${renderFundRate(coin.aevo)}</td>
                    <td class="${coin.bybit.includes('-') ? 'down' : 'up'}">${renderFundRate(coin.bybit)}</td>
                    <td class="${coin.gateio.includes('-') ? 'down' : 'up'}">${renderFundRate(coin.gateio)}</td>
                </tr>
            `;
        }).join('');
    };

    renderTable(coinData);

    const timeFilters = document.querySelectorAll('.time-filter');
    timeFilters.forEach(button => {
        button.addEventListener('click', () => {
            timeFilters.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });

    const hamburgerMenu = document.getElementById('hamburger-menu');
    const drawer = document.getElementById('drawer');
    const overlay = document.getElementById('overlay');
    const closeDrawer = document.getElementById('close-drawer');

    const openDrawer = () => {
        drawer.classList.add('open');
        overlay.classList.add('open');
    };

    const closeDrawerAndOverlay = () => {
        drawer.classList.remove('open');
        overlay.classList.remove('open');
    };

    hamburgerMenu.addEventListener('click', openDrawer);
    closeDrawer.addEventListener('click', closeDrawerAndOverlay);
    overlay.addEventListener('click', closeDrawerAndOverlay);
});
