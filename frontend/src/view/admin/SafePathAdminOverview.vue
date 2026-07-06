<template>
    <v-layout>
        <v-main>
            <v-container fluid class="pa-4 pa-md-6">
                <v-row class="mb-5">
                    <v-col cols="12" sm="6" lg="3" v-for="item in overviewStats" :key="item.label">
                        <v-card rounded="xl" elevation="0" max-height="100%">
                            <v-card-text class="overview-stat-card__content">
                                <v-avatar size="52" color="primary" variant="outlined">
                                    <v-icon :icon="item.icon" size="24" />
                                </v-avatar>
                                <div>
                                    <span class="text-medium-emphasis">{{ item.label }}</span>
                                    <div class="overview-stat-card__value">{{ item.value }}</div>
                                    <v-chip class="overview-stat-card__chip" size="small"
                                        :color="item.trendType === 'positive' ? 'success' : item.trendType === 'warning' ? 'warning' : 'primary'"
                                        variant="outlined">
                                        {{ item.trend }}
                                    </v-chip>
                                </div>
                            </v-card-text>
                        </v-card>
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
                                    <v-card-text>
                                        <div v-for="place in mostReportedPlaces" :key="place.name" class="mb-4">
                                            <div class="d-flex justify-space-between mb-1">
                                                <strong>{{ place.name }}</strong>
                                                <span class="text-caption text-medium-emphasis">{{ place.count }}
                                                    reports</span>
                                            </div>
                                            <p class="text-caption text-medium-emphasis mb-2">{{ place.topIncident }}
                                            </p>
                                            <v-progress-linear :model-value="place.percent" color="error" height="8"
                                                rounded />
                                        </div>
                                    </v-card-text>
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
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const tab = ref('Overview')

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
    font-size: x-large;
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