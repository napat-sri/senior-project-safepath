<template>
    <v-layout>
        <v-main>
            <v-container fluid class="pa-4 pa-md-6">
                <v-card id="search-logs" rounded="lg" elevation="2" class="mb-3">
                    <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                        Incident Report Logs
                        <div class="d-flex align-center ga-2">
                            <v-text-field v-model="searchIncidentFilter" label="Filter incident logs" density="compact"
                                variant="outlined" hide-details prepend-inner-icon="mdi-magnify" style="width: 300px"
                                clearable />
                            <v-btn icon="mdi-refresh" variant="text" :loading="incidentsLoading"
                                aria-label="Refresh incident logs" @click="loadIncidents" />
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
                        <v-data-table :headers="incidentHeaders" :items="filteredIncidents" :loading="incidentsLoading">
                            <template #item.incidentType="{ item }">
                                <v-chip :color="incidentTypeColor(item.incidentType)" size="small" variant="flat" label>
                                    {{ item.incidentType }}
                                </v-chip>
                            </template>
                            <template v-slot:item.action="{ item }">
                                <v-tooltip text="View details">
                                    <template v-slot:activator="{ props }">
                                        <v-btn color="primary" icon="mdi-eye" size="small" variant="text"
                                            v-bind="props" @click="openIncidentModal(item)"></v-btn>
                                    </template>
                                </v-tooltip>
                            </template>
                        </v-data-table>
                    </v-card-text>
                </v-card>
            </v-container>
        </v-main>
    </v-layout>

    <v-dialog v-model="showIncidentModal" max-width="500">
        <v-card rounded="lg">
            <v-card-title class="d-flex justify-space-between align-center">
                <div class="text-headline-small text-medium-emphasis ps-2">
                    Incident Details
                </div>

                <v-btn icon="mdi-close" variant="text" @click="closeIncidentModal"></v-btn>
            </v-card-title>
            <v-divider class="mb-2"></v-divider>
            <v-card-subtitle class="ma-3">
                <v-row>
                    <v-col cols="12" md="6"><v-icon>mdi-account</v-icon>&nbsp;Reporter Name</v-col>
                    <v-col cols="12" md="6">{{ incidentDetail?.reporterName }}</v-col>
                    <v-col cols="12" md="6"><v-icon>mdi-clock</v-icon>&nbsp;Date-Time</v-col>
                    <v-col cols="12" md="6">{{ incidentDetail?.date }}, {{ incidentDetail?.time }}</v-col>
                    <v-col cols="12" md="6"><v-icon>mdi-map-marker</v-icon>&nbsp;Location</v-col>
                    <v-col cols="12" md="6" class="text-wrap" style="overflow-wrap: anywhere;">
                        {{ incidentDetail?.location }}
                    </v-col>
                    <v-col cols="12" md="6"><v-icon>mdi-tag</v-icon>&nbsp;Incident Type</v-col>
                    <v-chip :color="incidentTypeColor(incidentDetail?.incidentType)"
                        size="small" variant="flat" label>
                        {{ incidentDetail?.incidentType }}
                    </v-chip>
                    <v-col cols="12" md="6"><v-icon>mdi-text-long</v-icon>&nbsp;Details</v-col>
                    <v-col cols="12" md="6" class="text-wrap" style="overflow-wrap: anywhere;">
                        {{ incidentDetail?.details }}
                    </v-col>
                </v-row>
            </v-card-subtitle>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import SafePathNavDrawer from '../../components/SafePathNavDrawer.vue';
import { adminService, incidentService } from '../../services/api.js';
import { incidentTypeColor } from '../../data/incidentTypes.js';

const router = useRouter();

const adminMenu = [
    { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/overview' },
    { title: 'Profile', icon: 'mdi-account', to: '/profile' },
    { title: 'Report Incident', icon: 'mdi-alert', to: '/incident' }
];

const searchIncidentFilter = ref('');
const showIncidentModal = ref(false);
const incidentDetail = ref(null);

const tab = ref('Overview')

const items = [
    'Overview',
    'Search Logs',
    'User Managemant',
]

const incidentReports = ref([]);
const incidentsLoading = ref(false);
const incidentsError = ref('');

const incidentHeaders = [
    { title: 'Reporter', key: 'reporterName' },
    { title: 'Date', key: 'date' },
    { title: 'Time', key: 'time' },
    { title: 'Location', key: 'location', width: '40%' },
    { title: 'Type', key: 'incidentType' },
    { title: 'Action', key: 'action' },
];

const loadIncidents = async () => {
    incidentsLoading.value = true;
    incidentsError.value = '';
    try {
        const { data } = await incidentService.listAdmin();
        incidentReports.value = data.incidents || [];
    } catch (err) {
        incidentsError.value = err.response?.data?.detail || 'Could not load incident reports.';
        incidentReports.value = [];
    } finally {
        incidentsLoading.value = false;
    }
};
onMounted(loadIncidents);

// Optional client-side text search using the existing searchIncidentFilter box.
const filteredIncidents = computed(() => {
    const q = searchIncidentFilter.value.trim().toLowerCase();
    if (!q) return incidentReports.value;
    return incidentReports.value.filter((i) =>
        [i.incidentType, i.location, i.reporterName, i.date, i.time, i.details]
            .join(' ').toLowerCase().includes(q));
});

const openIncidentModal = (report) => {
    incidentDetail.value = report;
    showIncidentModal.value = true;
};

const closeIncidentModal = () => {
    showIncidentModal.value = false;
    incidentDetail.value = null;
};

</script>

<style scoped></style>