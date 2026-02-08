import axios from 'axios';

// Create an axios instance with a dynamic base URL
// In development, Vite proxy handles '/predict' -> 'http://localhost:8000/predict'
// In production, we need the full URL from environment variables
const baseURL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
    baseURL: baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;
