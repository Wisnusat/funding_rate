import {
    fetchAevo,
    fetchGateio,
    fetchHyperliquid,
    fetchTickers,
    fetchBybit,
} from "../../config/apiService.js";

const loadingSpinner = document.getElementById('loadingSpinner');
const CHEVRON_GREEN = '/frontend/assets/icon/chevron-green.png';
const CHEVRON_RED = '/frontend/assets/icon/chevron-red.png';
const tableBody = document.getElementById('coinTableBody');
const refreshButton = document.querySelector('.refresh-button');
const searchBarMobile = document.getElementById('searchBarMobile');
const searchBarDesktop = document.getElementById('searchBarDesktop');
const timeFilters = document.querySelectorAll('.time-filter');
const hamburgerMenu = document.getElementById('hamburger-menu');
const drawer = document.getElementById('drawer');
const overlay = document.getElementById('overlay');
const closeDrawerButton = document.getElementById('close-drawer');
const logoutLink = document.getElementById('logoutLink');

let currentTimeFilter = '1h'; // Default time filter
let searchQuery = ''; // Default search query
let currentPage = 1;
const limitPerPage = 20;
let isFetching = false;

const formatToFiveDecimalPlaces = (numberString) => {
    const number = parseFloat(numberString);
    const parts = numberString.split('.');
    if (parts.length > 1 && parts[1].length > 5) {
        return number.toFixed(5);
    }
    return numberString;
};

const renderFundRate = (rate) => {
    if (rate !== 'None') {
        const icon = rate.includes('-') ? CHEVRON_RED : CHEVRON_GREEN;
        return `<img src="/frontend/assets/icon/loading-placeholder.png" data-src="${icon}" alt="${rate.includes('-') ? 'Down' : 'Up'}" class="chevron-icon lazy"> ${formatToFiveDecimalPlaces(rate)}`;
    }
    return '-';
};

const calculateAverage = (values) => {
    const validValues = values.filter(value => value !== 'None').map(parseFloat);
    if (validValues.length === 0) return 'None';
    const sum = validValues.reduce((acc, value) => acc + value, 0);
    return (sum / validValues.length).toFixed(5);
};

const renderTableRow = (coin, aevo, hyperliquid, bybit) => {
    const average = calculateAverage([aevo, bybit, hyperliquid]);

    return `
        <tr onclick="window.location.href='/frontend/detail.html?coin=${coin.coin}&logo=${coin.logo}'" style="cursor:pointer;">
            <td class="sticky-col">
                <img src="/frontend/assets/icon/loading-placeholder.png" data-src="${coin.logo}" class="coin-logo lazy">
                ${coin.coin}
            </td>
            <td class="${average !== 'None' && average.includes('-') ? 'down' : average !== 'None' ? 'up' : ''}">${renderFundRate(average)}</td>
            <td class="${aevo !== 'None' && aevo.includes('-') ? 'down' : 'up'}">${renderFundRate(aevo)}</td>
            <td class="${bybit !== 'None' && bybit.includes('-') ? 'down' : 'up'}">${renderFundRate(bybit)}</td>
            <td class="${"-0.65".includes('-') ? 'down' : 'up'}">${renderFundRate("-0.65")}</td>
            <td class="${hyperliquid !== 'None' && hyperliquid.includes('-') ? 'down' : 'up'}">${renderFundRate(hyperliquid)}</td>
        </tr>
    `;
};

const renderTable = (data, aevo, hyperliquid, bybit) => {
    tableBody.innerHTML += data.map((coin, index) => renderTableRow(coin, aevo[index], hyperliquid[index], bybit[index])).join('');
    lazyLoadImages(); // Lazy load images after rendering new data
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

const setupEventListeners = () => {
    timeFilters.forEach(button => button.addEventListener('click', () => {
        toggleActiveClass(timeFilters, button);
        currentTimeFilter = button.textContent.toLocaleLowerCase(); // Update current time filter
        refreshData(); // Refresh data when the time filter is changed
    }));

    hamburgerMenu.addEventListener('click', openDrawer);
    closeDrawerButton.addEventListener('click', closeDrawerAndOverlay);
    overlay.addEventListener('click', closeDrawerAndOverlay);
    logoutLink.addEventListener('click', logout);

    searchBarMobile.addEventListener('input', () => {
        debounce(() => {
            searchQuery = searchBarMobile.value;
            refreshData(); // Refresh data when the search query changes
        }, 300); // Debounce delay of 300ms
    });

    searchBarDesktop.addEventListener('input', () => {
        debounce(() => {
            searchQuery = searchBarDesktop.value;
            refreshData(); // Refresh data when the search query changes
        }, 300); // Debounce delay of 300ms
    });

    refreshButton.addEventListener('click', refreshData);
};

const fetchAndRenderCoinData = async () => {
    if (isFetching) return;
    isFetching = true;
    loadingSpinner.style.display = 'block'; // Show the loading spinner

    try {
        // Fetch all data concurrently
        const [data, aevo, hyperliquid, bybit] = await Promise.all([
            fetchTickers(currentPage, limitPerPage, currentTimeFilter, searchQuery),
            fetchAevo(currentPage, limitPerPage, currentTimeFilter, searchQuery),
            fetchHyperliquid(currentPage, limitPerPage, currentTimeFilter, searchQuery),
            fetchBybit(currentPage, limitPerPage, currentTimeFilter, searchQuery)
        ]);

        loadingSpinner.style.display = 'none'; // Hide the loading spinner

        // Check if data exists and render the table
        if (data && data.data && data.data.length > 0) {
            renderTable(data.data, aevo.data, hyperliquid.data, bybit.data);
            currentPage++;
            repositionSentinel();
        }
    } catch (error) {
        console.error("Error fetching data:", error);
        loadingSpinner.style.display = 'none'; // Hide the loading spinner in case of error
    } finally {
        isFetching = false;
    }
};

const repositionSentinel = () => {
    let sentinel = document.getElementById('sentinel');
    if (sentinel) {
        tableBody.removeChild(sentinel);
    }
    sentinel = document.createElement('tr');
    sentinel.setAttribute('id', 'sentinel');
    tableBody.appendChild(sentinel);
    observer.observe(sentinel);
};

const observerOptions = {
    root: document.querySelector('.table-container'),
    rootMargin: '0px',
    threshold: 1.0
};

const lazyLoadImages = () => {
    const images = document.querySelectorAll('img.lazy');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(image => {
        imageObserver.observe(image);
    });
};

let debounceTimer;
const debounce = (callback, delay) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(callback, delay);
};

const observer = new IntersectionObserver(async (entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !isFetching) {
            debounce(() => {
                console.log("Sentinel is intersecting, fetching more data...");
                fetchAndRenderCoinData();
            }, 200); // Debounce delay of 200ms
        }
    });
}, observerOptions);

const refreshData = () => {
    currentPage = 1;
    tableBody.innerHTML = '';
    fetchAndRenderCoinData();
};

document.addEventListener("DOMContentLoaded", () => {
    displayUsername();
    setupEventListeners();
    fetchAndRenderCoinData();
});
