export const API_CONFIG = {
    baseUrl: 'https://your-api-domain.com',
    endpoints: {
        coinData: '/api/coins',
        auth: 'http://shiny-adelaida-suryalab-d961bd87.koyeb.app/api/auth/',
        register: 'http://shiny-adelaida-suryalab-d961bd87.koyeb.app/api/user/',
        aevo: (page, limit) => `http://shiny-adelaida-suryalab-d961bd87.koyeb.app/api/funding-rates/aevo?page=${page}&limit=${limit}&time=1h`,
        // Add other endpoints as needed
    }
};
