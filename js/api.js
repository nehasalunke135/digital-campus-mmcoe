/**
 * MMCOE Digital Campus - API Communication Layer
 * 
 * Modular HTTP client that communicates with the backend authentication API.
 * Handles tokens, headers, JSON serialization, and normalized error responses.
 */

class ApiClient {
    constructor() {
        // Use relative path for all web requests (development and production)
        // Fall back to http://127.0.0.1:8000 only if loaded directly via file:// protocol
        if (typeof window !== 'undefined' && window.location && window.location.protocol === 'file:') {
            this.baseUrl = 'http://127.0.0.1:8000/api';
        } else {
            this.baseUrl = '/api';
        }
        
        this.tokenKey = 'mmcoe_auth_token';
    }

    /**
     * Retrieve stored auth token
     */
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    /**
     * Store auth token
     */
    setToken(token) {
        if (token) {
            localStorage.setItem(this.tokenKey, token);
        } else {
            localStorage.removeItem(this.tokenKey);
        }
    }

    /**
     * Remove auth token
     */
    clearToken() {
        localStorage.removeItem(this.tokenKey);
    }

    /**
     * Read CSRF token from document.cookie if present
     */
    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Generic fetch wrapper with token injection and error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...(options.headers || {})
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Token ${token}`;
        }

        const csrfToken = this.getCsrfToken();
        const method = (options.method || 'GET').toUpperCase();
        if (csrfToken && method !== 'GET' && method !== 'HEAD') {
            headers['X-CSRFToken'] = csrfToken;
        }

        try {
            const response = await fetch(url, {
                credentials: 'same-origin',
                ...options,
                headers
            });

            const contentType = response.headers.get('content-type');
            let data = null;
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                let errorMsg = 'An unexpected error occurred.';
                if (data && typeof data === 'object') {
                    if (data.detail) {
                        errorMsg = data.detail;
                    } else if (data.error) {
                        errorMsg = data.error;
                    } else if (data.message) {
                        errorMsg = data.message;
                    } else if (data.non_field_errors) {
                        errorMsg = Array.isArray(data.non_field_errors) ? data.non_field_errors.join(' ') : data.non_field_errors;
                    } else {
                        // Extract first validation error without technical field prefixes
                        const firstKey = Object.keys(data)[0];
                        const firstVal = data[firstKey];
                        errorMsg = Array.isArray(firstVal) ? firstVal.join(' ') : `${firstVal}`;
                    }
                } else if (typeof data === 'string' && data) {
                    errorMsg = data;
                }

                return {
                    ok: false,
                    status: response.status,
                    error: errorMsg,
                    data
                };
            }

            return {
                ok: true,
                status: response.status,
                data
            };
        } catch (err) {
            return {
                ok: false,
                status: 0,
                error: 'Unable to reach the server. Please ensure the backend is running.',
                networkError: true
            };
        }
    }

    /**
     * Authenticate user with identifier (email or student ID) and password
     */
    async login(identifier, password) {
        return this.request('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ identifier, password })
        });
    }

    /**
     * Register a new student account
     */
    async register(userData) {
        return this.request('/auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    /**
     * Invalidate token and log out user
     */
    async logout() {
        const result = await this.request('/auth/logout/', {
            method: 'POST'
        });
        this.clearToken();
        return result;
    }

    /**
     * Retrieve currently authenticated user profile
     */
    async getCurrentUser() {
        return this.request('/auth/me/', {
            method: 'GET'
        });
    }

    /**
     * Test role-based authorization for Student
     */
    async testStudentEndpoint() {
        return this.request('/auth/student-only/', {
            method: 'GET'
        });
    }

    /**
     * Test role-based authorization for Admin
     */
    async testAdminEndpoint() {
        return this.request('/auth/admin-only/', {
            method: 'GET'
        });
    }
}

// Export singleton instance
window.apiClient = new ApiClient();
