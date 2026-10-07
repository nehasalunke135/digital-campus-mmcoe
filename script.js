/**
 * MMCOE Digital Campus - UI Controller (Phase 2 Foundation)
 * 
 * Strictly manages DOM rendering, view switching, and role-based UI reflections.
 * All authentication logic, network calls, and token management remain cleanly
 * decoupled in `window.authService` and `window.apiClient`.
 */

document.addEventListener("DOMContentLoaded", function () {
    // ----------------------------------------------------
    // 1. DOM REFERENCES
    // ----------------------------------------------------
    // Login Elements
    const loginPage = document.getElementById("loginPage");
    const dashboard = document.getElementById("dashboard");
    const loginForm = document.getElementById("loginForm");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const loginSubmitBtn = document.getElementById("loginSubmitBtn");
    const loginBtnText = document.getElementById("loginBtnText");
    const loginBtnArrow = document.getElementById("loginBtnArrow");
    const errorMessage = document.getElementById("errorMessage");

    // Registration Elements
    const registerForm = document.getElementById("registerForm");
    const regFullNameInput = document.getElementById("regFullName");
    const regEmailInput = document.getElementById("regEmail");
    const regPasswordInput = document.getElementById("regPassword");
    const regPasswordConfirmInput = document.getElementById("regPasswordConfirm");
    const regSubmitBtn = document.getElementById("regSubmitBtn");
    const regBtnText = document.getElementById("regBtnText");
    const regBtnArrow = document.getElementById("regBtnArrow");
    const regErrorMessage = document.getElementById("regErrorMessage");
    const regSuccessMessage = document.getElementById("regSuccessMessage");

    // Auth Switcher & Card Elements
    const authBadgeText = document.getElementById("authBadgeText");
    const authTitle = document.getElementById("authTitle");
    const authSubtitle = document.getElementById("authSubtitle");
    const toggleToRegister = document.getElementById("toggleToRegister");
    const toggleToLogin = document.getElementById("toggleToLogin");
    const showRegisterLink = document.getElementById("showRegisterLink");
    const showLoginLink = document.getElementById("showLoginLink");
    const demoSection = document.getElementById("demoSection");

    // Quick Test Buttons
    const demoAdminBtn = document.getElementById("demoAdminBtn");
    const demoStudentABtn = document.getElementById("demoStudentABtn");
    const demoStudentBBtn = document.getElementById("demoStudentBBtn");

    // Navigation & Identity Controls
    const logoutBtn = document.getElementById("logoutBtn");
    const userAvatar = document.getElementById("userAvatar");
    const sidebarName = document.getElementById("sidebarName");
    const sidebarRole = document.getElementById("sidebarRole");
    const topbarPortalSubtitle = document.getElementById("topbarPortalSubtitle");
    const topbarRoleBadge = document.getElementById("topbarRoleBadge");
    const welcomeName = document.getElementById("welcomeName");
    const welcomeSubtitle = document.getElementById("welcomeSubtitle");

    // Backend Auth Status & API Verification
    const authStatusRole = document.getElementById("authStatusRole");
    const authStatusUser = document.getElementById("authStatusUser");
    const authStatusId = document.getElementById("authStatusId");
    const testStudentApiBtn = document.getElementById("testStudentApiBtn");
    const testAdminApiBtn = document.getElementById("testAdminApiBtn");
    const apiTestResult = document.getElementById("apiTestResult");

    // ----------------------------------------------------
    // 2. UI UTILITY FUNCTIONS
    // ----------------------------------------------------
    function setLoading(isLoading) {
        if (isLoading) {
            loginSubmitBtn.disabled = true;
            loginBtnText.textContent = "Authenticating...";
            if (loginBtnArrow) loginBtnArrow.style.display = "none";
        } else {
            loginSubmitBtn.disabled = false;
            loginBtnText.textContent = "Sign In to Portal";
            if (loginBtnArrow) loginBtnArrow.style.display = "inline";
        }
    }

    function showError(message) {
        if (!errorMessage) return;
        errorMessage.textContent = message || "";
        if (message) {
            errorMessage.style.display = "block";
            errorMessage.style.opacity = "1";
        } else {
            errorMessage.style.display = "none";
            errorMessage.style.opacity = "0";
        }
    }

    function setRegLoading(isLoading) {
        if (!regSubmitBtn) return;
        if (isLoading) {
            regSubmitBtn.disabled = true;
            if (regBtnText) regBtnText.textContent = "Creating Account...";
            if (regBtnArrow) regBtnArrow.style.display = "none";
        } else {
            regSubmitBtn.disabled = false;
            if (regBtnText) regBtnText.textContent = "Create Account";
            if (regBtnArrow) regBtnArrow.style.display = "inline";
        }
    }

    function showRegError(message) {
        if (!regErrorMessage) return;
        regErrorMessage.textContent = message || "";
        if (message) {
            regErrorMessage.style.display = "block";
            regErrorMessage.style.opacity = "1";
        } else {
            regErrorMessage.style.display = "none";
            regErrorMessage.style.opacity = "0";
        }
    }

    function showRegSuccess(message) {
        if (!regSuccessMessage) return;
        regSuccessMessage.textContent = message || "";
        if (message) {
            regSuccessMessage.style.display = "block";
            regSuccessMessage.style.opacity = "1";
        } else {
            regSuccessMessage.style.display = "none";
            regSuccessMessage.style.opacity = "0";
        }
    }

    function showLoginForm(updateUrl = true) {
        if (loginForm) loginForm.classList.remove("hidden");
        if (registerForm) registerForm.classList.add("hidden");
        if (toggleToRegister) toggleToRegister.classList.remove("hidden");
        if (toggleToLogin) toggleToLogin.classList.add("hidden");
        if (demoSection) demoSection.classList.remove("hidden");
        if (authTitle) authTitle.innerHTML = 'Portal Sign In<span>.</span>';
        if (authSubtitle) authSubtitle.textContent = 'Enter your Student ID or official email address to access your profile.';
        if (authBadgeText) authBadgeText.textContent = 'UNIFIED AUTHENTICATION';
        showError("");
        showRegError("");
        showRegSuccess("");
        if (updateUrl && typeof window !== 'undefined' && window.history && window.location.pathname !== '/' && window.location.pathname !== '/login/') {
            window.history.pushState({ page: 'login' }, '', '/');
        }
    }

    function showRegistrationForm(updateUrl = true) {
        if (loginForm) loginForm.classList.add("hidden");
        if (registerForm) registerForm.classList.remove("hidden");
        if (toggleToRegister) toggleToRegister.classList.add("hidden");
        if (toggleToLogin) toggleToLogin.classList.remove("hidden");
        if (demoSection) demoSection.classList.add("hidden");
        if (authTitle) authTitle.innerHTML = 'Create Account<span>.</span>';
        if (authSubtitle) authSubtitle.textContent = 'Register with your approved MMCOE college email to access the portal.';
        if (authBadgeText) authBadgeText.textContent = 'STUDENT REGISTRATION';
        showError("");
        showRegError("");
        showRegSuccess("");
        if (updateUrl && typeof window !== 'undefined' && window.history && window.location.pathname !== '/register/') {
            window.history.pushState({ page: 'register' }, '', '/register/');
        }
    }

    function syncAuthViewWithUrl() {
        if (typeof window === 'undefined' || !window.location) return;
        const path = window.location.pathname.toLowerCase();
        const hash = window.location.hash.toLowerCase();
        if (path.includes('/register') || path.includes('/create-account') || hash === '#register') {
            showRegistrationForm(false);
        } else {
            showLoginForm(false);
        }
    }

    window.showRegistrationForm = showRegistrationForm;
    window.showLoginForm = showLoginForm;
    window.syncAuthViewWithUrl = syncAuthViewWithUrl;

    function getInitials(name, fallback = "DC") {
        if (!name) return fallback;
        const parts = name.trim().split(" ");
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    }

    function applyRoleStyles(role) {
        const isStudent = role === "STUDENT";
        const roleLabel = isStudent ? "STUDENT" : "ADMIN";
        const badgeClass = isStudent ? "badge-student" : "badge-admin";

        // Update badges
        if (sidebarRole) {
            sidebarRole.textContent = isStudent ? "Student Account" : "Administrator";
            sidebarRole.className = `badge-role ${badgeClass}`;
        }
        if (topbarRoleBadge) {
            topbarRoleBadge.textContent = roleLabel;
            topbarRoleBadge.className = `badge-role ${badgeClass}`;
        }
        if (authStatusRole) {
            authStatusRole.textContent = roleLabel;
            authStatusRole.className = `badge-role ${badgeClass}`;
        }
        if (topbarPortalSubtitle) {
            topbarPortalSubtitle.textContent = isStudent 
                ? "MMCOE / STUDENT PORTAL" 
                : "MMCOE / ADMINISTRATIVE PORTAL";
        }
        if (welcomeSubtitle) {
            welcomeSubtitle.textContent = "Welcome to MMCOE Digital Campus.";
        }
    }

    // ----------------------------------------------------
    // 3. AUTH STATE SYNCHRONIZATION
    // ----------------------------------------------------
    function onAuthStateChange(user) {
        if (user) {
            // Display Dashboard, Hide Login
            loginPage.classList.add("hidden");
            dashboard.classList.remove("hidden");

            const displayName = user.full_name || user.name || user.username || user.email;
            const initials = getInitials(displayName, user.role === "ADMIN" ? "AD" : "ST");

            // Sidebar and Topbar info
            if (userAvatar) {
                if (user.profile_picture) {
                    userAvatar.innerHTML = `<img src="${user.profile_picture}" alt="Avatar" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
                } else {
                    userAvatar.textContent = initials;
                }
            }
            if (sidebarName) sidebarName.textContent = displayName;
            if (welcomeName) welcomeName.textContent = displayName;

            // Security panel meta
            if (authStatusUser) authStatusUser.textContent = user.email || user.username;
            if (authStatusId) authStatusId.textContent = `#${user.id} (${user.username})`;

            applyRoleStyles(user.role);
            showPage("home");
            showError("");
        } else {
            // Display Login, Hide Dashboard
            dashboard.classList.add("hidden");
            loginPage.classList.remove("hidden");
            if (loginForm) loginForm.reset();
            if (registerForm) registerForm.reset();
            syncAuthViewWithUrl();
            showError("");
        }
    }

    // Subscribe UI listener to auth service
    window.authService.onAuthStateChanged(onAuthStateChange);

    // Initial check for route on fresh load
    syncAuthViewWithUrl();

    // ----------------------------------------------------
    // 4. LOGIN FORM SUBMISSION
    // ----------------------------------------------------
    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const identifier = emailInput.value.trim();
        const password = passwordInput.value.trim();

        if (!identifier || !password) {
            showError("Please provide your email / ID and password.");
            return;
        }

        setLoading(true);
        showError("");

        const result = await window.authService.login(identifier, password);
        setLoading(false);

        if (!result.ok) {
            showError(result.error);
        }
    });

    // ----------------------------------------------------
    // 4B. AUTH SWITCHER & REGISTRATION FORM SUBMISSION
    // ----------------------------------------------------
    if (showRegisterLink) {
        showRegisterLink.addEventListener("click", function (e) {
            e.preventDefault();
            showRegistrationForm(true);
        });
    }

    if (showLoginLink) {
        showLoginLink.addEventListener("click", function (e) {
            e.preventDefault();
            showLoginForm(true);
        });
    }

    window.addEventListener("popstate", function () {
        if (!window.authService || !window.authService.isAuthenticated()) {
            syncAuthViewWithUrl();
        }
    });

    if (registerForm) {
        registerForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const fullName = regFullNameInput ? regFullNameInput.value.trim() : "";
            const email = regEmailInput ? regEmailInput.value.trim() : "";
            const password = regPasswordInput ? regPasswordInput.value : "";
            const passwordConfirm = regPasswordConfirmInput ? regPasswordConfirmInput.value : "";

            if (!fullName) {
                showRegError("Please enter your full name.");
                return;
            }
            if (!email) {
                showRegError("Please enter your college email.");
                return;
            }
            if (!password) {
                showRegError("Please enter a password.");
                return;
            }
            if (password !== passwordConfirm) {
                showRegError("Passwords do not match.");
                return;
            }

            setRegLoading(true);
            showRegError("");
            showRegSuccess("");

            const result = await window.authService.register(fullName, email, password, passwordConfirm);
            setRegLoading(false);

            if (result.ok) {
                showRegSuccess(result.message || "Registration successful. Please log in.");
                registerForm.reset();
                setTimeout(() => {
                    showLoginForm();
                    if (emailInput) {
                        emailInput.value = email;
                    }
                    if (passwordInput) {
                        passwordInput.value = "";
                        passwordInput.focus();
                    }
                }, 1500);
            } else {
                showRegError(result.error);
            }
        });
    }

    // ----------------------------------------------------
    // 5. QUICK DEMO BUTTONS (ADMIN, STUDENT A, STUDENT B)
    // ----------------------------------------------------
    if (demoAdminBtn) {
        demoAdminBtn.addEventListener("click", async function () {
            emailInput.value = "admin@gmail.com";
            passwordInput.value = "Admin@123";
            setLoading(true);
            showError("");
            const result = await window.authService.login("admin@gmail.com", "Admin@123");
            setLoading(false);
            if (!result.ok) showError(result.error);
        });
    }

    if (demoStudentABtn) {
        demoStudentABtn.addEventListener("click", async function () {
            emailInput.value = "student.a@gmail.com";
            passwordInput.value = "Studenta@123";
            setLoading(true);
            showError("");
            const result = await window.authService.login("student.a@gmail.com", "Studenta@123");
            setLoading(false);
            if (!result.ok) showError(result.error);
        });
    }

    if (demoStudentBBtn) {
        demoStudentBBtn.addEventListener("click", async function () {
            emailInput.value = "student.b@gmail.com";
            passwordInput.value = "Studentb@123";
            setLoading(true);
            showError("");
            const result = await window.authService.login("student.b@gmail.com", "Studentb@123");
            setLoading(false);
            if (!result.ok) showError(result.error);
        });
    }

    // ----------------------------------------------------
    // 6. LOGOUT
    // ----------------------------------------------------
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async function () {
            await window.authService.logout();
        });
    }

    // ----------------------------------------------------
    // 7. BACKEND ROLE AUTHORIZATION LIVE TESTS
    // ----------------------------------------------------
    async function executeApiTest(apiCall, endpointName) {
        if (!apiTestResult) return;
        apiTestResult.style.display = "block";
        apiTestResult.style.background = "#fff8e6";
        apiTestResult.style.border = "1px solid #fde68a";
        apiTestResult.style.color = "#854d0e";
        apiTestResult.innerHTML = `Connecting to <code>${endpointName}</code>...`;

        const response = await apiCall();
        if (response.ok) {
            apiTestResult.style.background = "#f0fdf4";
            apiTestResult.style.border = "1px solid #bbf7d0";
            apiTestResult.style.color = "#15803d";
            apiTestResult.innerHTML = `<strong>HTTP ${response.status} OK:</strong> ${response.data.message || 'Access Authorized.'}`;
        } else {
            apiTestResult.style.background = "#fef2f2";
            apiTestResult.style.border = "1px solid #fecaca";
            apiTestResult.style.color = "#b91c1c";
            apiTestResult.innerHTML = `<strong>HTTP ${response.status} Forbidden:</strong> ${response.error || 'Access Denied by backend authorization.'}`;
        }
    }

    if (testStudentApiBtn) {
        testStudentApiBtn.addEventListener("click", function () {
            executeApiTest(() => window.apiClient.testStudentEndpoint(), "/api/auth/student-only/");
        });
    }

    if (testAdminApiBtn) {
        testAdminApiBtn.addEventListener("click", function () {
            executeApiTest(() => window.apiClient.testAdminEndpoint(), "/api/auth/admin-only/");
        });
    }

    // ----------------------------------------------------
    // 8. SUBPAGE TAB NAVIGATION (ACCESSIBLE SWITCHER)
    // ----------------------------------------------------
    function showPage(pageName) {
        document.querySelectorAll(".page").forEach(function (page) {
            page.classList.remove("active");
        });

        document.querySelectorAll(".nav-btn").forEach(function (button) {
            button.classList.remove("active");
        });

        const selectedPage = document.getElementById("page-" + pageName);
        const selectedButton = document.querySelector(`.nav-btn[data-page="${pageName}"]`);

        if (selectedPage) {
            selectedPage.classList.add("active");
        }
        if (selectedButton) {
            selectedButton.classList.add("active");
        }
    }

    window.showPage = showPage;

    // ----------------------------------------------------
    // 8B. MOBILE NAVIGATION DRAWER (HAMBURGER MENU)
    // ----------------------------------------------------
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const mobileMenuCloseBtn = document.getElementById("mobileMenuCloseBtn");
    const mobileDrawerOverlay = document.getElementById("mobileDrawerOverlay");
    const sidebarNav = document.getElementById("sidebarNav") || document.querySelector(".sidebar");

    function openMobileMenu(e) {
        if (e && e.preventDefault) e.preventDefault();
        const sidebar = document.getElementById("sidebarNav") || document.querySelector(".sidebar");
        const overlay = document.getElementById("mobileDrawerOverlay");
        const btn = document.getElementById("mobileMenuBtn");
        if (sidebar) sidebar.classList.add("mobile-open");
        if (overlay) overlay.classList.add("active");
        if (btn) btn.setAttribute("aria-expanded", "true");
        document.body.classList.add("drawer-open");
    }

    function closeMobileMenu(e) {
        if (e && e.stopPropagation) e.stopPropagation();
        const sidebar = document.getElementById("sidebarNav") || document.querySelector(".sidebar");
        const overlay = document.getElementById("mobileDrawerOverlay");
        const btn = document.getElementById("mobileMenuBtn");
        if (sidebar) sidebar.classList.remove("mobile-open");
        if (overlay) overlay.classList.remove("active");
        if (btn) btn.setAttribute("aria-expanded", "false");
        document.body.classList.remove("drawer-open");
    }

    window.openMobileMenu = openMobileMenu;
    window.closeMobileMenu = closeMobileMenu;

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener("click", openMobileMenu);
        mobileMenuBtn.addEventListener("touchend", function (e) {
            e.preventDefault();
            openMobileMenu(e);
        });
    }
    if (mobileMenuCloseBtn) {
        mobileMenuCloseBtn.addEventListener("click", closeMobileMenu);
        mobileMenuCloseBtn.addEventListener("touchend", function (e) {
            e.preventDefault();
            closeMobileMenu(e);
        });
    }
    if (mobileDrawerOverlay) {
        mobileDrawerOverlay.addEventListener("click", closeMobileMenu);
        mobileDrawerOverlay.addEventListener("touchend", function (e) {
            e.preventDefault();
            closeMobileMenu(e);
        });
    }

    // Auto-close drawer on Escape key
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && sidebarNav && sidebarNav.classList.contains("mobile-open")) {
            closeMobileMenu();
        }
    });

    // Sidebar navigation click handlers
    document.querySelectorAll(".nav-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            closeMobileMenu();
            const page = button.dataset.page;
            if (page === "maps") {
                window.location.href = "/navigator/";
                return;
            }
            if (page === "internships") {
                window.location.href = "/interx/";
                return;
            }
            if (page === "community") {
                window.location.href = "/community/";
                return;
            }
            showPage(page);
        });
    });

    // In-page explore links
    document.querySelectorAll(".explore-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            if (button.dataset.go === "community") {
                window.location.href = "/community/";
                return;
            }
            if (button.dataset.go) {
                showPage(button.dataset.go);
            }
        });
    });

    // Campus Wayfinding card click handler -> opens /navigator/
    const campusWayfindingCard = document.getElementById("campusWayfindingCard");
    if (campusWayfindingCard) {
        campusWayfindingCard.addEventListener("click", function (e) {
            if (!e.target.closest("a")) {
                window.location.href = "/navigator/";
            }
        });
    }

    // InterX Career Hub card click handler -> opens /interx/
    const interxCareerHubCard = document.getElementById("interxCareerHubCard");
    if (interxCareerHubCard) {
        interxCareerHubCard.addEventListener("click", function (e) {
            if (!e.target.closest("a")) {
                window.location.href = "/interx/";
            }
        });
    }

    // Student Community card click handler -> opens /community/
    const studentCommunityCard = document.getElementById("studentCommunityCard");
    if (studentCommunityCard) {
        studentCommunityCard.addEventListener("click", function (e) {
            if (!e.target.closest("a")) {
                window.location.href = "/community/";
            }
        });
    }

    // ----------------------------------------------------
    // 9. AUTOMATIC SESSION RESTORATION
    // ----------------------------------------------------
    window.authService.init();
});