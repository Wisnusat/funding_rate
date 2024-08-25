
const baseUrl = 'https://deep-flss-suryalab-9cf66ab5.koyeb.app';

export const API_CONFIG = {
    endpoints: {
        auth: `${baseUrl}/api/auth/`,
        register: `${baseUrl}/api/user/`,
        allCoin: (page, limit, time, keyword) => `${baseUrl}/api/funding-rates/aggregated-funding?page=${page}&limit=${limit}&time=${time}&keyword=${keyword}`,
        coinList: (keyword) => `${baseUrl}/api/funding-rates/coins?keyword=${keyword}`,
        detailCoin: (coin) => `https://api.coingecko.com/api/v3/coins/${coin}`,
        // Add other endpoints as needed
    }
};
