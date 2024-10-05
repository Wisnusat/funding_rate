import { fetchCoin, fetchCoinList } from "../../config/apiService.js";

const loadingContainer = document.getElementById('loadingContainer');
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
const coinSearchDropdown = document.getElementById('coinSearchDropdown');
const dropdownOptions = document.getElementById('dropdownOptions');
const dropdownLoading = document.getElementById('dropdownLoading');
const calculateLoading = document.getElementById('calculateLoading');
const calculateButton = document.querySelector('.calculate-button');

let currentTimeFilter = '1h'; // Default time filter
let searchQuery = ''; // Default search query
let currentPage = 1;
const limitPerPage = 20;
let isFetching = false;
let allCoinData = []; // Store all fetched data
let isNextPageAvailable = true; // Flag to check if there are more pages to fetch
let abortController = null;
let requestId = 0;

const showErrorNotification = (message) => {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.add('show');
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000); // Hide after 3 seconds
};

const formatToFourDecimalPlaces = (numberString) => {
    const number = parseFloat(numberString);
    const parts = numberString.split('.');
    if (parts.length > 1 && parts[1].length > 4) {
        return number.toFixed(4);
    }
    return numberString;
};

const renderFundRate = (rate) => {
    if (rate !== null && rate !== undefined) {
        const icon = rate.includes('-') ? CHEVRON_RED : CHEVRON_GREEN;
        return `<img src="/frontend/assets/icon/loading-placeholder.png" data-src="${icon}" alt="${rate.includes('-') ? 'Down' : 'Up'}" class="chevron-icon lazy"> ${formatToFourDecimalPlaces(rate)}%`;
    }
    return '-';
};

const calculateAverage = (values) => {
    const validValues = values.filter(value => value !== null && value !== undefined).map(parseFloat);
    if (validValues.length === 0) return '-';
    const sum = validValues.reduce((acc, value) => acc + value, 0);
    return (sum / validValues.length).toFixed(5);
};

const renderTableRow = (coin, funding) => {
    const average = calculateAverage([funding.aevo, funding.hyperliquid, funding.bybit, funding.gateio]);
    return `
        <tr onclick="window.location.href='/detail.html?name=${coin.name ? coin.name.toLowerCase() : 'none'}&coin=${coin.coin}&logo=${coin.logo}'" style="cursor:pointer;">
            <td class="sticky-col">
                <img src="/assets/icon/loading-placeholder.png" data-src="${coin.logo}" class="coin-logo lazy">
                ${coin.coin}
            </td>
            <td class="${average !== '-' && average.includes('-') ? 'down' : average !== '-' ? 'up' : ''}">${renderFundRate(average)}</td>
            <td class="${funding.aevo !== null && funding.aevo.includes('-') ? 'down' : funding.aevo !== null ? 'up' : ''}">${renderFundRate(funding.aevo)}</td>
            <td class="${funding.bybit !== null && funding.bybit.includes('-') ? 'down' : funding.bybit !== null ? 'up' : ''}">${renderFundRate(funding.bybit)}</td>
            <td class="${funding.gateio !== null && funding.gateio.includes('-') ? 'down' : funding.gateio !== null ? 'up' : ''}">${renderFundRate(funding.gateio)}</td>
            <td class="${funding.hyperliquid !== null && funding.hyperliquid.includes('-') ? 'down' : funding.hyperliquid !== null ? 'up' : ''}">${renderFundRate(funding.hyperliquid)}</td>
        </tr>
    `;
};

const renderTable = (data) => {
    tableBody.innerHTML = data.map(({ coin, funding }) => renderTableRow(coin, funding)).join('');
    lazyLoadImages(); // Lazy load images after rendering new data
    repositionSentinel(); // Ensure the sentinel is correctly positioned
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
    window.location.href = '/login.html'; // Redirect to the login page
};

const setupEventListeners = () => {
    timeFilters.forEach(button => button.addEventListener('click', () => {
        isNextPageAvailable = true;
        toggleActiveClass(timeFilters, button);
        currentTimeFilter = button.textContent == '1M' ? '1M' : button.textContent.toLocaleLowerCase(); // Update current time filter
        refreshData(); // Refresh data when the time filter is changed
    }));

    hamburgerMenu.addEventListener('click', openDrawer);
    closeDrawerButton.addEventListener('click', closeDrawerAndOverlay);
    overlay.addEventListener('click', closeDrawerAndOverlay);
    logoutLink.addEventListener('click', logout);

    searchBarMobile.addEventListener('input', () => {
        isNextPageAvailable = true;
        debounce(() => {
            searchQuery = searchBarMobile.value;
            allCoinData = [];
            currentPage = 1;
            if (searchQuery) {
                filterAndRenderData(); // Filter and render data when the search query changes
            } else {
                isNextPageAvailable = true;
                refreshData(); // Refresh data if search query is cleared
            }
        }, 300); // Debounce delay of 300ms
    });
    
    searchBarDesktop.addEventListener('input', () => {
        isNextPageAvailable = true;
        debounce(() => {
            searchQuery = searchBarDesktop.value;
            allCoinData = [];
            currentPage = 1;
            if (searchQuery) {
                filterAndRenderData(); // Filter and render data when the search query changes
            } else {
                refreshData(); // Refresh data if search query is cleared
            }
        }, 300); // Debounce delay of 300ms
    });

    refreshButton.addEventListener('click', refreshData);
};

const fetchAndRenderCoinData = async () => {
    // Abort the previous API call if it's still in progress
    if (abortController) {
        abortController.abort();
    }

    // Create a new AbortController instance for the new request
    abortController = new AbortController();

    if (isFetching || !isNextPageAvailable) return;

    // Increment the request ID to track the current request
    const currentRequestId = ++requestId;

    // Show the loading spinner
    loadingSpinner.style.display = 'block';
    loadingContainer.style.visibility = 'visible';
    isFetching = true;

    try {
        // Fetch ticker data for the current page
        const tickerData = await fetchCoin(currentPage, limitPerPage, currentTimeFilter, searchQuery, abortController.signal);

        // If the current request is no longer the latest one, do nothing
        if (currentRequestId !== requestId) return;

        if (tickerData.error) {
            throw new Error(tickerData.error); // Handle errors
        }

        // Check if there are more pages to fetch
        if (!tickerData.meta || !tickerData.meta.isNextPage) {
            isNextPageAvailable = false;
        }

        // Process the fetched data
        const coinData = tickerData.data.map((coin) => ({
            coin: {
                coin: coin.coin,
                logo: coin.logo,
                name: coin.name
            },
            funding: coin.funding
        }));

        // Append the new coin data to the existing array
        allCoinData = allCoinData.concat(coinData);

        // Render the full data to the table
        renderTable(allCoinData);

        // Increment the page number for the next fetch
        currentPage++;
    } catch (error) {
        // Only show an error notification if it's not an AbortError
        if (error.name !== 'AbortError') {
            showErrorNotification("Error fetching data. Please try again.");
        }
    } finally {
        // If the current request is no longer the latest one, do nothing
        if (currentRequestId !== requestId) return;

        // Hide the spinner and reset isFetching if this is the latest request
        isFetching = false;
        loadingSpinner.style.display = 'none';
        loadingContainer.style.visibility = 'hidden';
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

// Function to handle smooth and slower scrolling
const smoothScrollHandler = (event) => {
    event.preventDefault(); // Prevent the default scroll behavior

    // Adjust the scroll sensitivity factor
    const scrollSensitivity = 0.5; // Decrease this value to make scrolling slower

    // Calculate the new scroll position
    const scrollAmount = event.deltaY * scrollSensitivity;

    // Use requestAnimationFrame for smooth scrolling
    const scrollElement = document.querySelector('.table-container');
    let start = null;

    const step = (timestamp) => {
        if (!start) start = timestamp;
        const progress = timestamp - start;
        const scrollStep = Math.min(progress / 10, scrollAmount); // Adjust the divisor for smoothness

        scrollElement.scrollTop += scrollStep;

        if (progress < 200) { // Adjust the duration for smoothness
            requestAnimationFrame(step);
        }
    };

    requestAnimationFrame(step);
};

// Add the smooth scroll handler to the table container
document.querySelector('.table-container').addEventListener('wheel', smoothScrollHandler);

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
                if (isNextPageAvailable) {
                    console.log("Sentinel is intersecting, fetching more data...");
                    fetchAndRenderCoinData();
                }
            }, 200); // Debounce delay of 200ms
        }
    });
}, observerOptions);

const refreshData = () => {
    isNextPageAvailable = true;
    isFetching = false;
    currentPage = 1;
    allCoinData = []; // Clear existing data
    tableBody.innerHTML = '';
    fetchAndRenderCoinData();
};

// Function to filter and render data based on search query
const filterAndRenderData = () => {
    const filteredData = allCoinData.filter(({ coin }) => coin.coin.toLowerCase().includes(searchQuery.toLowerCase()));
    renderTable(filteredData);
};

// Global variable to track sort state
let sortState = {
    column: 'coin',
    order: 'asc'
};

// Function to compare values for sorting
const compareValues = (key, order = 'asc') => {
    return function(a, b) {
        let aValue, bValue;

        if (key === 'average') {
            aValue = calculateAverage([a.funding.aevo, a.funding.hyperliquid, a.funding.bybit, a.funding.gateio]);
            bValue = calculateAverage([b.funding.aevo, b.funding.hyperliquid, b.funding.bybit, b.funding.gateio]);
        } else if (key !== 'coin') {
            aValue = a.funding[key] === null || a.funding[key] === '-' ? null : parseFloat(a.funding[key]);
            bValue = b.funding[key] === null || b.funding[key] === '-' ? null : parseFloat(b.funding[key]);
        } else {
            aValue = a.coin[key] === null || a.coin[key] === '-' ? null : a.coin[key];
            bValue = b.coin[key] === null || b.coin[key] === '-' ? null : b.coin[key];
        }

        // Handle null or "-" values to always be at the bottom
        if (aValue === null && bValue === null) return 0;
        if (aValue === null) return 1;
        if (bValue === null) return -1;

        let comparison = 0;
        if (aValue > bValue) comparison = 1;
        else if (aValue < bValue) comparison = -1;

        return (order === 'desc') ? (comparison * -1) : comparison;
    };
};

// Function to sort data and render table
const sortAndRenderData = () => {
    const sortedData = [...allCoinData].sort(compareValues(sortState.column, sortState.order));
    renderTable(sortedData);
};

// Event listeners for sorting
const setupSortEventListeners = () => {
    const sortableHeaders = document.querySelectorAll('.sortable');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            if (sortState.column === column) {
                sortState.order = sortState.order === 'asc' ? 'desc' : 'asc';
            } else {
                sortState.column = column;
                sortState.order = 'asc';
            }
            sortAndRenderData(); // Sort and render data with the new sort state
        });
    });
};

// Function to update the current local time in the footer
const updateLocalTime = () => {
    const localTimeElement = document.getElementById('currentLocalTime');
    if (localTimeElement) {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const seconds = now.getSeconds().toString().padStart(2, '0');
        localTimeElement.textContent = `${hours}:${minutes}:${seconds}`;
    }
};

// Call the function to set the initial time
updateLocalTime();

// Update the time every second
setInterval(updateLocalTime, 1000);

document.addEventListener("DOMContentLoaded", () => {
    displayUsername();
    setupEventListeners();
    setupSortEventListeners();
    fetchAndRenderCoinData();
    repositionSentinel(); // Initialize sentinel

    // Initial call to update the time
    updateLocalTime();
    // Set interval to update the time every second
    setInterval(updateLocalTime, 1000);
});

// Modal Logic

// Get the modal
const modal = document.getElementById("arbitrageModal");

// Get the button that opens the modal
const btn = document.getElementById("arbitrageTrigger");

// Get the <span> element that closes the modal
const span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal
btn.onclick = function() {
    modal.classList.add("show");
    setTimeout(() => modal.style.display = "block", 50); // Slight delay to allow transition
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.classList.remove("show");
    setTimeout(() => modal.style.display = "none", 300); // Delay hiding the modal until transition ends
    document.getElementById('amount').value = "";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.classList.remove("show");
        setTimeout(() => modal.style.display = "none", 300); // Delay hiding the modal until transition ends
        document.getElementById('amount').value = "";
    }
}

// Function to populate dropdown options
const populateDropdownOptions = (coins) => {
    dropdownOptions.innerHTML = ''; // Clear existing options

    if (coins.length === 0) {
        dropdownOptions.style.display = 'none'; // Hide options if no coins are found
        return;
    }

    coins.forEach(coin => {
        const option = document.createElement('div');
        option.className = 'option';
        option.dataset.value = coin.coin; // Store the coin ID in a data attribute
        option.dataset.coinId = coin.coin; // Store the coin ID in a data attribute
        option.innerText = coin.coin;

        option.addEventListener('click', () => {
            coinSearchDropdown.value = coin.coin; // Set input value to the selected option
            coinSearchDropdown.dataset.selectedCoinId = coin.coin; // Store selected coin ID in input dataset
            dropdownOptions.style.display = 'none'; // Hide options
        });

        dropdownOptions.appendChild(option);
    });

    dropdownOptions.style.display = 'block'; // Show options if there are results
};

// Function to fetch and filter coins based on input
const fetchAndFilterCoins = async (keyword) => {
    try {
        dropdownLoading.style.display = 'inline-block'; // Show loading spinner
        const data = await fetchCoinList(keyword);
        if (data) {
            populateDropdownOptions(data);
        } else {
            showErrorNotification("No coins found.");
            dropdownOptions.style.display = 'none'; // Hide dropdown if no data is returned
        }
    } catch (error) {
        console.error("Error fetching coin list:", error);
        showErrorNotification("Error fetching coin list. Please try again.");
        dropdownOptions.style.display = 'none'; // Hide dropdown if an error occurs
    } finally {
        dropdownLoading.style.display = 'none'; // Hide loading spinner
    }
};

// Event listener to handle input changes with your debouncing
coinSearchDropdown.addEventListener('input', () => {
    debounce(async () => {
        const keyword = coinSearchDropdown.value.trim();
        if (keyword.length >= 2) { // Fetch only if the user has entered 2 or more characters
            await fetchAndFilterCoins(keyword);
        } else {
            dropdownOptions.style.display = 'none'; // Hide dropdown if input is cleared
        }
    }, 300); // Debounce delay of 300ms
});

// Hide dropdown if clicked outside
document.addEventListener('click', (event) => {
    if (!coinSearchDropdown.contains(event.target) && !dropdownOptions.contains(event.target)) {
        dropdownOptions.style.display = 'none';
    }
});

// Show dropdown if input is focused and has value
coinSearchDropdown.addEventListener('focus', () => {
    if (coinSearchDropdown.value.trim().length >= 2) {
        dropdownOptions.style.display = 'block';
    }
});

// Arbitrage Calculation Logic
document.getElementById('arbitrageForm').addEventListener('submit', async function(event) {
    document.getElementById('result').innerText = '';
    event.preventDefault();

    const exchangeA = document.getElementById('exchangeA').value;
    const exchangeB = document.getElementById('exchangeB').value;
    const coinId = coinSearchDropdown.dataset.selectedCoinId;
    const amount = parseFloat(document.getElementById('amount').value);
    const time = document.getElementById('timeInterval').value;

    if (!coinId) {
        showErrorNotification("Please select a coin.");
        return;
    }

    try {
        calculateButton.classList.add('disabled'); // Disable the button
        calculateLoading.style.display = 'inline-block'; // Show loading spinner

        // Fetch the funding rates for the selected coin
        const data = await fetchCoin(1, 1, time, coinId);
        const selectedCoin = data.data[0];

        if (!selectedCoin || !selectedCoin.funding) {
            showErrorNotification('Funding rate data not available for the selected coin.');
            return;
        }

        const fundingRateA = parseFloat(selectedCoin.funding[exchangeA] || 0);
        const fundingRateB = parseFloat(selectedCoin.funding[exchangeB] || 0);

        const cumulativeFundingRate = fundingRateA + fundingRateB;
        const result = cumulativeFundingRate * amount;

        document.getElementById('result').innerText = `Estimated Arbitrage Profit: $${result.toFixed(2)}`;
    } catch (error) {
        console.error("Error fetching funding rates:", error);
        showErrorNotification("Error fetching funding rates. Please try again.");
    } finally {
        calculateButton.classList.remove('disabled'); // Re-enable the button
        calculateLoading.style.display = 'none'; // Hide loading spinner
    }
});