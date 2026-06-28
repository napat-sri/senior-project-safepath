<template>
    <div class="page-shell">
        <aside :class="['sidebar', { collapsed: sidebarCollapsed }]">
            <div class="brand-section">
                <img class="brand-logo" :src="safePathLogo" alt="SafePath Berlin logo" />

                <div class="brand-copy">
                    <h2>SafePath</h2>
                    <span>Berlin</span>
                </div>

                <button class="sidebar-toggle" type="button" @click="toggleSidebar" aria-label="Toggle sidebar">
                    ☰
                </button>
            </div>

            <nav class="nav-menu" aria-label="Primary navigation">
                <button type="button" class="nav-item" @click="goToHome">
                    <span>🗺️</span>
                    Dashboard
                </button>

                <button type="button" class="nav-item active">
                    <span>👤</span>
                    Profile
                </button>

                <button type="button" class="nav-item" @click="goToIncident">
                    <span>⚠️</span>
                    Report Incident
                </button>

                <button type="button" class="nav-item">
                    <span>📋</span>
                    Community Reports
                </button>
            </nav>

            <div class="side-note card">
                <p class="side-label">Edit Profile</p>
                <h3>Manage your SafePath profile</h3>
                <p>
                    Update your profile picture, display name, and account settings.
                </p>
            </div>
        </aside>

        <main class="main-content">
            <header class="topbar card">
                <div>
                    <h2>Profile Settings</h2>
                    <p class="muted">
                        Manage your SafePath Berlin account, profile details, and account actions.
                    </p>
                </div>

                <button type="button" class="btn btn-ghost" @click="logout">
                    Logout
                </button>
            </header>

            <section class="profile-grid">
                <section class="profile-main">
                    <article class="profile-card card">
                        <div class="profile-header">
                            <div class="avatar">
                                <img v-if="profilePreview" :src="profilePreview" alt="Profile preview" />
                                <span v-else>{{ userInitials }}</span>
                            </div>

                            <div>
                                <p class="eyebrow">Account Overview</p>
                                <h3>{{ user.name }}</h3>
                                <p class="muted">{{ user.email }}</p>
                            </div>

                            <span class="status-badge">
                                <span class="status-dot"></span>
                                Active
                            </span>
                        </div>

                        <div class="info-grid">
                            <div class="info-item">
                                <span>Login Provider</span>
                                <strong>{{ user.provider }}</strong>
                            </div>

                            <div class="info-item">
                                <span>Member Since</span>
                                <strong>{{ user.memberSince }}</strong>
                            </div>

                            <div class="info-item">
                                <span>Account Type</span>
                                <strong>{{ user.accountType }}</strong>
                            </div>
                        </div>
                    </article>

                    <article class="edit-profile-card card">
                        <div class="panel-header">
                            <div>
                                <h3>Edit Profile</h3>
                                <p class="muted">
                                    Update your display name and profile picture for your SafePath account.
                                </p>
                            </div>
                        </div>

                        <div class="edit-profile-layout">
                            <div class="profile-photo-editor">
                                <div class="large-avatar">
                                    <img v-if="profilePreview" :src="profilePreview" alt="Profile picture preview" />
                                    <span v-else>{{ userInitials }}</span>
                                </div>

                                <label class="upload-photo-btn">
                                    Change Picture
                                    <input type="file" accept="image/*" @change="handleProfileImageChange" />
                                </label>

                                <button v-if="profilePreview" type="button" class="remove-photo-btn"
                                    @click="removeProfileImage">
                                    Remove picture
                                </button>
                            </div>

                            <div class="edit-form">
                                <label for="display-name">Display Name</label>
                                <input id="display-name" v-model="editableProfile.name" class="input" type="text"
                                    placeholder="Enter your display name" />

                                <label for="email-address">Email Address</label>
                                <input id="email-address" v-model="editableProfile.email" class="input" type="email"
                                    disabled />

                                <p class="helper-copy">
                                    Email address is managed by your sign-in provider and cannot be changed here.
                                </p>

                                <button type="button" class="btn btn-primary save-btn" @click="saveProfile">
                                    Save Profile
                                </button>
                            </div>
                        </div>
                    </article>

                    <article class="privacy-card card">
                        <h3>Privacy Notice</h3>
                        <p class="muted">
                            SafePath Berlin only uses your account information to support login,
                            profile settings, route-related features, and safety preferences.
                        </p>
                    </article>

                    <article class="danger-card card">
                        <div>
                            <p class="eyebrow danger-eyebrow">Danger Zone</p>
                            <h3>Delete Account</h3>
                            <p class="muted">
                                Permanently delete your SafePath account. Your saved profile data may be removed,
                                while incident reports may be anonymized for community safety.
                            </p>
                        </div>

                        <button type="button" class="delete-btn" @click="openDeleteModal">
                            Delete my account
                        </button>
                    </article>
                </section>
            </section>
        </main>

        <div v-if="showDeleteModal" class="modal-backdrop">
            <section class="confirm-modal card">
                <div class="modal-icon">⚠️</div>

                <h3>Delete account?</h3>

                <p class="muted">
                    This action cannot be undone. To confirm account deletion, type
                    <strong>DELETE</strong> below.
                </p>

                <input v-model="deleteConfirmText" class="input confirm-input" type="text"
                    placeholder="Type DELETE to confirm" />

                <div class="modal-actions">
                    <button type="button" class="btn btn-ghost" @click="closeDeleteModal">
                        Cancel
                    </button>

                    <button type="button" class="delete-confirm-btn" :disabled="deleteConfirmText !== 'DELETE'"
                        @click="deleteAccount">
                        Delete permanently
                    </button>
                </div>
            </section>
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import safePathLogo from '../assets/Berlin.png'

const router = useRouter()

const sidebarCollapsed = ref(false)
const showDeleteModal = ref(false)
const deleteConfirmText = ref('')
const profilePreview = ref('')

const user = ref({
    name: 'SafePath User',
    email: 'user@example.com',
    provider: 'Google',
    memberSince: 'June 2026',
    accountType: 'Standard'
})

const editableProfile = ref({
    name: user.value.name,
    email: user.value.email
})

const userInitials = computed(() => {
    return user.value.name
        .split(' ')
        .map((part) => part.charAt(0))
        .join('')
        .slice(0, 2)
        .toUpperCase()
})

const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
}

const goToHome = () => {
    router.push('/home')
}

const goToIncident = () => {
    router.push('/incident')
}

const handleProfileImageChange = (event) => {
    const file = event.target.files?.[0]

    if (!file) {
        return
    }

    profilePreview.value = URL.createObjectURL(file)
}

const removeProfileImage = () => {
    profilePreview.value = ''
}

const saveProfile = () => {
    user.value.name = editableProfile.value.name

    console.log('Profile saved:', {
        name: editableProfile.value.name,
        profileImage: profilePreview.value
    })
}

const logout = () => {
    console.log('Logout user')
    router.push('/login')
}

const openDeleteModal = () => {
    deleteConfirmText.value = ''
    showDeleteModal.value = true
}

const closeDeleteModal = () => {
    showDeleteModal.value = false
    deleteConfirmText.value = ''
}

const deleteAccount = () => {
    if (deleteConfirmText.value !== 'DELETE') {
        return
    }

    console.log('Delete account requested')

    closeDeleteModal()
    router.push('/login')
}
</script>


<style scoped>
:global(body) {
    margin: 0;
    background: var(--color-bg);
}

.page-shell {
    min-height: 100vh;
    display: flex;
    color: var(--color-text);
}

.sidebar {
    width: 248px;
    flex-shrink: 0;
    padding: 24px 18px;
    border-right: 1px solid var(--color-border);
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(14px);
    transition: width 200ms ease, padding 200ms ease;
}

.sidebar.collapsed {
    width: 76px;
    padding: 16px;
}

.brand-section {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
}

.brand-logo {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    object-fit: cover;
    flex-shrink: 0;
    border: 1px solid var(--color-border);
    background: var(--color-surface);
}

.brand-copy {
    flex: 1;
    min-width: 0;
}

.brand-copy h2 {
    margin: 0;
}

.brand-copy span {
    color: var(--color-primary);
    font-weight: 700;
}

.sidebar-toggle {
    margin-left: auto;
    flex-shrink: 0;
    border: 0;
    background: transparent;
    color: var(--color-text-secondary);
    font-size: 20px;
    cursor: pointer;
}

.sidebar.collapsed .brand-copy,
.sidebar.collapsed .nav-menu,
.sidebar.collapsed .side-note {
    display: none;
}

.nav-menu {
    display: grid;
    gap: 10px;
    margin-top: 32px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 16px;
    border-radius: var(--radius-md);
    border: 1px solid transparent;
    background: #f8fafc;
    color: var(--color-text);
    text-decoration: none;
    cursor: pointer;
    font: inherit;
}

.nav-item.active {
    border-color: rgba(99, 102, 241, 0.22);
    background: rgba(99, 102, 241, 0.08);
    color: var(--color-primary);
}

.side-note {
    margin-top: 28px;
    padding: 18px;
}

.side-label,
.eyebrow {
    margin: 0 0 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 11px;
    color: var(--color-neutral);
}

.side-note p,
.profile-card p {
    color: var(--color-text-secondary);
}

.main-content {
    flex: 1;
    padding: 28px;
}

.topbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 18px;
    padding: 18px;
    margin-bottom: 24px;
}

.topbar h2 {
    margin: 0 0 6px;
}

.profile-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 24px;
    align-items: start;
}

.profile-main {
    display: grid;
    gap: 24px;
}

.profile-card,
.edit-profile-card,
.privacy-card,
.danger-card {
    padding: 22px;
}

.profile-header {
    display: flex;
    align-items: center;
    gap: 18px;
}

.avatar {
    width: 72px;
    height: 72px;
    display: grid;
    place-items: center;
    overflow: hidden;
    flex-shrink: 0;
    border-radius: 22px;
    background: rgba(99, 102, 241, 0.12);
    color: var(--color-primary);
    font-size: 24px;
    font-weight: 800;
}

.avatar img,
.large-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.status-badge {
    margin-left: auto;
    display: inline-flex;
    align-items: center;
    padding: 8px 12px;
    border-radius: var(--radius-pill);
    border: 1px solid var(--color-border);
    color: var(--color-text-secondary);
    font-size: 14px;
}

.status-dot {
    background: var(--color-success);
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-top: 24px;
}

.info-item {
    padding: 16px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: #f8fafc;
}

.info-item span {
    display: block;
    margin-bottom: 8px;
    color: var(--color-text-secondary);
    font-size: 13px;
}

.panel-header {
    margin-bottom: 18px;
}

.panel-header h3,
.privacy-card h3 {
    margin: 0 0 6px;
}

/* Edit Profile section */
.edit-profile-layout {
    display: grid;
    grid-template-columns: 220px minmax(0, 1fr);
    gap: 28px;
    align-items: start;
}

.profile-photo-editor {
    display: grid;
    justify-items: center;
    gap: 12px;
}

.large-avatar {
    width: 132px;
    height: 132px;
    display: grid;
    place-items: center;
    overflow: hidden;
    border-radius: 32px;
    border: 1px solid var(--color-border);
    background: rgba(99, 102, 241, 0.12);
    color: var(--color-primary);
    font-size: 38px;
    font-weight: 800;
}

.upload-photo-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 42px;
    padding: 0 14px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border);
    background: #ffffff;
    color: var(--color-primary);
    font-weight: 700;
    cursor: pointer;
}

.upload-photo-btn input {
    display: none;
}

.remove-photo-btn {
    border: 0;
    background: transparent;
    color: var(--color-error);
    font-weight: 700;
    cursor: pointer;
}

.edit-form {
    display: grid;
    gap: 12px;
}

.edit-form label {
    font-weight: 700;
    color: var(--color-text);
}

.edit-form .input {
    width: 100%;
    box-sizing: border-box;
}

.edit-form .input:disabled {
    background: #f8fafc;
    color: var(--color-text-secondary);
    cursor: not-allowed;
}

.helper-copy {
    margin: 0;
    color: var(--color-text-secondary);
    font-size: 13px;
    line-height: 1.5;
}

.save-btn {
    width: fit-content;
    margin-top: 6px;
}

.danger-card {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    border-color: rgba(239, 68, 68, 0.35);
}

.danger-eyebrow {
    color: var(--color-error);
}

.delete-btn,
.delete-confirm-btn {
    border: 0;
    border-radius: var(--radius-sm);
    background: var(--color-error);
    color: #ffffff;
    font-weight: 700;
    cursor: pointer;
}

.delete-btn {
    align-self: center;
    min-width: 170px;
    height: 46px;
}

.delete-btn:hover,
.delete-confirm-btn:hover:not(:disabled) {
    background: #dc2626;
}

.modal-backdrop {
    position: fixed;
    inset: 0;
    display: grid;
    place-items: center;
    padding: 24px;
    background: rgba(15, 23, 42, 0.48);
    z-index: 50;
}

.confirm-modal {
    width: 100%;
    max-width: 440px;
    padding: 28px;
}

.modal-icon {
    width: 52px;
    height: 52px;
    display: grid;
    place-items: center;
    margin-bottom: 16px;
    border-radius: 18px;
    background: rgba(239, 68, 68, 0.1);
}

.confirm-input {
    width: 100%;
    box-sizing: border-box;
    margin-top: 18px;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 22px;
}

.delete-confirm-btn {
    padding: 10px 16px;
}

.delete-confirm-btn:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

@media (max-width: 1100px) {
    .info-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 760px) {
    .page-shell {
        flex-direction: column;
    }

    .sidebar,
    .sidebar.collapsed {
        width: auto;
        padding: 16px;
    }

    .sidebar.collapsed .brand-copy {
        display: block;
    }

    .sidebar.collapsed .nav-menu,
    .sidebar.collapsed .side-note {
        display: grid;
    }

    .main-content {
        padding: 18px;
    }

    .topbar,
    .profile-header,
    .danger-card,
    .modal-actions {
        flex-direction: column;
        align-items: stretch;
    }

    .edit-profile-layout {
        grid-template-columns: 1fr;
    }

    .status-badge {
        margin-left: 0;
        width: fit-content;
    }

    .save-btn,
    .delete-btn {
        width: 100%;
    }
}
</style>
