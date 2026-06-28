<template>
    <div class="page-shell admin-shell">
        <aside :class="['sidebar', { collapsed: sidebarCollapsed }]">
            <div class="brand-section">
                <img class="brand-logo" :src="safePathLogo" alt="SafePath Berlin logo" />

                <div class="brand-copy">
                    <h2>SafePath</h2>
                    <span>Admin</span>
                </div>

                <button class="sidebar-toggle" type="button" @click="toggleSidebar" aria-label="Toggle sidebar">
                    ☰
                </button>
            </div>

            <nav class="nav-menu" aria-label="Admin navigation">
                <button type="button" class="nav-item active" aria-label="Dashboard" @click="$router.push('/')">
                    <span>🗺️</span>
                    Dashboard
                </button>

                <button type="button" class="nav-item" aria-label="Profile" @click="$router.push('/profile')">
                    <span>👤</span>
                    Profile
                </button>

                <button type="button" class="nav-item" aria-label="Report Incident" @click="$router.push('/incident')">
                    <span>⚠️</span>
                    Report Incident
                </button>

                <button type="button" class="nav-item" aria-label="Overview Dashboard" @click="$router.push('/overview')">
                    <span>📊</span>
                    Overview Dashboard
                </button>
                
                <button type="button" class="nav-item">
                    <span>📋</span>
                    Community Reports
                </button>

                <button type="button" class="nav-item" @click="scrollToSection('users')">
                    <span>👥</span>
                    Users
                </button>

                <button type="button" class="nav-item" @click="scrollToSection('search-logs')">
                    <span>🔍</span>
                    Search Logs
                </button>

                <button type="button" class="nav-item" @click="scrollToSection('incidents')">
                    <span>⚠️</span>
                    Incidents
                </button>

                <button type="button" class="nav-item" @click="scrollToSection('locations')">
                    <span>📍</span>
                    Location Insights
                </button>

                <button type="button" class="nav-item" @click="goToHome">
                    <span>🗺️</span>
                    User App
                </button>
            </nav>
        </aside>

        <main class="main-content">
            <header class="topbar card">
                <div>
                    <p class="eyebrow">Internal Admin Dashboard</p>
                    <h1>SafePath Berlin Admin</h1>
                    <p class="muted">
                        Review platform activity, manage users, moderate incident reports, and understand safety demand
                        across Berlin.
                    </p>
                </div>

                <div class="topbar-actions">
                    <button type="button" class="btn btn-ghost" @click="refreshDashboard">
                        Refresh
                    </button>

                    <button type="button" class="btn btn-primary" @click="exportReport">
                        Export Report
                    </button>
                </div>
            </header>

            <section class="stats-grid">
                <article v-for="item in overviewStats" :key="item.label" class="stat-card card">
                    <div class="stat-icon">{{ item.icon }}</div>
                    <p>{{ item.label }}</p>
                    <strong>{{ item.value }}</strong>
                    <span :class="['trend', item.trendType]">{{ item.trend }}</span>
                </article>
            </section>

            <section class="admin-grid">
                <section id="search-logs" class="admin-panel card">
                    <div class="panel-header">
                        <div>
                            <h2>User Search Logs</h2>
                            <p class="muted">
                                Track route searches with date, time, start location, destination, and safety score.
                            </p>
                        </div>

                        <div class="table-tools">
                            <input v-model="searchLogFilter" class="input compact-input" type="text"
                                placeholder="Filter search logs" />
                        </div>
                    </div>

                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>User</th>
                                    <th>Start</th>
                                    <th>Destination</th>
                                    <th>Date</th>
                                    <th>Time</th>
                                    <th>Safety</th>
                                    <th>Status</th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr v-for="log in filteredSearchLogs" :key="log.id">
                                    <td>
                                        <div class="user-cell">
                                            <span class="mini-avatar">{{ log.userInitial }}</span>
                                            <div>
                                                <strong>{{ log.user }}</strong>
                                                <small>{{ log.email }}</small>
                                            </div>
                                        </div>
                                    </td>
                                    <td>{{ log.start }}</td>
                                    <td>{{ log.destination }}</td>
                                    <td>{{ log.date }}</td>
                                    <td>{{ log.time }}</td>
                                    <td>
                                        <span :class="['score-badge', getSafetyClass(log.safetyScore)]">
                                            {{ log.safetyScore }}/100
                                        </span>
                                    </td>
                                    <td>
                                        <span :class="['status-badge', log.status.toLowerCase()]">
                                            <span class="status-dot"></span>
                                            {{ log.status }}
                                        </span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>

                <section id="users" class="admin-panel card">
                    <div class="panel-header">
                        <div>
                            <h2>User Management</h2>
                            <p class="muted">
                                Manage user roles, account status, and administrative access.
                            </p>
                        </div>

                        <button type="button" class="btn btn-primary" @click="openUserModal()">
                            Add User
                        </button>
                    </div>

                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>User</th>
                                    <th>Role</th>
                                    <th>Provider</th>
                                    <th>Status</th>
                                    <th>Last Login</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr v-for="user in users" :key="user.id">
                                    <td>
                                        <div class="user-cell">
                                            <span class="mini-avatar">{{ user.initial }}</span>
                                            <div>
                                                <strong>{{ user.name }}</strong>
                                                <small>{{ user.email }}</small>
                                            </div>
                                        </div>
                                    </td>
                                    <td>{{ user.role }}</td>
                                    <td>{{ user.provider }}</td>
                                    <td>
                                        <span :class="['status-badge', user.status.toLowerCase()]">
                                            <span class="status-dot"></span>
                                            {{ user.status }}
                                        </span>
                                    </td>
                                    <td>{{ user.lastLogin }}</td>
                                    <td>
                                        <div class="row-actions">
                                            <button type="button" @click="openUserModal(user)">Edit</button>
                                            <button type="button" class="danger-text" @click="deactivateUser(user.id)">
                                                Deactivate
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>

                <section id="incidents" class="admin-panel card">
                    <div class="panel-header">
                        <div>
                            <h2>Incident Report Management</h2>
                            <p class="muted">
                                Review submitted incidents before they influence public safety insights.
                            </p>
                        </div>

                        <select v-model="incidentStatusFilter" class="input compact-input">
                            <option value="All">All reports</option>
                            <option value="Pending">Pending</option>
                            <option value="Approved">Approved</option>
                            <option value="Rejected">Rejected</option>
                        </select>
                    </div>

                    <div class="incident-list">
                        <article v-for="incident in filteredIncidents" :key="incident.id" class="incident-item">
                            <div class="incident-main">
                                <div class="incident-topline">
                                    <h3>{{ incident.type }}</h3>
                                    <span :class="['status-badge', incident.status.toLowerCase()]">
                                        <span class="status-dot"></span>
                                        {{ incident.status }}
                                    </span>
                                </div>

                                <p class="muted">
                                    {{ incident.location }} · {{ incident.date }} · {{ incident.time }}
                                </p>

                                <p>{{ incident.description }}</p>

                                <div class="evidence-row">
                                    <span>{{ incident.evidenceCount }} evidence files</span>
                                    <span>Submitted by {{ incident.submittedBy }}</span>
                                </div>
                            </div>

                            <div class="incident-actions">
                                <button type="button" class="btn btn-ghost"
                                    @click="updateIncidentStatus(incident.id, 'Rejected')">
                                    Reject
                                </button>

                                <button type="button" class="btn btn-primary"
                                    @click="updateIncidentStatus(incident.id, 'Approved')">
                                    Approve
                                </button>
                            </div>
                        </article>
                    </div>
                </section>

                <section id="locations" class="admin-panel card">
                    <div class="panel-header">
                        <div>
                            <h2>Location Insights</h2>
                            <p class="muted">
                                Understand most searched places and most reported incident areas.
                            </p>
                        </div>
                    </div>

                    <div class="insights-grid">
                        <article class="insight-card">
                            <h3>Most Searched Places</h3>

                            <div class="ranking-list">
                                <div v-for="place in mostSearchedPlaces" :key="place.name" class="ranking-item">
                                    <div>
                                        <strong>{{ place.name }}</strong>
                                        <span>{{ place.type }}</span>
                                    </div>

                                    <div class="bar-wrap">
                                        <span :style="{ width: `${place.percent}%` }"></span>
                                    </div>

                                    <small>{{ place.count }} searches</small>
                                </div>
                            </div>
                        </article>

                        <article class="insight-card">
                            <h3>Most Incident Report Places</h3>

                            <div class="ranking-list">
                                <div v-for="place in mostReportedPlaces" :key="place.name" class="ranking-item">
                                    <div>
                                        <strong>{{ place.name }}</strong>
                                        <span>{{ place.topIncident }}</span>
                                    </div>

                                    <div class="bar-wrap risk">
                                        <span :style="{ width: `${place.percent}%` }"></span>
                                    </div>

                                    <small>{{ place.count }} reports</small>
                                </div>
                            </div>
                        </article>
                    </div>
                </section>
            </section>
        </main>

        <div v-if="showUserModal" class="modal-backdrop">
            <section class="admin-modal card">
                <div class="modal-header">
                    <div>
                        <p class="eyebrow">{{ selectedUser ? 'Edit User' : 'Create User' }}</p>
                        <h2>{{ selectedUser ? 'Update user access' : 'Add new user' }}</h2>
                    </div>

                    <button type="button" class="close-btn" @click="closeUserModal">
                        ×
                    </button>
                </div>

                <form class="modal-form" @submit.prevent="saveUser">
                    <label for="admin-user-name">Name</label>
                    <input id="admin-user-name" v-model="userForm.name" class="input" type="text" />

                    <label for="admin-user-email">Email</label>
                    <input id="admin-user-email" v-model="userForm.email" class="input" type="email" />

                    <label for="admin-user-role">Role</label>
                    <select id="admin-user-role" v-model="userForm.role" class="input">
                        <option>Admin</option>
                        <option>Moderator</option>
                        <option>User</option>
                    </select>

                    <label for="admin-user-status">Status</label>
                    <select id="admin-user-status" v-model="userForm.status" class="input">
                        <option>Active</option>
                        <option>Suspended</option>
                        <option>Pending</option>
                    </select>

                    <div class="modal-actions">
                        <button type="button" class="btn btn-ghost" @click="closeUserModal">
                            Cancel
                        </button>

                        <button type="submit" class="btn btn-primary">
                            Save User
                        </button>
                    </div>
                </form>
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
const searchLogFilter = ref('')
const incidentStatusFilter = ref('All')
const showUserModal = ref(false)
const selectedUser = ref(null)

const overviewStats = ref([
    {
        label: 'Total Users',
        value: '1,248',
        icon: '👥',
        trend: '+12 this week',
        trendType: 'positive'
    },
    {
        label: 'Route Searches',
        value: '8,920',
        icon: '🔍',
        trend: '+18% today',
        trendType: 'positive'
    },
    {
        label: 'Incident Reports',
        value: '312',
        icon: '⚠️',
        trend: '24 pending',
        trendType: 'warning'
    },
    {
        label: 'Top Search Place',
        value: 'Alexanderplatz',
        icon: '📍',
        trend: '842 searches',
        trendType: 'neutral'
    }
])

const searchLogs = ref([
    {
        id: 1,
        user: 'Nora Klein',
        userInitial: 'N',
        email: 'n***@gmail.com',
        start: 'Alexanderplatz',
        destination: 'Berlin Hbf',
        date: '2026-06-24',
        time: '18:42',
        safetyScore: 82,
        status: 'Success'
    },
    {
        id: 2,
        user: 'Emre Yilmaz',
        userInitial: 'E',
        email: 'e***@outlook.com',
        start: 'Kottbusser Tor',
        destination: 'Hermannplatz',
        date: '2026-06-24',
        time: '21:18',
        safetyScore: 61,
        status: 'Success'
    },
    {
        id: 3,
        user: 'SafePath User',
        userInitial: 'S',
        email: 's***@example.com',
        start: 'Warschauer Straße',
        destination: 'Ostkreuz',
        date: '2026-06-24',
        time: '22:05',
        safetyScore: 54,
        status: 'Success'
    },
    {
        id: 4,
        user: 'Lina Weber',
        userInitial: 'L',
        email: 'l***@icloud.com',
        start: 'Potsdamer Platz',
        destination: 'Brandenburg Gate',
        date: '2026-06-23',
        time: '17:36',
        safetyScore: 91,
        status: 'Success'
    }
])

const users = ref([
    {
        id: 1,
        initial: 'A',
        name: 'Admin User',
        email: 'admin@safepath.local',
        role: 'Admin',
        provider: 'Email',
        status: 'Active',
        lastLogin: 'Today 19:12'
    },
    {
        id: 2,
        initial: 'M',
        name: 'Mina Schneider',
        email: 'm***@gmail.com',
        role: 'Moderator',
        provider: 'Google',
        status: 'Active',
        lastLogin: 'Today 17:40'
    },
    {
        id: 3,
        initial: 'S',
        name: 'SafePath User',
        email: 's***@example.com',
        role: 'User',
        provider: 'Google',
        status: 'Active',
        lastLogin: 'Yesterday 21:04'
    },
    {
        id: 4,
        initial: 'J',
        name: 'Jonas Meyer',
        email: 'j***@github.com',
        role: 'User',
        provider: 'GitHub',
        status: 'Suspended',
        lastLogin: '2026-06-18'
    }
])

const incidentReports = ref([
    {
        id: 1,
        type: 'Harassment',
        location: 'Kottbusser Tor',
        date: '2026-06-24',
        time: '21:10',
        status: 'Pending',
        evidenceCount: 2,
        submittedBy: 'Anonymous user',
        description: 'User reported repeated verbal harassment near the station entrance.'
    },
    {
        id: 2,
        type: 'Poor Lighting',
        location: 'Warschauer Straße',
        date: '2026-06-23',
        time: '22:45',
        status: 'Approved',
        evidenceCount: 1,
        submittedBy: 'user_1042',
        description: 'Low visibility reported along the walking path close to the bridge.'
    },
    {
        id: 3,
        type: 'Suspicious Activity',
        location: 'Alexanderplatz',
        date: '2026-06-23',
        time: '20:30',
        status: 'Pending',
        evidenceCount: 0,
        submittedBy: 'Anonymous user',
        description: 'Report of repeated suspicious behavior near a crowded exit area.'
    }
])

const mostSearchedPlaces = ref([
    {
        name: 'Alexanderplatz',
        type: 'Start + destination searches',
        count: 842,
        percent: 100
    },
    {
        name: 'Berlin Hbf',
        type: 'Destination searches',
        count: 731,
        percent: 86
    },
    {
        name: 'Brandenburg Gate',
        type: 'Destination searches',
        count: 622,
        percent: 74
    },
    {
        name: 'Potsdamer Platz',
        type: 'Start searches',
        count: 490,
        percent: 58
    }
])

const mostReportedPlaces = ref([
    {
        name: 'Kottbusser Tor',
        topIncident: 'Harassment reports',
        count: 28,
        percent: 100
    },
    {
        name: 'Alexanderplatz',
        topIncident: 'Suspicious activity',
        count: 21,
        percent: 75
    },
    {
        name: 'Warschauer Straße',
        topIncident: 'Poor lighting',
        count: 18,
        percent: 64
    },
    {
        name: 'Hermannplatz',
        topIncident: 'Crowding / disturbance',
        count: 13,
        percent: 46
    }
])

const userForm = ref({
    name: '',
    email: '',
    role: 'User',
    status: 'Active'
})

const filteredSearchLogs = computed(() => {
    const query = searchLogFilter.value.trim().toLowerCase()

    if (!query) {
        return searchLogs.value
    }

    return searchLogs.value.filter((log) => {
        return [
            log.user,
            log.email,
            log.start,
            log.destination,
            log.date,
            log.time,
            log.status
        ]
            .join(' ')
            .toLowerCase()
            .includes(query)
    })
})

const filteredIncidents = computed(() => {
    if (incidentStatusFilter.value === 'All') {
        return incidentReports.value
    }

    return incidentReports.value.filter((incident) => incident.status === incidentStatusFilter.value)
})

const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
}

const goToHome = () => {
    router.push('/home')
}

const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    })
}

const getSafetyClass = (score) => {
    if (score >= 80) {
        return 'safe'
    }

    if (score >= 60) {
        return 'medium'
    }

    return 'risk'
}

const openUserModal = (user = null) => {
    selectedUser.value = user

    if (user) {
        userForm.value = {
            name: user.name,
            email: user.email,
            role: user.role,
            status: user.status
        }
    } else {
        userForm.value = {
            name: '',
            email: '',
            role: 'User',
            status: 'Active'
        }
    }

    showUserModal.value = true
}

const closeUserModal = () => {
    showUserModal.value = false
    selectedUser.value = null
}

const saveUser = () => {
    if (selectedUser.value) {
        const index = users.value.findIndex((user) => user.id === selectedUser.value.id)

        if (index !== -1) {
            users.value[index] = {
                ...users.value[index],
                name: userForm.value.name,
                email: userForm.value.email,
                role: userForm.value.role,
                status: userForm.value.status,
                initial: userForm.value.name.charAt(0).toUpperCase() || 'U'
            }
        }
    } else {
        users.value.unshift({
            id: Date.now(),
            initial: userForm.value.name.charAt(0).toUpperCase() || 'U',
            name: userForm.value.name || 'New User',
            email: userForm.value.email || 'new-user@example.com',
            role: userForm.value.role,
            provider: 'Email',
            status: userForm.value.status,
            lastLogin: 'Never'
        })
    }

    closeUserModal()
}

const deactivateUser = (userId) => {
    const user = users.value.find((item) => item.id === userId)

    if (user) {
        user.status = 'Suspended'
    }
}

const updateIncidentStatus = (incidentId, status) => {
    const incident = incidentReports.value.find((item) => item.id === incidentId)

    if (incident) {
        incident.status = status
    }
}

const refreshDashboard = () => {
    console.log('Refresh admin dashboard data')
}

const exportReport = () => {
    console.log('Export admin report')
}
</script>

<style scoped>
/* =========================
   Global Page Setup
========================= */

:global(body) {
    margin: 0;
    background: var(--color-bg);
}

.page-shell {
    min-height: 100vh;
    display: flex;
    color: var(--color-text);
}


/* =========================
   Sidebar Container
========================= */

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
    width: auto;
    padding: 16px;
}


/* =========================
   Sidebar Brand / Logo Area
========================= */

.brand-section {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
}

.brand-logo {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
    border-radius: 14px;
    object-fit: cover;
    border: 1px solid var(--color-border);
    background: var(--color-surface);
}

.brand-copy {
    flex: 1;
    min-width: 0;
}

.brand-copy span {
    display: block;
    margin-top: 2px;
    color: var(--color-primary);
    font-weight: 700;
}

.brand-copy p,
.panel-header p,
.topbar p,
.route-summary,
.route-pair,
.muted,
.helper-copy


/* =========================
   Sidebar Collapsed State
========================= */

.sidebar.collapsed .brand-logo,
.sidebar.collapsed .brand-copy {
    display: block;
}
.sidebar.collapsed .nav-menu {
    display: grid;
}


/* =========================
   Sidebar Toggle Button
========================= */

.sidebar-toggle {
    margin-left: auto;
    border: 0;
    background: transparent;
    color: var(--color-text-secondary);
    font-size: 20px;
    cursor: pointer;
}


/* =========================
   Sidebar Navigation Menu
========================= */

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

.side-note h3 {
    margin: 0 0 8px;
}

.side-note p,
.brand-copy p,
.panel-header p,
.topbar p,
.muted {
    color: var(--color-text-secondary);
}

.side-label,
.eyebrow {
    margin: 0 0 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 11px;
    color: var(--color-neutral);
}

/* =========================
   Main Layout
========================= */

.main-content {
    flex: 1;
    padding: 28px;
}
.content-grid {
    display: grid;
    grid-template-columns: minmax(340px, 420px) minmax(0, 1fr);
    gap: 24px;
    align-items: start;
}

.topbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 10px;
    padding: 12px;
    margin-bottom: 12px;
}

/* =========================
   Overview Stats
========================= */

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.stat-card {
    padding: 18px;
}

.stat-icon {
    width: 44px;
    height: 44px;
    display: grid;
    place-items: center;
    margin-bottom: 14px;
    border-radius: 14px;
    background: rgba(99, 102, 241, 0.1);
}

.stat-card p {
    margin: 0 0 6px;
    color: var(--color-text-secondary);
    font-size: 14px;
}

.stat-card strong {
    display: block;
    font-size: 24px;
}

.trend {
    display: inline-flex;
    margin-top: 10px;
    font-size: 13px;
    font-weight: 700;
}

.trend.positive {
    color: var(--color-success);
}

.trend.warning {
    color: var(--color-warning);
}

.trend.neutral {
    color: var(--color-primary);
}

/* =========================
   Admin Sections
========================= */

.admin-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 24px;
}

.admin-panel {
    padding: 22px;
    scroll-margin-top: 24px;
}

.panel-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 18px;
}

.panel-header h2 {
    margin: 0 0 6px;
}

.table-tools {
    display: flex;
    gap: 10px;
}

.compact-input {
    min-width: 210px;
}

/* =========================
   Tables
========================= */

.table-wrap {
    overflow-x: auto;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 860px;
}

th,
td {
    padding: 14px 16px;
    border-bottom: 1px solid var(--color-border);
    text-align: left;
    vertical-align: middle;
}

th {
    background: #f8fafc;
    color: var(--color-text-secondary);
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

tr:last-child td {
    border-bottom: 0;
}

.user-cell {
    display: flex;
    align-items: center;
    gap: 10px;
}

.user-cell strong {
    display: block;
}

.user-cell small {
    display: block;
    margin-top: 2px;
    color: var(--color-text-secondary);
}

.mini-avatar {
    width: 38px;
    height: 38px;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    border-radius: 12px;
    background: rgba(99, 102, 241, 0.1);
    color: var(--color-primary);
    font-weight: 800;
}

/* =========================
   Badges
========================= */

.score-badge,
.status-badge {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    border-radius: var(--radius-pill);
    padding: 7px 10px;
    font-size: 13px;
    font-weight: 700;
}

.score-badge.safe {
    background: rgba(16, 185, 129, 0.12);
    color: var(--color-success);
}

.score-badge.medium {
    background: rgba(245, 158, 11, 0.14);
    color: #a16207;
}

.score-badge.risk {
    background: rgba(239, 68, 68, 0.12);
    color: var(--color-error);
}

.status-badge {
    border: 1px solid var(--color-border);
    color: var(--color-text-secondary);
}

.status-badge.active,
.status-badge.approved,
.status-badge.success {
    color: var(--color-success);
}

.status-badge.pending {
    color: var(--color-warning);
}

.status-badge.suspended,
.status-badge.rejected {
    color: var(--color-error);
}

.status-badge.active .status-dot,
.status-badge.approved .status-dot,
.status-badge.success .status-dot {
    background: var(--color-success);
}

.status-badge.pending .status-dot {
    background: var(--color-warning);
}

.status-badge.suspended .status-dot,
.status-badge.rejected .status-dot {
    background: var(--color-error);
}

/* =========================
   Row Actions
========================= */

.row-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.row-actions button {
    border: 0;
    background: transparent;
    color: var(--color-primary);
    font-weight: 700;
    cursor: pointer;
}

.row-actions .danger-text {
    color: var(--color-error);
}

/* =========================
   Incident Management
========================= */

.incident-list {
    display: grid;
    gap: 14px;
}

.incident-item {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    padding: 16px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: #ffffff;
}

.incident-main {
    min-width: 0;
}

.incident-topline {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}

.incident-topline h3 {
    margin: 0;
}

.incident-main p {
    margin: 8px 0 0;
    line-height: 1.5;
}

.evidence-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 12px;
}

.evidence-row span {
    padding: 7px 10px;
    border-radius: var(--radius-pill);
    border: 1px solid var(--color-border);
    background: #f8fafc;
    color: var(--color-text-secondary);
    font-size: 13px;
}

.incident-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}

/* =========================
   Location Insights
========================= */

.insights-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 18px;
}

.insight-card {
    padding: 18px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: #ffffff;
}

.insight-card h3 {
    margin: 0 0 16px;
}

.ranking-list {
    display: grid;
    gap: 16px;
}

.ranking-item {
    display: grid;
    gap: 8px;
}

.ranking-item strong,
.ranking-item span,
.ranking-item small {
    display: block;
}

.ranking-item span,
.ranking-item small {
    color: var(--color-text-secondary);
    font-size: 13px;
}

.bar-wrap {
    width: 100%;
    height: 8px;
    overflow: hidden;
    border-radius: var(--radius-pill);
    background: #eef2ff;
}

.bar-wrap span {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: var(--color-primary);
}

.bar-wrap.risk {
    background: #fee2e2;
}

.bar-wrap.risk span {
    background: var(--color-error);
}

/* =========================
   Modal
========================= */

.modal-backdrop {
    position: fixed;
    inset: 0;
    display: grid;
    place-items: center;
    padding: 24px;
    background: rgba(15, 23, 42, 0.48);
    z-index: 50;
}

.admin-modal {
    width: 100%;
    max-width: 480px;
    padding: 24px;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 18px;
}

.modal-header h2 {
    margin: 0;
}

.close-btn {
    width: 36px;
    height: 36px;
    border: 0;
    border-radius: var(--radius-pill);
    background: #f8fafc;
    color: var(--color-text-secondary);
    font-size: 24px;
    cursor: pointer;
}

.modal-form {
    display: grid;
    gap: 10px;
}

.modal-form label {
    font-weight: 700;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 14px;
}


/* =========================
   Responsive - Large Screens
========================= */

@media (min-width: 1440px) {
    .content-grid {
        grid-template-columns: 1fr 3fr;
    }

    #home-map,
    #map-container {
        height: 850px;
    }
}


/* =========================
   Responsive - Medium Screens
========================= */

@media (max-width: 1200px) {
    /* .page-shell {
        flex-direction: column;
    } */

    .content-grid {
        grid-template-columns: 2fr;
    }

    #home-map,
    #map-container {
        height: 400px;
    }

    .brand-section {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    }

    .sidebar-toggle {
        margin-left: auto;
        border: 0;
        background: transparent;
        color: var(--color-text-secondary);
        font-size: 20px;
        cursor: pointer;
    }

    .main-content {
        padding: 18px;
        padding-bottom: 110px;
    }

    .topbar,
    .results-header,
    .route-card-top,
    .route-footer,
    .map-header {
        flex-direction: column;
        align-items: flex-start;
    }
}


/* =========================
Responsive - Below 1440px
========================= */

@media (max-width: 1440px) {

    #home-map,
    #map-container {
        height: 450px;
    }
}
</style>