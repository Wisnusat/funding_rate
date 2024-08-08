const baseUrl = 'https://1771-2001-448a-50e1-a0-edbb-bbac-cd34-f4c3.ngrok-free.app';

export const API_CONFIG = {
    endpoints: {
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
