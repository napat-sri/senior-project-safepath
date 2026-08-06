<template>
    <v-container fluid class="pa-4 pa-md-6">
        <v-row class="mb-5">
            <v-col cols="12" sm="6" lg="4" v-for="item in overviewStats" :key="item.label">
                <v-col cols="12" md="6">
                    <v-card rounded="lg" class="mx-auto" :subtitle=item.label>
                        <template v-slot:prepend>
                            <v-avatar color="primary" size="24">
                                <v-icon :icon=item.icon size="16"></v-icon>
                            </v-avatar>
                        </template>
                        <v-card-text>
                            <div class="overview-stat-card__value">{{ item.value }}
                                <v-chip class="overview-stat-card__chip" size="small"
                                    :color="item.trendType === 'positive' ? 'success' : item.trendType === 'error' ? 'error' : ''"
                                    variant="tonal" rounded="lg" v-if="item.trend != ''">
                                    {{ item.trend }}
                                </v-chip>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-col>
        </v-row>

        <v-card id="locations" rounded="lg" elevation="2" class="mb-4">
            <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                Location Insights
            </v-card-title>
            <v-card-subtitle class="text-medium-emphasis mb-2">
                Most searched and most reported places across Berlin.
            </v-card-subtitle>
            <v-card-text>
                <v-row>
                    <!-- Most Searched Places -->
                    <v-col cols="12" md="6">
                        <v-card variant="outlined" rounded="lg">
                            <v-card-title>Most Searched Places</v-card-title>
                            <v-divider class="mb-2"></v-divider>
                            <v-card-text>
                                <div v-if="searchLogsLoading" class="text-caption text-medium-emphasis">Loading…</div>
                                <div v-else-if="searchLogsError" class="text-caption text-error">{{ searchLogsError }}
                                </div>
                                <div v-else-if="!mostSearchedPlaces.length" class="text-caption text-medium-emphasis">
                                    No route searches yet.
                                </div>
                                <template v-else>
                                    <div v-for="search in mostSearchedPlaces" :key="search.name" class="mb-6">
                                        <div class="d-flex justify-space-between mb-4">
                                            <strong>{{ search.name }}</strong>
                                            <span class="text-caption text-medium-emphasis">{{ search.count }}
                                                searches</span>
                                        </div>
                                        <v-progress-linear :model-value="search.percent" color="primary" height="8"
                                            rounded />
                                    </div>
                                </template>
                            </v-card-text>
                        </v-card>
                    </v-col>


                    <!-- Most Incident Report Places -->
                    <v-col cols="12" md="6">
                        <v-card variant="outlined" rounded="lg">
                            <v-card-title>Most Incident Report Places</v-card-title>
                            <v-divider class="mb-2"></v-divider>
                            <v-slide-group v-model="selectedTypes" class="mt-3" selected-class="bg-warning" multiple
                                show-arrows>
                                <v-slide-group-item v-for="item in incidentTypes" :key="item" :value="item" :text="item"
                                    v-slot="{ isSelected, toggle, selectedClass }">
                                    <v-btn :color="isSelected ? 'warning' : undefined" rounded
                                        :class="['ma-1', selectedClass]" @click="toggle">
                                        {{ item }}
                                    </v-btn>
                                </v-slide-group-item>
                            </v-slide-group>
                            <v-card-text>
                                <div v-for="report in mostReportedPlaces" :key="report.name" class="mb-4">
                                    <div class="d-flex justify-space-between mb-1">
                                        <strong>{{ report.name }}</strong>
                                        <span class="text-caption text-medium-emphasis">{{ report.count }}
                                            reports</span>
                                    </div>
                                    <v-card-subtitle v-if="selectedTypes.length != 1"
                                        class="text-caption text-medium-emphasis mb-1">
                                        <b>Most common:</b> {{ report.topIncident }}
                                    </v-card-subtitle>
                                    <v-progress-linear :model-value="report.percent" color="error" height="8" rounded />
                                </div>
                            </v-card-text>
                            <div v-if="incidentsLoading" class="text-caption text-medium-emphasis">Loading…
                            </div>
                            <div v-else-if="incidentsError" class="text-caption text-error">{{ incidentsError }}
                            </div>
                            <div v-else-if="!mostReportedPlaces.length" class="text-caption text-medium-emphasis">
                                No incident reports yet.
                            </div>
                        </v-card>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </v-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import SafePathNavDrawer from '../../components/SafePathNavDrawer.vue';
import { incidentService, adminService } from '../../services/api.js';
import { incidentTypeColor } from '../../data/incidentTypes.js';

const router = useRouter();

const tab = ref('Overview')

// --- users ---
const users = ref([]);
const usersLoading = ref(false);
const usersError = ref('');

const loadUsers = async () => {
    usersLoading.value = true;
    usersError.value = '';
    try {
        // high limit so the total-count stat isn't capped at the backend default (100)
        const { data } = await adminService.listUsers({ limit: 10000 });
        users.value = data.users || [];
    } catch (err) {
        usersError.value = err.response?.data?.detail || 'Could not load users.';
        users.value = [];
    } finally {
        usersLoading.value = false;
    }
};

// --- shared helpers ---
// First segment of the display name, e.g. "Zoologischer Garten".
const placeKey = (location) => (location || '').split(',')[0].trim();
// A usable place name = not empty, not "Unknown", not a raw "lat, lng" coordinate.
const isRealPlace = (name) => !!name && name !== 'Unknown' && !/^-?\d+(\.\d+)?$/.test(name);

// --- incidents ---
const incidents = ref([]);
const incidentsLoading = ref(false);
const incidentsError = ref('');
const selectedTypes = ref([]);          // bound to the chip group; [] = all types
const incidentTypes = [
    'Harassment',
    'Theft',
    'Unsafe area',
    'Suspicious activity',
    'Transport issue',
    'Other'
];

const loadIncidents = async () => {
    incidentsLoading.value = true;
    incidentsError.value = '';
    try {
        // high limit so the total-count stat isn't capped at the backend default (100)
        const { data } = await incidentService.listAdmin({ limit: 10000 });
        incidents.value = data.incidents || [];
    } catch (err) {
        incidentsError.value = err.response?.data?.detail || 'Could not load incident reports.';
        incidents.value = [];
    } finally {
        incidentsLoading.value = false;
    }
};

const mostReportedPlaces = computed(() => {
    const types = selectedTypes.value;
    // No chips selected => all types.
    const rows = types.length
        ? incidents.value.filter((i) => types.includes(i.incidentType))
        : incidents.value;

    // Group by first segment of location.
    const byPlace = new Map();   // name -> { name, count, typeCounts }
    for (const i of rows) {
        const name = placeKey(i.location);
        if (!name) continue;
        if (!byPlace.has(name)) byPlace.set(name, { name, count: 0, typeCounts: {} });
        const p = byPlace.get(name);
        p.count += 1;
        p.typeCounts[i.incidentType] = (p.typeCounts[i.incidentType] || 0) + 1;
    }

    const places = [...byPlace.values()]
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

    const max = places.length ? places[0].count : 0;
    return places.map((p) => ({
        name: p.name,
        count: p.count,
        percent: max ? Math.round((p.count / max) * 100) : 0,
        // most common incident type at this place (for the sub-label)
        topIncident: Object.entries(p.typeCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || '',
    }));
});

// --- route-search logs ---
const searchLogs = ref([]);
const searchLogsLoading = ref(false);
const searchLogsError = ref('');

const loadSearchLogs = async () => {
    searchLogsLoading.value = true;
    searchLogsError.value = '';
    try {
        // last 7 days, generous limit
        const { data } = await adminService.searchLogs({ minutes: 10080, limit: 100 });
        searchLogs.value = data.logs || [];
        console.log(data)
    } catch (err) {
        searchLogsError.value = err.response?.data?.detail || 'Could not load search logs.';
        searchLogs.value = [];
    } finally {
        searchLogsLoading.value = false;
    }
};

onMounted(() => {
    loadUsers();
    loadIncidents();
    loadSearchLogs();
});

const mostSearchedPlaces = computed(() => {
    const byPlace = new Map();   // name -> count
    for (const log of searchLogs.value) {
        for (const raw of [log.start, log.destination]) {
            const name = placeKey(raw);
            if (!isRealPlace(name)) continue;   // skip Unknown / coordinate fallbacks
            byPlace.set(name, (byPlace.get(name) || 0) + 1);
        }
    }
    const places = [...byPlace.entries()]
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 6);

    const max = places.length ? places[0].count : 0;
    return places.map((p) => ({
        name: p.name,
        count: p.count,
        percent: max ? Math.round((p.count / max) * 100) : 0,
    }));
});

// --- Overview stats ---
const totalUsers = computed(() => users.value.length);
const totalIncidents = computed(() => incidents.value.length);
const totalSearches = computed(() => searchLogs.value.length);

const overviewStats = computed(() => [
    {
        label: 'Total Users',
        value: usersLoading.value ? '…' : totalUsers.value.toLocaleString(),
        icon: 'mdi-account-group',
        trend: '',
        trendType: ''
    },
    {
        label: 'Route Searches',
        value: searchLogsLoading.value ? '…' : totalSearches.value.toLocaleString(),
        icon: 'mdi-magnify',
        trend: '',
        trendType: '',
    },
    {
        label: 'Incident Reports',
        value: incidentsLoading.value ? '…' : totalIncidents.value.toLocaleString(),
        icon: 'mdi-alert-circle',
        trend: '',
        trendType: '',
    },
]);
</script>

<style scoped>
.overview-stat-card__value {
    font-size: xx-large;
    line-height: 1.05;
    font-weight: 700;
    word-break: break-word;
    margin-top: 5px;
}

.overview-stat-card__chip {
    /* align-self: flex-start; */
    font-weight: 600;
    margin-left: 10px;
}
</style>