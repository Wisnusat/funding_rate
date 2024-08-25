// Function to get a cookie value by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Function to check if the user is authenticated
function checkAuth() {
    const token = getCookie('token');
    if (!token) {
        window.location.href = '/login.html'; // Redirect to the login page if not authenticated
    }
}

// Function to delete a cookie by name
function deleteCookie(name) {
    document.cookie = name + '=; Max-Age=0; path=/; domain=' + window.location.hostname;
}

// Function to log the user out
function logout() {
    deleteCookie('token'); // Delete the authentication token cookie
    window.location.href = '/login.html'; // Redirect to the login page
}

// Call checkAuth on page load
document.addEventListener('DOMContentLoaded', checkAuth);
