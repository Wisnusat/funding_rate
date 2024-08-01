export const API_CONFIG = {
    baseUrl: 'https://your-api-domain.com',
    endpoints: {
        coinData: '/api/coins',
        auth: 'https://1bfb-36-85-74-78.ngrok-free.app/api/auth/',
        register: 'https://1bfb-36-85-74-78.ngrok-free.app/api/user/',
        aevo: (page, limit) => `https://1bfb-36-85-74-78.ngrok-free.app/api/funding-rates/aevo?page=${page}&limit=${limit}&time=1h`,
        // Add other endpoints as needed
    }
};
