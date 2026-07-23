<template>
    <v-layout>
        <v-main>
            <v-container fluid class="pa-4 pa-md-6">
                <v-card id="users" rounded="lg" elevation="2" class="mb-3">
                    <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                        User Management
                        <v-btn variant="outlined" color="primary" @click="openUserModal()"
                            prepend-icon="mdi-account-plus">
                            Add User
                        </v-btn>
                    </v-card-title>
                    <v-card-subtitle class="text-medium-emphasis mb-2">
                        Manage user roles and account status.
                    </v-card-subtitle>
                    <v-card-text>
                        <v-data-table>
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
                                        <div class="d-flex align-center ga-2">
                                            <v-avatar size="28" color="primary" variant="tonal">{{ user.initial
                                            }}</v-avatar>
                                            <div>
                                                <div class="font-weight-medium">{{ user.name }}</div>
                                                <div class="text-caption text-medium-emphasis">{{ user.email }}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>{{ user.role }}</td>
                                    <td>{{ user.provider }}</td>
                                    <td>
                                        <v-chip size="small" :color="user.status === 'Active' ? 'success' : 'warning'"
                                            variant="tonal">{{ user.status }}</v-chip>
                                    </td>
                                    <td>{{ user.lastLogin }}</td>
                                    <td>
                                        <div class="d-flex ga-2">
                                            <v-btn size="small" variant="tonal" color="primary"
                                                @click="openUserModal(user)">Edit</v-btn>
                                            <v-btn size="small" variant="text" color="error"
                                                @click="deactivateUser(user.id)">Deactivate</v-btn>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </v-data-table>
                    </v-card-text>
                </v-card>
            </v-container>
        </v-main>
    </v-layout>

    <v-dialog v-model="showUserModal" max-width="560">
        <v-card rounded="lg" color="info">
            <template v-slot:title>
                <span class="font-weight-black">{{ selectedUser ? 'Update user access' : 'Add new user' }}</span>
            </template>
            <v-card-text class="bg-surface-light pt-4">
                <v-text-field v-model="userForm.name" label="Name" variant="outlined" class="mb-3" />
                <v-text-field v-model="userForm.email" label="Email" variant="outlined" class="mb-3" />
                <v-select v-model="userForm.role" :items="['Admin', 'Moderator', 'User']" label="Role"
                    variant="outlined" class="mb-3" />
                <v-select v-model="userForm.status" :items="['Active', 'Suspended', 'Pending']" label="Status"
                    variant="outlined" />
            </v-card-text>
            <v-card-actions class="bg-surface-light pt-4">
                <v-spacer />
                <v-btn variant="text" @click="closeUserModal">Cancel</v-btn>
                <v-btn color="primary" @click="saveUser">Save User</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import SafePathNavDrawer from '../../components/SafePathNavDrawer.vue';
import SafePathAdminSearchLogs from '../admin/SafePathAdminSearchLogsView.vue'

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
    'User Managemant',
]

const overviewStats = ref([
    {
        label: 'Total Users',
        value: '1,248',
        icon: 'mdi-account-group',
        trend: '+12 this week',
        trendType: 'positive'
    },
    {
        label: 'Route Searches',
        value: '8,920',
        icon: 'mdi-magnify',
        trend: '+18% today',
        trendType: 'positive'
    },
    {
        label: 'Incident Reports',
        value: '312',
        icon: 'mdi-alert-circle',
        trend: '24 pending',
        trendType: 'warning'
    },
    {
        label: 'Top Search Place',
        value: 'Alexanderplatz',
        icon: 'mdi-map-marker',
        trend: '842 searches',
        trendType: 'neutral'
    }
]);

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
]);

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
]);

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
]);

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
]);

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
]);

const userForm = ref({
    name: '',
    email: '',
    role: 'User',
    status: 'Active'
});

const filteredSearchLogs = computed(() => {
    const query = searchLogFilter.value.trim().toLowerCase();

    if (!query) {
        return searchLogs.value;
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
            .includes(query);
    });
});

const filteredIncidents = computed(() => {
    if (incidentStatusFilter.value === 'All') {
        return incidentReports.value;
    }

    return incidentReports.value.filter((incident) => incident.status === incidentStatusFilter.value);
});

const goToHome = () => {
    router.push('/home');
};

const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
};

const getSafetyClass = (score) => {
    if (score >= 80) {
        return 'safe';
    }

    if (score >= 60) {
        return 'medium';
    }

    return 'risk';
};

const openUserModal = (user = null) => {
    selectedUser.value = user;

    if (user) {
        userForm.value = {
            name: user.name,
            email: user.email,
            role: user.role,
            status: user.status
        };
    } else {
        userForm.value = {
            name: '',
            email: '',
            role: 'User',
            status: 'Active'
        };
    }

    showUserModal.value = true;
};

const closeUserModal = () => {
    showUserModal.value = false;
    selectedUser.value = null;
};

const saveUser = () => {
    if (selectedUser.value) {
        const index = users.value.findIndex((user) => user.id === selectedUser.value.id);

        if (index !== -1) {
            users.value[index] = {
                ...users.value[index],
                name: userForm.value.name,
                email: userForm.value.email,
                role: userForm.value.role,
                status: userForm.value.status,
                initial: userForm.value.name.charAt(0).toUpperCase() || 'U'
            };
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
        });
    }

    closeUserModal();
};

const deactivateUser = (userId) => {
    const user = users.value.find((item) => item.id === userId);

    if (user) {
        user.status = 'Suspended';
    }
};

const updateIncidentStatus = (incidentId, status) => {
    const incident = incidentReports.value.find((item) => item.id === incidentId);

    if (incident) {
        incident.status = status;
    }
};

const refreshDashboard = () => {
    console.log('Refresh admin dashboard data');
};

const exportReport = () => {
    console.log('Export admin report');
};
</script>

<style scoped>
</style>