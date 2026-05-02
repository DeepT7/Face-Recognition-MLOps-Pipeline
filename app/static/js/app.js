// Face Matching Gateway Frontend Application

class FaceGatewayApp {
    constructor() {
        this.apiKey = null;
        this.apiBaseUrl = window.location.origin;
        this.currentSection = 'home';
        this.allUsers = []; // Store all users for search functionality

        // Pagination state
        this.currentPage = 1;
        this.pageSize = 100;
        this.filteredUsers = []; // Store filtered users for pagination

        this.init();
    }

    init() {
        this.bindEvents();
        this.showSection('home');
        this.checkAuthStatus();
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.getAttribute('href').substring(1);
                this.showSection(section);
            });
        });

        // Authentication Modal
        document.getElementById('authBtn').addEventListener('click', () => this.showAuthModal());
        document.querySelectorAll('.modal-close').forEach(close => {
            close.addEventListener('click', () => this.hideModals());
        });

        // Auth Form
        document.getElementById('authenticateBtn').addEventListener('click', () => this.authenticate());

        // Register Form
        document.getElementById('registerForm').addEventListener('submit', (e) => this.handleRegister(e));

        // Verify Form
        document.getElementById('verifyForm').addEventListener('submit', (e) => this.handleVerify(e));

        // Manage Users
        document.getElementById('refreshUsersBtn').addEventListener('click', () => this.loadUsers());
        document.getElementById('userSearch').addEventListener('input', (e) => this.filterUsers(e.target.value));
        document.getElementById('pageSize').addEventListener('change', (e) => this.changePageSize(parseInt(e.target.value)));
        document.getElementById('prevPage').addEventListener('click', () => this.changePage(this.currentPage - 1));
        document.getElementById('nextPage').addEventListener('click', () => this.changePage(this.currentPage + 1));

        // File Upload Previews
        document.getElementById('personImage').addEventListener('change', (e) => this.previewImage(e.target, 'imagePreview'));
        document.getElementById('verifyImage').addEventListener('change', (e) => this.previewImage(e.target, 'verifyImagePreview'));

        // Drag and Drop
        this.setupDragAndDrop('personImage', 'imagePreview');
        this.setupDragAndDrop('verifyImage', 'verifyImagePreview');

        // Modal outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModals();
                }
            });
        });
    }

    showSection(sectionId) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[href="#${sectionId}"]`).classList.add('active');

        // Show section
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionId).classList.add('active');

        this.currentSection = sectionId;

        // Load data for specific sections
        if (sectionId === 'manage') {
            this.loadUsers();
        }
    }

    scrollToSection(sectionId) {
        this.showSection(sectionId);
        document.getElementById(sectionId).scrollIntoView({ behavior: 'smooth' });
    }

    showAuthModal() {
        document.getElementById('authModal').classList.add('show');
    }

    hideModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
        });
    }

    checkAuthStatus() {
        this.apiKey = null;
        this.updateAuthUI(false);
    }

    async validateApiKey(apiKey) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/users`, {
                headers: {
                    'X-API-Key': apiKey
                }
            });
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    async authenticate() {
        const apiKey = document.getElementById('apiKey').value.trim();
        const statusDiv = document.getElementById('authStatus');
        const authBtn = document.getElementById('authenticateBtn');

        if (!apiKey) {
            this.showAuthStatus('Please enter an API key', 'error');
            return;
        }

        authBtn.disabled = true;
        authBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Authenticating...';

        try {
            // Test authentication with a simple request
            const response = await fetch(`${this.apiBaseUrl}/users`, {
                headers: {
                    'X-API-Key': apiKey
                }
            });

            if (response.ok) {
                this.apiKey = apiKey;
                this.updateAuthUI(true);
                this.showAuthStatus('Authentication successful!', 'success');
                setTimeout(() => {
                    this.hideModals();
                }, 1500);
            } else {
                this.showAuthStatus('Invalid API key', 'error');
            }
        } catch (error) {
            this.showAuthStatus('Network error. Please check your connection.', 'error');
        } finally {
            authBtn.disabled = false;
            authBtn.innerHTML = '<i class="fas fa-check"></i> Authenticate';
        }
    }

    showAuthStatus(message, type) {
        const statusDiv = document.getElementById('authStatus');
        statusDiv.textContent = message;
        statusDiv.className = `auth-status ${type}`;
    }

    updateAuthUI(isAuthenticated) {
        const authBtn = document.getElementById('authBtn');

        if (isAuthenticated) {
            authBtn.innerHTML = '<i class="fas fa-check-circle"></i> Authenticated';
            authBtn.classList.add('authenticated');
        } else {
            authBtn.innerHTML = '<i class="fas fa-key"></i> Authenticate';
            authBtn.classList.remove('authenticated');
        }
    }

    async handleRegister(event) {
        event.preventDefault();

        if (!this.apiKey) {
            this.showToast('Please authenticate first', 'error');
            this.showAuthModal();
            return;
        }

        const personName = document.getElementById('personName').value.trim();
        const imageFile = document.getElementById('personImage').files[0];
        const registerBtn = document.getElementById('registerBtn');

        if (!personName || !imageFile) {
            this.showToast('Please fill in all fields', 'error');
            return;
        }

        registerBtn.disabled = true;
        registerBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registering...';

        try {
            const formData = new FormData();
            formData.append('file', imageFile);

            const response = await fetch(`${this.apiBaseUrl}/register?person_name=${encodeURIComponent(personName)}`, {
                method: 'POST',
                headers: {
                    'X-API-Key': this.apiKey
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.showResponseModal('Registration Successful', JSON.stringify(data, null, 2));
                document.getElementById('registerForm').reset();
                document.getElementById('imagePreview').style.display = 'none';
                this.showToast('Face registered successfully!', 'success');
            } else {
                this.showResponseModal('Registration Failed', `Error ${response.status}: ${JSON.stringify(data, null, 2)}`);
                this.showToast('Registration failed', 'error');
            }
        } catch (error) {
            this.showResponseModal('Network Error', error.message);
            this.showToast('Network error occurred', 'error');
        } finally {
            registerBtn.disabled = false;
            registerBtn.innerHTML = '<i class="fas fa-plus"></i> Register Face';
        }
    }

    async handleVerify(event) {
        event.preventDefault();

        const imageFile = document.getElementById('verifyImage').files[0];
        const personId = document.getElementById('personId').value.trim();
        const verifyBtn = document.getElementById('verifyBtn');

        if (!imageFile) {
            this.showToast('Please select an image to verify', 'error');
            return;
        }

        verifyBtn.disabled = true;
        verifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';

        try {
            const formData = new FormData();
            formData.append('file', imageFile);

            const url = personId
                ? `${this.apiBaseUrl}/verify?person_id=${personId}`
                : `${this.apiBaseUrl}/verify`;

            // No authentication required for verification
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.showResponseModal('Verification Result', JSON.stringify(data, null, 2));
                this.showToast('Face verification completed!', 'success');
            } else {
                this.showResponseModal('Verification Failed', `Error ${response.status}: ${JSON.stringify(data, null, 2)}`);
                this.showToast('Verification failed', 'error');
            }
        } catch (error) {
            this.showResponseModal('Network Error', error.message);
            this.showToast('Network error occurred', 'error');
        } finally {
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = '<i class="fas fa-search"></i> Verify Face';
        }
    }

    async loadUsers() {
        if (!this.apiKey) {
            this.showToast('Please authenticate first', 'error');
            this.showAuthModal();
            return;
        }

        const usersList = document.getElementById('usersList');
        usersList.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i><p>Loading users...</p></div>';

        try {
            const response = await fetch(`${this.apiBaseUrl}/users`, {
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.allUsers = data.users || [];
                this.filteredUsers = [...this.allUsers]; // Initialize filtered users
                this.currentPage = 1; // Reset to first page
                this.renderUsers();
                this.updatePaginationControls();
            } else {
                usersList.innerHTML = '<div class="loading"><p>Failed to load users</p></div>';
                this.showToast('Failed to load users', 'error');
            }
        } catch (error) {
            usersList.innerHTML = '<div class="loading"><p>Network error</p></div>';
            this.showToast('Network error occurred', 'error');
        }
    }

    renderUsers() {
        const usersList = document.getElementById('usersList');
        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = startIndex + this.pageSize;
        const usersToShow = this.filteredUsers.slice(startIndex, endIndex);

        if (usersToShow.length === 0) {
            usersList.innerHTML = '<div class="loading"><p>No users found</p></div>';
            return;
        }

        usersList.innerHTML = usersToShow.map(user => `
            <div class="user-card">
                <div class="user-info">
                    <div class="user-avatar">
                        ${user.name.charAt(0).toUpperCase()}
                    </div>
                    <div class="user-details">
                        <h3>${user.name}</h3>
                        <p>ID: ${user.id}</p>
                    </div>
                </div>
                <div class="user-actions">
                    <button class="btn btn-danger btn-small" onclick="app.deleteUser('${user.id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    filterUsers(searchTerm) {
        if (!searchTerm.trim()) {
            // Show all users if search is empty
            this.filteredUsers = [...this.allUsers];
        } else {
            // Filter users based on search term
            this.filteredUsers = this.allUsers.filter(user => {
                const nameMatch = user.name.toLowerCase().includes(searchTerm.toLowerCase());
                const idMatch = user.id.toLowerCase().includes(searchTerm.toLowerCase());
                return nameMatch || idMatch;
            });
        }

        // Reset to first page when filtering
        this.currentPage = 1;
        this.renderUsers();
        this.updatePaginationControls();
    }

    changePageSize(newPageSize) {
        this.pageSize = newPageSize;
        this.currentPage = 1; // Reset to first page
        this.renderUsers();
        this.updatePaginationControls();
    }

    changePage(newPage) {
        const totalPages = Math.ceil(this.filteredUsers.length / this.pageSize);
        if (newPage >= 1 && newPage <= totalPages) {
            this.currentPage = newPage;
            this.renderUsers();
            this.updatePaginationControls();
        }
    }

    updatePaginationControls() {
        const totalUsers = this.filteredUsers.length;
        const totalPages = Math.ceil(totalUsers / this.pageSize);
        const startIndex = (this.currentPage - 1) * this.pageSize + 1;
        const endIndex = Math.min(this.currentPage * this.pageSize, totalUsers);

        // Update pagination info
        const paginationInfo = document.getElementById('paginationInfo');
        const currentPageSpan = document.getElementById('currentPage');
        const totalPagesSpan = document.getElementById('totalPages');
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        const paginationControls = document.getElementById('paginationControls');

        if (totalUsers === 0) {
            paginationControls.style.display = 'none';
            return;
        }

        paginationControls.style.display = 'flex';
        paginationInfo.textContent = `Showing ${startIndex}-${endIndex} of ${totalUsers} users`;
        currentPageSpan.textContent = this.currentPage;
        totalPagesSpan.textContent = totalPages;

        // Update button states
        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentPage === totalPages;
    }

    async deleteUser(userId) {
        if (!confirm(`Are you sure you want to delete user ${userId}?`)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/person/${userId}`, {
                method: 'DELETE',
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.showResponseModal('Deletion Successful', JSON.stringify(data, null, 2));
                this.showToast('User deleted successfully!', 'success');
                this.loadUsers(); // Refresh the list
            } else {
                this.showResponseModal('Deletion Failed', `Error ${response.status}: ${JSON.stringify(data, null, 2)}`);
                this.showToast('Failed to delete user', 'error');
            }
        } catch (error) {
            this.showResponseModal('Network Error', error.message);
            this.showToast('Network error occurred', 'error');
        }
    }

    previewImage(input, previewId) {
        const preview = document.getElementById(previewId);
        const file = input.files[0];

        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            preview.style.display = 'none';
        }
    }

    setupDragAndDrop(inputId, previewId) {
        const input = document.getElementById(inputId);
        const uploadArea = input.closest('.file-upload').querySelector('.file-upload-area');

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            });
        });

        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                this.previewImage(input, previewId);
            }
        });
    }

    showResponseModal(title, content) {
        document.getElementById('responseTitle').textContent = title;
        document.getElementById('responseContent').textContent = content;
        document.getElementById('responseModal').classList.add('show');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <div class="toast-message">${message}</div>
        `;

        document.getElementById('toastContainer').appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
}

// Initialize the application
const app = new FaceGatewayApp();