<template>
    <v-layout>
        <v-main>
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
                            <v-col cols="12" md="6">
                                <v-card variant="outlined" rounded="lg">
                                    <v-card-title>Most Searched Places</v-card-title>
                                    <v-card-text>
                                        <div v-for="place in mostSearchedPlaces" :key="place.name" class="mb-4">
                                            <div class="d-flex justify-space-between mb-1">
                                                <strong>{{ place.name }}</strong>
                                                <span class="text-caption text-medium-emphasis">{{ place.count }}
                                                    searches</span>
                                            </div>
                                            <p class="text-caption text-medium-emphasis mb-2">{{ place.type }}</p>
                                            <v-progress-linear :model-value="place.percent" color="primary" height="8"
                                                rounded />
                                        </div>
                                    </v-card-text>
                                </v-card>
                            </v-col>

                            <v-col cols="12" md="6">
                                <v-card variant="outlined" rounded="lg">
                                    <v-card-title>Most Incident Report Places</v-card-title>
                                    <v-divider class="mb-2"></v-divider>
                                    <v-chip-group v-model="selectedTypes" selected-class="text-warning" multiple
                                        class="mt-2">
                                        <v-chip v-for="item in incidentTypes" :key="item" :value="item"
                                            :text="item"></v-chip>
                                    </v-chip-group> <v-card-text>
                                        <div v-for="place in mostReportedPlaces" :key="place.name" class="mb-4">
                                            <div class="d-flex justify-space-between mb-1">
                                                <strong>{{ place.name }}</strong>
                                                <span class="text-caption text-medium-emphasis">{{ place.count }}
                                                    reports</span>
                                            </div>
                                            <v-card-subtitle v-if="selectedTypes.length != 1"
                                                class="text-caption text-medium-emphasis mb-1">
                                                <b>Most common:</b> {{ place.topIncident }}
                                            </v-card-subtitle>
                                            <v-progress-linear :model-value="place.percent" color="error" height="8"
                                                rounded />
                                        </div>
                                    </v-card-text>
                                    <div v-if="incidentsLoading" class="text-caption text-medium-emphasis">Loading…
                                    </div>
                                    <div v-else-if="incidentsError" class="text-caption text-error">{{ incidentsError }}
                                    </div>
                                    <div v-else-if="!mostReportedPlaces.length"
                                        class="text-caption text-medium-emphasis">
                                        No incident reports yet.
                                    </div>
                                </v-card>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>
            </v-container>
        </v-main>
    </v-layout>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { incidentService } from '../../services/api.js';
import { incidentTypeColor } from '../../data/incidentTypes.js';

const router = useRouter();

const tab = ref('Overview')

const incidentTypes = [
    'Harassment',
    'Theft',
    'Unsafe area',
    'Suspicious activity',
    'Transport issue',
    'Other'
];

const incidents = ref([]);              // raw rows from the API
const incidentsLoading = ref(false);
const incidentsError = ref('');
const selectedTypes = ref([]);          // bound to the chip group; [] = all types

// First segment of the display name, e.g. "Zoologischer Garten".
const placeKey = (location) => (location || '').split(',')[0].trim();

const loadIncidents = async () => {
    incidentsLoading.value = true;
    incidentsError.value = '';
    try {
        const { data } = await incidentService.listAdmin({ limit: 10000 });   // no status param
        incidents.value = data.incidents || [];
    } catch (err) {
        incidentsError.value = err.response?.data?.detail || 'Could not load incident reports.';
        incidents.value = [];
    } finally {
        incidentsLoading.value = false;
    }
};
onMounted(loadIncidents);

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

const totalIncidents = computed(() => incidents.value.length);

const overviewStats = computed(() => [
    { label: 'Total Users',   value: '1,248', icon: 'mdi-account-group', trend: '+12',  trendType: 'positive' },
    { label: 'Route Searches',value: '8,920', icon: 'mdi-magnify',       trend: '+18%', trendType: 'positive' },
    {
        label: 'Incident Reports',
        value: incidentsLoading.value ? '…' : totalIncidents.value.toLocaleString(),
        icon: 'mdi-alert-circle',
        trend: '',
        trendType: '',
    },
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
    gap: 8px;
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