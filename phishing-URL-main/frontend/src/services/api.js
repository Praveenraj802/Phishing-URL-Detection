/**
 * API Service for URL Scanning
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Scan a URL for phishing
 * @param {string} url - The URL to scan
 * @returns {Promise} - Scanner response
 */
export const scanURL = async (url) => {
    try {
        const response = await api.post('/scan-url', { url });
        return response.data;
    } catch (error) {
        if (error.response) {
            throw new Error(error.response.data.detail || error.response.data.message || 'Scan failed');
        } else if (error.request) {
            throw new Error('Unable to connect to server. Please ensure the backend is running.');
        } else {
            throw new Error('An unexpected error occurred');
        }
    }
};

/**
 * Check API health
 * @returns {Promise} - Health status
 */
export const checkHealth = async () => {
    try {
        const response = await api.get('/health');
        return response.data;
    } catch (error) {
        throw new Error('Health check failed');
    }
};

/**
 * Submit feedback
 * @param {Object} feedbackData - Feedback data
 * @returns {Promise} - Feedback response
 */
export const submitFeedback = async (feedbackData) => {
    try {
        const response = await api.post('/feedback', feedbackData);
        return response.data;
    } catch (error) {
        throw new Error('Failed to submit feedback');
    }
};

export default api;
