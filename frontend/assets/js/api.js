/**
 * API Helper Functions
 * Centralized API calling with error handling
 */

// Make API call with authentication
async function apiCall(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            ...auth.getAuthHeader()
        },
        cache: 'no-store'
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };

    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();

        if (!response.ok) {
            // Handle 401 Unauthorized
            if (response.status === 401) {
                showError('Session expired. Please login again.');
                auth.logout();
                return null;
            }

            throw new Error(data.detail || data.message || 'API request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Show loading spinner
function showLoading(message = 'Loading...') {
    const existing = document.getElementById('loading-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

// Hide loading spinner
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.remove();
}

// Show success message
function showSuccess(message) {
    showToast(message, 'success');
}

// Show error message
function showError(message) {
    showToast(message, 'error');
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 100);

    // Remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(amount);
}

// Get risk level badge HTML
function getRiskBadge(riskLevel) {
    const badges = {
        low: '<span class="badge badge-success">Low Risk</span>',
        medium: '<span class="badge badge-warning">Medium Risk</span>',
        high: '<span class="badge badge-danger">High Risk</span>'
    };
    return badges[riskLevel?.toLowerCase()] || '<span class="badge badge-secondary">Unknown</span>';
}

// Get status badge HTML
function getStatusBadge(status) {
    const badges = {
        'pending_documents': '<span class="badge badge-info">Pending Documents</span>',
        'submitted': '<span class="badge badge-info">Submitted</span>',
        'under_review': '<span class="badge badge-warning">Under Review</span>',
        'approved': '<span class="badge badge-success">Approved</span>',
        'rejected': '<span class="badge badge-danger">Rejected</span>',
        'escalated': '<span class="badge badge-warning">Escalated</span>'
    };
    return badges[status] || '<span class="badge badge-secondary">' + status + '</span>';
}

// Export to window
window.api = {
    call: apiCall,
    showLoading,
    hideLoading,
    showSuccess,
    showError,
    showToast
};

window.utils = {
    formatDate,
    formatCurrency,
    getRiskBadge,
    getStatusBadge
};
