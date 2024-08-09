import {
    API_CONFIG
} from './apiConfig.js';

const login = async (username, password) => {
    try {
        const response = await fetch(API_CONFIG.endpoints.auth, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                password
            })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        return error;
    }
};

const register = async (username, password) => {
    try {
        const response = await fetch(API_CONFIG.endpoints.register, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                password
            })
        });
        if (!response.ok) {
            return response.json();
        }
        const data = await response.json();
        return data;
    } catch (error) {
        return error;
    }
};

const fetchAevo = async (page, limit, time, keyword) => {
    const token = getCookie('token'); // Ambil token dari cookie

    try {
        const response = await fetch(API_CONFIG.endpoints.aevo(page, limit, time, keyword), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Menambahkan token pada header
            },
        });

        if (!response.ok) {
            return response.json();
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return error;
    }
};

const fetchHyperliquid = async (page, limit, time, keyword) => {
    const token = getCookie('token'); // Ambil token dari cookie

    try {
        const response = await fetch(API_CONFIG.endpoints.hyperliquid(page, limit, time, keyword), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Menambahkan token pada header
            },
        });

        if (!response.ok) {
            return response.json();
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return error;
    }
};

const fetchBybit = async (page, limit, time, keyword) => {
    const token = getCookie('token'); // Ambil token dari cookie

    try {
        const response = await fetch(API_CONFIG.endpoints.bybit(page, limit, time, keyword), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Menambahkan token pada header
            },
        });

        if (!response.ok) {
            return response.json();
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return error;
    }
};

const fetchGateio = async (page, limit, time, keyword) => {
    const token = getCookie('token'); // Ambil token dari cookie

    try {
        const response = await fetch(API_CONFIG.endpoints.gateio(page, limit, time, keyword), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Menambahkan token pada header
            },
        });

        if (!response.ok) {
            return response.json();
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return error;
    }
};

const fetchTickers = async (page, limit, time, keyword) => {
    const token = getCookie('token'); // Ambil token dari cookie

    try {
        const response = await fetch(API_CONFIG.endpoints.tickers(page, limit, time, keyword), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Menambahkan token pada header
            },
        });

        if (!response.ok) {
            return response.json();
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        return error;
    }
};

const fetchDetailCoin = async (coin) => {
    try {
        const response = await fetch(API_CONFIG.endpoints.detailCoin(coin), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Error fetching data: ${response.status} ${response.statusText}`, errorData);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching coin details:', error);
        return { error: true, message: error.message };
    }
};

export {
    login,
    register,
    fetchAevo,
    fetchHyperliquid,
    fetchGateio,
    fetchBybit,
    fetchTickers,
    fetchDetailCoin,
};