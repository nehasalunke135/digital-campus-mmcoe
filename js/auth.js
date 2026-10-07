/**
 * MMCOE Digital Campus - Authentication & State Management Layer
 * 
 * Manages client authentication state, token persistence, user profiles,
 * and role-based access checks. UI independent.
 */

class AuthService {
    constructor(api) {
        this.api = api;
        this.userStorageKey = 'mmcoe_user_data';
        this.currentUser = null;
        this.listeners = [];
        this.initialized = false;
    }

    /**
     * Subscribe to authentication state changes
     */
    onAuthStateChanged(callback) {
        this.listeners.push(callback);
        // If already initialized, call callback immediately with current user
        if (this.initialized) {
            callback(this.currentUser);
        }
        return () => {
            this.listeners = this.listeners.filter(cb => cb !== callback);
        };
    }

    /**
     * Notify all registered listeners of auth state changes
     */
    _notifyListeners() {
        for (const callback of this.listeners) {
            try {
                callback(this.currentUser);
            } catch (e) {
                console.error('Error in auth state listener:', e);
            }
        }
    }

    /**
     * Initialize auth state from local storage and verify with backend
     */
    async init() {
        const token = this.api.getToken();
        const cachedUserJson = localStorage.getItem(this.userStorageKey);

        if (token && cachedUserJson) {
            try {
                this.currentUser = JSON.parse(cachedUserJson);
            } catch (e) {
                this.currentUser = null;
            }
        }

        // Verify with backend
        if (token) {
            const result = await this.api.getCurrentUser();
            if (result.ok && result.data) {
                this.setCurrentUser(result.data);
            } else if (result.status === 401) {
                // Stale token, clear session
                this.clearAuth();
            }
        } else {
            this.clearAuth();
        }

        this.initialized = true;
        this._notifyListeners();
        return this.currentUser;
    }

    /**
     * Save authenticated user and token
     */
    setCurrentUser(user, token = null) {
        this.currentUser = user;
        if (user) {
            localStorage.setItem(this.userStorageKey, JSON.stringify(user));
        } else {
            localStorage.removeItem(this.userStorageKey);
        }
        if (token) {
            this.api.setToken(token);
            localStorage.setItem('interx_token', token);
        }
        this._notifyListeners();
    }

    /**
     * Clear auth data
     */
    clearAuth() {
        this.currentUser = null;
        this.api.clearToken();
        localStorage.removeItem(this.userStorageKey);
        localStorage.removeItem('interx_token');
        this._notifyListeners();
    }

    /**
     * Authenticate with email or student ID and password
     */
    async login(identifier, password) {
        const result = await this.api.login(identifier, password);
        if (result.ok && result.data) {
            const { token, user } = result.data;
            this.setCurrentUser(user, token);
            return { ok: true, user };
        }
        return { ok: false, error: result.error || 'Authentication failed' };
    }

    /**
     * Register a new student account
     */
    async register(fullName, email, password, passwordConfirm) {
        const result = await this.api.register({
            full_name: fullName,
            email: email,
            password: password,
            password_confirm: passwordConfirm
        });
        if (result.ok && result.data) {
            return { ok: true, user: result.data.user, token: result.data.token, message: result.data.message };
        }
        return { ok: false, error: result.error || 'Registration failed' };
    }

    /**
     * Log out current user
     */
    async logout() {
        try {
            await this.api.logout();
        } catch (e) {
            // Even if network fails, ensure local auth is cleared
        } finally {
            this.clearAuth();
        }
    }

    /**
     * Get currently cached user
     */
    getUser() {
        return this.currentUser;
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return Boolean(this.currentUser && this.api.getToken());
    }

    /**
     * Get verified user role from backend profile (never trusted from unverified source)
     */
    getRole() {
        return this.currentUser ? this.currentUser.role : null;
    }

    /**
     * Check if user is a student
     */
    isStudent() {
        return this.getRole() === 'STUDENT';
    }

    /**
     * Check if user is an admin
     */
    isAdmin() {
        return this.getRole() === 'ADMIN';
    }

    /**
     * Check if user has one of the allowed roles
     */
    hasAnyRole(allowedRoles = []) {
        if (!this.isAuthenticated()) return false;
        return allowedRoles.includes(this.getRole());
    }
}

// Export singleton instance
window.authService = new AuthService(window.apiClient);
