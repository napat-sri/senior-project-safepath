<template>
    <SafePathNavDrawer subtitle="Admin" :width="300" :items="adminMenu">
        <!-- <v-divider class="my-2" />
            <v-list-item title="Users" prepend-icon="mdi-account-group" @click="scrollToSection('users')" />
            <v-list-item title="Search Logs" prepend-icon="mdi-magnify" @click="scrollToSection('search-logs')" />
            <v-list-item title="Incidents" prepend-icon="mdi-alert-circle" @click="scrollToSection('incidents')" />
            <v-list-item title="Location Insights" prepend-icon="mdi-map-marker"
                @click="scrollToSection('locations')" /> -->
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
                <v-tabs-window-item value="Incident Logs">
                    <SafePathAdminIncidentLogs />
                </v-tabs-window-item>
                <v-tabs-window-item value="User Management">
                    <SafePathAdminUserManagement />
                </v-tabs-window-item>
                <v-tabs-window-item value="Login Logs">
                    <SafePathAdminLoginLogs />
                </v-tabs-window-item>
            </v-tabs-window>
        </v-container>
    </v-main>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import SafePathNavDrawer from '../../components/SafePathNavDrawer.vue';
import SafePathAdminOverview from '../admin/SafePathAdminOverview.vue';
import SafePathAdminSearchLogs from '../admin/SafePathAdminSearchLogsView.vue';
import SafePathAdminIncidentLogs from '../admin/SafePathAdminIncidentLogsView.vue';
import SafePathAdminUserManagement from '../admin/SafePathAdminUserManagement.vue';
import SafePathAdminLoginLogs from './SafePathAdminLoginLogsView.vue';

const router = useRouter();

const adminMenu = [
    { title: 'Home', icon: 'mdi-home', to: '/home' },
    { title: 'Profile', icon: 'mdi-account', to: '/profile' },
    { title: 'Report Incident', icon: 'mdi-alert', to: '/incident' },
    { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/overview' },
];

const tab = ref('Overview')

const items = [
    'Overview',
    'Search Logs',
    'Incident Logs',
    'User Management',
    'Login Logs',
];
</script>

<style scoped>
.app-shell {
    min-height: 100vh;
}
</style>