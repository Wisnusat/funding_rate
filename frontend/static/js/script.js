document.addEventListener('DOMContentLoaded', () => {
    const COIN_DATA = [
        { rank: 1, coin: "Bitcoin BTC", logo: "https://cryptologos.cc/logos/bitcoin-btc-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 2, coin: "Ethereum ETH", logo: "https://cryptologos.cc/logos/ethereum-eth-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 3, coin: "Cardano ADA", logo: "https://cryptologos.cc/logos/cardano-ada-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 4, coin: "Binance BNB", logo: "https://cryptologos.cc/logos/binance-coin-bnb-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 5, coin: "Tether USDT", logo: "https://cryptologos.cc/logos/tether-usdt-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 6, coin: "XRP XRP", logo: "https://cryptologos.cc/logos/xrp-xrp-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" },
        { rank: 7, coin: "Polkadot DOT", logo: "https://cryptologos.cc/logos/polkadot-new-dot-logo.png", average: "-0.65%", hyperliquid: "-0.65%", aevo: "0.65%", bybit: "-0.65%", gateio: "0.65%" }
    ];
    const CHEVRON_GREEN = '/frontend/assets/icon/chevron-green.png';
    const CHEVRON_RED = '/frontend/assets/icon/chevron-red.png';
    const tableBody = document.getElementById('coinTableBody');

    const renderFundRate = (rate) => {
        const icon = rate.includes('-') ? CHEVRON_RED : CHEVRON_GREEN;
        return `<img src="${icon}" alt="${rate.includes('-') ? 'Down' : 'Up'}" class="chevron-icon"> ${rate}`;
    };

    const renderTableRow = (coin) => {
        const [name, abbreviation] = coin.coin.split(' ');
        return `
            <tr onclick="window.location.href='/frontend/detail.html?coin=${abbreviation}'" style="cursor:pointer;">
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
    };

    const renderTable = (data) => {
        tableBody.innerHTML = data.map(renderTableRow).join('');
    };

    const toggleActiveClass = (buttons, activeButton) => {
        buttons.forEach(button => button.classList.remove('active'));
        activeButton.classList.add('active');
    };

    const getCookie = (name) => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        return parts.length === 2 ? parts.pop().split(';').shift() : null;
    };

    const decodeToken = (token) => jwt_decode(token);

    const displayUsername = () => {
        const token = getCookie('token');
        if (token) {
            const { username } = decodeToken(token); // Assuming the token contains a 'username' field
            const usernameDisplayElements = document.querySelectorAll('#usernameDisplay');
            usernameDisplayElements.forEach(element => {
                element.textContent = `${username}!`;
            });
        }
    };

    const openDrawer = () => {
        drawer.classList.add('open');
        overlay.classList.add('open');
    };

    const closeDrawerAndOverlay = () => {
        drawer.classList.remove('open');
        overlay.classList.remove('open');
    };

    const logout = (event) => {
        event.preventDefault(); // Prevent the default link behavior
        document.cookie = 'token=; Max-Age=0; path=/; domain=' + window.location.hostname; // Delete the authentication token cookie
        window.location.href = '/frontend/login.html'; // Redirect to the login page
    };

    // Render table on page load
    renderTable(COIN_DATA);

    // Setup time filter buttons
    const timeFilters = document.querySelectorAll('.time-filter');
    timeFilters.forEach(button => button.addEventListener('click', () => toggleActiveClass(timeFilters, button)));

    // Setup drawer menu
    const hamburgerMenu = document.getElementById('hamburger-menu');
    const drawer = document.getElementById('drawer');
    const overlay = document.getElementById('overlay');
    const closeDrawerButton = document.getElementById('close-drawer');
    hamburgerMenu.addEventListener('click', openDrawer);
    closeDrawerButton.addEventListener('click', closeDrawerAndOverlay);
    overlay.addEventListener('click', closeDrawerAndOverlay);

    // Setup logout link
    document.getElementById('logoutLink').addEventListener('click', logout);

    // Display username on page load
    displayUsername();
});
