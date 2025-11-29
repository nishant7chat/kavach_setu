/**
 * API Configuration
 * Central configuration for all API endpoints
 */

const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api/v1',

    // Customer endpoints
    CUSTOMER: {
        LOGIN: '/auth/customer/login',
        DASHBOARD: '/customer/dashboard',
        POLICIES: '/customer/policies',
        CLAIMS: '/customer/claims',
        CLAIM_DETAILS: '/customer/claims',
        SUBMIT_CLAIM: '/customer/claims/submit'
    },

    // Employee endpoints
    EMPLOYEE: {
        LOGIN: '/auth/employee/login',
        CLAIMS_FEED: '/claims/feed',
        CLAIM_DETAILS: '/claims',
        SUBMIT_DECISION: '/claims/{claim_id}/decision'
    },

    // Documents endpoints
    DOCUMENTS: {
        UPLOAD: '/documents/upload',
        VERIFICATION: '/documents/verification',
        DELETE: '/documents/{claim_id}/{document_type}',
        HEALTH: '/documents/health'
    },

    // Fraud detection endpoints
    FRAUD: {
        ANALYZE: '/fraud/{claim_id}/analyze',
        RESULT: '/fraud/{claim_id}/result'
    },

    // Hospital verification
    HOSPITAL: {
        VERIFY: '/hospital/verify'
    }
};

// Helper function to get full URL
function getApiUrl(endpoint, params = {}) {
    let url = API_CONFIG.BASE_URL + endpoint;

    // Replace path parameters
    for (const [key, value] of Object.entries(params)) {
        url = url.replace(`{${key}}`, value);
    }

    return url;
}

// Export for use in other scripts
window.API_CONFIG = API_CONFIG;
window.getApiUrl = getApiUrl;
