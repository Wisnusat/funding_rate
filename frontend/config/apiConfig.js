const baseUrl =  'https://deep-flss-suryalab-9cf66ab5.koyeb.app';

export const API_CONFIG = {
    endpoints: {
        coinData: '/api/coins',
        auth: `${baseUrl}/api/auth/`,
        register: `${baseUrl}/api/user/`,
        aevo: (page, limit, time, keyword) => `${baseUrl}/api/funding-rates/aevo?page=${page}&limit=${limit}&time=${time}&keyword=${keyword}`,
        hyperliquid: (page, limit, time, keyword) => `${baseUrl}/api/funding-rates/hyperliquid?page=${page}&limit=${limit}&time=${time}&keyword=${keyword}`,
        bybit: (page, limit, time, keyword) => `${baseUrl}/api/funding-rates/bybit?page=${page}&limit=${limit}&time=${time}&keyword=${keyword}`,
        gateio: (page, limit, time, keyword) => `${baseUrl}/api/funding-rates/gateio?page=${page}&limit=${limit}&time=${time}&keyword=${keyword}`,
        tickers: (page, limit, time, keyword) => `${baseUrl}/api/funding-rates/tickers?page=${page}&limit=${limit}&time=${time}&keyword=${keyword}`,
        // Add other endpoints as needed
    }
};
