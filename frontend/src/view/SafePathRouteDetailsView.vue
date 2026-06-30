<template>
    <v-layout class="app-shell">
        <SafePathNavDrawer />

        <v-main>
            <v-container fluid class="pa-4 pa-md-6">
                <v-card class="mb-4" rounded="lg" elevation="2">
                    <v-card-text class="d-flex flex-wrap ga-4 justify-space-between align-center">
                        <div>
                            <h2 class="text-h5 text-md-h4">Route Detailed Analysis</h2>
                            <p class="text-medium-emphasis mt-2">Inspect overall score, safety breakdown, and selected
                                route
                                map.</p>
                        </div>
                        <v-btn variant="tonal" color="primary" @click="goHome">Back to Search</v-btn>
                    </v-card-text>
                </v-card>

                <v-row>
                    <v-col cols="12">
                        <v-card rounded="lg" elevation="2">
                            <v-card-text>
                                <div class="d-flex justify-space-between align-center flex-wrap ga-3 mb-2">
                                    <div>
                                        <p class="text-overline text-medium-emphasis">Overall Safety</p>
                                        <h3 class="text-h5">{{ selectedRoute.name }}</h3>
                                    </div>
                                    <v-chip :style="scoreBadgeStyle(selectedRoute.safetyScore)" size="large">
                                        {{ selectedRoute.safetyScore }}/100
                                    </v-chip>
                                </div>

                                <p class="text-body-1 text-medium-emphasis mb-3">{{ selectedRoute.summary }}</p>

                                <v-progress-linear :model-value="selectedRoute.safetyScore"
                                    :color="selectedRoute.accentColor || getSafetyTone(selectedRoute.safetyScore).color"
                                    height="10" rounded />
                            </v-card-text>
                        </v-card>
                    </v-col>

                    <v-col cols="12" md="6">
                        <v-card rounded="lg" elevation="2" height="100%">
                            <v-card-title>Route Information</v-card-title>
                            <v-card-text>
                                <v-list lines="two">
                                    <v-list-item title="Distance covered" :subtitle="selectedRoute.distance" />
                                    <v-list-item title="Estimated duration" :subtitle="selectedRoute.duration" />
                                    <v-list-item title="Route type" :subtitle="selectedRoute.routeType" />
                                    <v-list-item title="Journey" :subtitle="displayJourney" />
                                </v-list>
                            </v-card-text>
                        </v-card>
                    </v-col>

                    <v-col cols="12" md="6">
                        <v-card rounded="lg" elevation="2" height="100%">
                            <v-card-title>Safety Score Breakdown</v-card-title>
                            <v-card-text>
                                <div v-for="item in selectedRoute.breakdown" :key="item.label" class="mb-4">
                                    <div class="d-flex justify-space-between mb-2">
                                        <span class="font-weight-medium">{{ item.label }}</span>
                                        <span>{{ item.score }}/100</span>
                                    </div>
                                    <v-progress-linear :model-value="item.score"
                                        :color="selectedRoute.accentColor || getSafetyTone(selectedRoute.safetyScore).color"
                                        height="8" rounded />
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-col>

                    <v-col cols="12">
                        <v-card rounded="lg" elevation="2">
                            <v-card-title class="d-flex justify-space-between align-center">
                                <div>
                                    <h3 class="text-h6">Navigation Map</h3>
                                    <p class="text-body-2 text-medium-emphasis">The selected route is highlighted with
                                        the
                                        analysis safety color.</p>
                                </div>
                                <v-chip variant="tonal" color="primary">{{ selectedRoute.routeType }}</v-chip>
                            </v-card-title>
                            <v-card-text>
                                <div id="detail-map-wrap">
                                    <div id="detail-map"></div>
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
            <div id="chat-container"></div>
        </v-main>
    </v-layout>
</template>

<script setup>
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import 'leaflet/dist/leaflet.css';
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { getRouteById, getSafetyTone } from '../data/routeAnalysis';
import SafePathNavDrawer from '../components/SafePathNavDrawer.vue';
import { mountLangflowChat } from '../utils/langflowChat';

const TILE_URL = process.env.VUE_APP_TILE_URL || 'http://localhost:8081/tile/{z}/{x}/{y}.png';

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const router = useRouter();
const route = useRoute();
const map = ref(null);
const routeOverlay = ref(null);

const selectedRoute = computed(() => getRouteById(route.params.routeId));

const displayJourney = computed(() => {
    const start = String(route.query.start || selectedRoute.value.origin).trim();
    const destination = String(route.query.destination || selectedRoute.value.destination).trim();
    return `${start} to ${destination}`;
});

function scoreBadgeStyle(score) {
    const tone = getSafetyTone(score);

    return {
        color: tone.color,
        backgroundColor: tone.soft
    };
}

function goHome() {
    router.back();
}

function renderRoute(routeData = selectedRoute.value) {
    if (!map.value || !routeData) {
        return;
    }

    const tone = getSafetyTone(routeData.safetyScore);

    if (routeOverlay.value) {
        routeOverlay.value.clearLayers();
    }

    const path = L.polyline(routeData.coordinates, {
        color: tone.color,
        weight: 6,
        opacity: 0.95
    });

    routeOverlay.value.addLayer(path);

    routeOverlay.value.addLayer(
        L.circleMarker(routeData.coordinates[0], {
            radius: 9,
            color: '#FFFFFF',
            weight: 3,
            fillColor: tone.color,
            fillOpacity: 1
        })
    );

    routeOverlay.value.addLayer(
        L.circleMarker(routeData.coordinates[routeData.coordinates.length - 1], {
            radius: 9,
            color: '#FFFFFF',
            weight: 3,
            fillColor: '#0A0A0A',
            fillOpacity: 1
        })
    );

    map.value.fitBounds(path.getBounds().pad(0.22));
}

function initMap() {
    if (map.value) {
        return;
    }

    map.value = L.map('detail-map', {
        zoomControl: false
    }).setView([52.52, 13.405], 12);

    L.control.zoom({ position: 'topright' }).addTo(map.value);

    L.tileLayer(TILE_URL, {
        maxZoom: 18,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map.value);

    routeOverlay.value = L.layerGroup().addTo(map.value);
    renderRoute();
}

function initChat() {
    mountLangflowChat('chat-container');
}

watch(
    () => route.params.routeId,
    () => {
        renderRoute();
    }
);

onMounted(() => {
    initMap();
    initChat();
});

onBeforeUnmount(() => {
    if (map.value) {
        map.value.remove();
        map.value = null;
    }
});
</script>

<style scoped>
.app-shell {
    min-height: 100vh;
}

#detail-map-wrap {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(148, 163, 184, 0.35);
}

#detail-map {
    width: 100%;
    height: 68vh;
    min-height: 420px;
}
</style>