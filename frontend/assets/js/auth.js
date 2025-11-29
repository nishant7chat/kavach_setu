/**
 * Authentication Helper Functions
 * Handles token storage, retrieval, and validation
 */

// Store auth token
function saveToken(token, userType = 'customer') {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user_type', userType);
}

// Get auth token
function getToken() {
    return localStorage.getItem('auth_token');
}

// Get user type
function getUserType() {
    return localStorage.getItem('user_type') || 'customer';
}

// Save user info
function saveUserInfo(userInfo) {
    localStorage.setItem('user_info', JSON.stringify(userInfo));
}

// Get user info
function getUserInfo() {
    const userInfo = localStorage.setItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getToken();
}

// Logout user
function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_type');
    localStorage.removeItem('user_info');
    window.location.href = '/frontend/index.html';
}

// Get authorization header
function getAuthHeader() {
    const token = getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// Redirect to login if not authenticated
function requireAuth(redirectUrl = null) {
    if (!isAuthenticated()) {
        const userType = getUserType();
        const loginPage = userType === 'employee'
            ? '/frontend/insurer/login.html'
            : '/frontend/customer/login.html';

        if (redirectUrl) {
            localStorage.setItem('redirect_after_login', redirectUrl);
        }

        window.location.href = loginPage;
        return false;
    }
    return true;
}

// Handle post-login redirect
function handlePostLoginRedirect(defaultUrl) {
    const redirectUrl = localStorage.getItem('redirect_after_login');
    if (redirectUrl) {
        localStorage.removeItem('redirect_after_login');
        window.location.href = redirectUrl;
    } else {
        window.location.href = defaultUrl;
    }
}

// Export functions
window.auth = {
    saveToken,
    getToken,
    getUserType,
    saveUserInfo,
    getUserInfo,
    isAuthenticated,
    logout,
    getAuthHeader,
    requireAuth,
    handlePostLoginRedirect
};
