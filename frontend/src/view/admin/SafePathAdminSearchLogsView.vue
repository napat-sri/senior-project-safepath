<template>
    <v-container fluid class="pa-4 pa-md-6">
        <v-card id="search-logs" rounded="lg" elevation="2" class="mb-3">
            <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                User Search Logs
                <div class="d-flex align-center ga-2">
                    <v-text-field v-model="searchLogFilter" label="Filter search logs" density="compact"
                        variant="outlined" hide-details prepend-inner-icon="mdi-magnify" style="width: 300px" />
                    <v-btn icon="mdi-refresh" variant="text" :loading="logsLoading" aria-label="Refresh search logs"
                        @click="loadSearchLogs" />
                </div>
            </v-card-title>
            <v-card-subtitle class="text-medium-emphasis mb-2">
                Track route searches with safety score and status.
            </v-card-subtitle>
            <v-progress-linear v-if="logsLoading" indeterminate color="primary" />
            <v-card-text>
                <v-alert v-if="logsError" type="error" variant="tonal" density="compact" class="mb-3">
                    {{ logsError }}
                </v-alert>
<v-data-table :headers="searchLogHeaders" :items="filteredSearchLogs" :loading="logsLoading">
  <!-- User = avatar + name + email -->
  <template #item.user="{ item }">
    <div class="d-flex align-center ga-2">
      <v-avatar size="28" color="primary" variant="tonal">{{ item.userInitial }}</v-avatar>
      <div>
        <div class="font-weight-medium">{{ item.user }}</div>
        <div class="text-caption text-medium-emphasis">{{ item.email }}</div>
      </div>
    </div>
  </template>

  <!-- Safety score chip -->
  <template #item.safetyScore="{ item }">
    <v-chip size="small" variant="tonal"
      :color="getSafetyClass(item.safetyScore) === 'safe' ? 'success'
             : getSafetyClass(item.safetyScore) === 'medium' ? 'warning' : 'error'">
      {{ item.safetyScore }}/100
    </v-chip>
  </template>

  <!-- Status chip -->
  <template #item.status="{ item }">
    <v-chip size="small" color="primary" variant="tonal">{{ item.status }}</v-chip>
  </template>

  <!-- Empty state -->
  <template #no-data>
    <div class="text-center text-medium-emphasis py-6">
      {{ logsError ? 'No logs to show.' : 'No route searches yet.' }}
    </div>
  </template>
</v-data-table>            </v-card-text>
        </v-card>
    </v-container>

    <v-dialog v-model="showUserModal" max-width="560">
        <v-card rounded="lg">
            <v-card-title>{{ selectedUser ? 'Update user access' : 'Add new user' }}</v-card-title>
            <v-card-text>
                <v-text-field v-model="userForm.name" label="Name" variant="outlined" class="mb-3" />
                <v-text-field v-model="userForm.email" label="Email" variant="outlined" class="mb-3" />
                <v-select v-model="userForm.role" :items="['Admin', 'Moderator', 'User']" label="Role"
                    variant="outlined" class="mb-3" />
                <v-select v-model="userForm.status" :items="['Active', 'Suspended', 'Pending']" label="Status"
                    variant="outlined" />
            </v-card-text>
            <v-card-actions>
                <v-spacer />
                <v-btn variant="text" @click="closeUserModal">Cancel</v-btn>
                <v-btn color="primary" @click="saveUser">Save User</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import SafePathNavDrawer from '../../components/SafePathNavDrawer.vue';
import { adminService } from '../../services/api';

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

const searchLogHeaders = [
  { title: 'User', key: 'user' },
  { title: 'Start', key: 'start' },
  { title: 'Destination', key: 'destination' },
  { title: 'Date', key: 'date' },
  { title: 'Time', key: 'time' },
  { title: 'Safety Score', key: 'safetyScore' },
  { title: 'Status', key: 'status', sortable: false },
];

// Real route-search logs, fetched from the backend (Langfuse-sourced).
const searchLogs = ref([]);
const logsLoading = ref(false);
const logsError = ref('');

const loadSearchLogs = async () => {
    logsLoading.value = true;
    logsError.value = '';

    try {
        const { data } = await adminService.searchLogs();
        searchLogs.value = data.logs ?? [];
    } catch (err) {
        logsError.value =
            err.response?.data?.detail ||
            'Could not load search logs. Please try again.';
        searchLogs.value = [];
    } finally {
        logsLoading.value = false;
    }
};

onMounted(loadSearchLogs);

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
</script>

<style scoped></style>