import axios from 'axios';

// Create an instance of axios with the base URL
const api = axios.create({
    baseURL: 'http://localhost:8000', // Change this to your FastAPI backend URL
});

// Export the Axios instance
export default api;