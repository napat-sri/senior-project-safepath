<template>
    <v-layout class="app-shell">
        <SafePathNavDrawer subtitle="Admin" :width="300" :items="adminMenu">
            <!-- <v-divider class="my-2" />
            <v-list-item title="Users" prepend-icon="mdi-account-group" @click="scrollToSection('users')" />
            <v-list-item title="Search Logs" prepend-icon="mdi-magnify" @click="scrollToSection('search-logs')" />
            <v-list-item title="Incidents" prepend-icon="mdi-alert-circle" @click="scrollToSection('incidents')" />
            <v-list-item title="Location Insights" prepend-icon="mdi-map-marker"
                @click="scrollToSection('locations')" /> -->
            <v-divider class="my-2" />
            <v-list-item title="User App" prepend-icon="mdi-map" @click="goToHome" />
        </SafePathNavDrawer>

        <v-main>
            <v-container fluid class="pa-4 pa-md-6">
                <v-card rounded="lg" elevation="2" class="mb-3">
                    <v-card-text class="d-flex justify-space-between align-center flex-wrap ga-3">
                        <div>
                            <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                                Admin Dashboard
                            </v-card-title>
                            <v-card-subtitle class="text-medium-emphasis mb-2">
                                Review activity, manage users, moderate incidents, and understand safety demand across
                                Berlin.
                            </v-card-subtitle>
                        </div>
                        <div class="d-flex ga-2">
                            <v-btn variant="outlined" @click="refreshDashboard" prepend-icon="mdi-refresh">
                                Refresh
                            </v-btn>
                            <v-btn variant="outlined" color="primary" @click="exportReport" prepend-icon="mdi-download">
                                Export Report
                            </v-btn>
                        </div>
                    </v-card-text>
                </v-card>

                <v-tabs v-model="tab">
                    <v-tab v-for="item in items" :key="item" :text="item" :value="item"></v-tab>
                </v-tabs>

                <v-tabs-window v-model="tab">
                    <v-tabs-window-item value="Overview">
                        <SafePathAdminOverview />
                    </v-tabs-window-item>
                    <v-tabs-window-item value="Search Logs">
                        <SafePathAdminSearchLogs />
                    </v-tabs-window-item>
                    <v-tabs-window-item value="User Management">
                        <SafePathAdminUserManagement />
                    </v-tabs-window-item>
                </v-tabs-window>

                <!-- <v-card id="incidents" rounded="lg" elevation="2" class="mb-4">
                    <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                        Incident Report Management
                        <v-select v-model="incidentStatusFilter" :items="['All', 'Pending', 'Approved', 'Rejected']"
                            density="compact" variant="outlined" hide-details style="max-width: 200px" />
                    </v-card-title>
                    <v-card-subtitle class="text-medium-emphasis mb-2">
                        Review incidents before they influence public insights.
                    </v-card-subtitle>
                    <v-card-text>
                        <v-card v-for="incident in filteredIncidents" :key="incident.id" variant="outlined" class="mb-3"
                            rounded="lg">
                            <v-card-text>
                                <div class="d-flex justify-space-between align-center flex-wrap ga-3 mb-2">
                                    <h3 class="text-subtitle-1">{{ incident.type }}</h3>
                                    <v-chip size="small"
                                        :color="incident.status === 'Approved' ? 'success' : incident.status === 'Rejected' ? 'error' : 'warning'"
                                        variant="tonal">
                                        {{ incident.status }}
                                    </v-chip>
                                </div>

                                <p class="text-body-2 text-medium-emphasis mb-2">
                                    {{ incident.location }} · {{ incident.date }} · {{ incident.time }}
                                </p>
                                <p class="text-body-2 mb-3">{{ incident.description }}</p>

                                <div class="d-flex justify-space-between align-center flex-wrap ga-3">
                                    <span class="text-caption text-medium-emphasis">
                                        {{ incident.evidenceCount }} evidence files · Submitted by {{
                                            incident.submittedBy }}
                                    </span>
                                    <div class="d-flex ga-2">
                                        <v-btn size="small" variant="outlined" color="error"
                                            @click="updateIncidentStatus(incident.id, 'Rejected')">
                                            Reject
                                        </v-btn>
                                        <v-btn size="small" color="primary"
                                            @click="updateIncidentStatus(incident.id, 'Approved')">
                                            Approve
                                        </v-btn>
                                    </div>
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-card-text>
                </v-card> -->
            </v-container>
        </v-main>
    </v-layout>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import SafePathNavDrawer from '../../components/SafePathNavDrawer.vue';
import SafePathAdminOverview from '../admin/SafePathAdminOverview.vue';
import SafePathAdminSearchLogs from '../admin/SafePathAdminSearchLogsView.vue';
import SafePathAdminUserManagement from '../admin/SafePathAdminUserManagement.vue';

const router = useRouter();

const adminMenu = [
    { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/overview' },
    { title: 'Profile', icon: 'mdi-account', to: '/profile' },
    { title: 'Report Incident', icon: 'mdi-alert', to: '/incident' }
];

const searchLogFilter = ref('');
const incidentStatusFilter = ref('All');
const showUserModal = ref(false);
const selectedUser = ref(null);

const tab = ref('Overview')

const items = [
    'Overview',
    'Search Logs',
    'User Management',
];

const goToHome = () => {
    router.push('/home');
};

const refreshDashboard = () => {
    console.log('Refresh admin dashboard data');
};

const exportReport = () => {
    console.log('Export admin report');
};
</script>

<style scoped>
.app-shell {
    min-height: 100vh;
}

.overview-stat-card {
    height: 100%;
    border: 1px solid rgba(0, 0, 0, 0.08);
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.96) 100%);
    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
    overflow: hidden;
}

.overview-stat-card__content {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 22px;
}

.overview-stat-card__avatar {
    flex: 0 0 auto;
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.45);
}

.overview-stat-card__copy {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.overview-stat-card__label {
    font-size: 0.9rem;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.66);
    letter-spacing: 0.01em;
}

.overview-stat-card__value {
    font-size: large;
    line-height: 1.05;
    font-weight: 800;
    word-break: break-word;
    margin-top: 5px;
}

.overview-stat-card__chip {
    align-self: flex-start;
    font-weight: 700;
    margin-top: 10px;
}
</style>