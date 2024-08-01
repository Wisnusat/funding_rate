const baseUrl =  'https://1bfb-36-85-74-78.ngrok-free.app';

export const API_CONFIG = {
    endpoints: {
        coinData: '/api/coins',
        auth: `${baseUrl}/api/auth/`,
        register: `${baseUrl}/api/user/`,
        aevo: (page, limit, time, keyword) => `${baseUrl}/api/funding-rates/aevo?page=${page}&limit=${limit}&time=${time}&keyword=${keyword}`,
        // Add other endpoints as needed
    }
};
