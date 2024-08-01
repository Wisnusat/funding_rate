import {
    API_CONFIG
} from './apiConfig.js';

const fetchData = async (endpoint) => {
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
};

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
    console.log("feching...");
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

export {
    fetchData,
    login,
    register,
    fetchAevo,
};