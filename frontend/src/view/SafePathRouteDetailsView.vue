<template>
    <SafePathNavDrawer />

    <v-main>
        <v-container fluid class="pa-4 pa-md-6">
            <v-card class="mb-5" rounded="lg" elevation="2">
                <v-card-text class="d-flex flex-wrap ga-4 justify-space-between align-center">
                    <div>
                        <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                            Route Detailed Analysis
                        </v-card-title>
                        <v-card-subtitle class="text-medium-emphasis">
                            Inspect overall score, safety breakdown, and selected route map.
                        </v-card-subtitle>
                    </div>
                    <v-btn variant="tonal" color="primary" @click="goHome">Back to Search</v-btn>
                </v-card-text>
            </v-card>
            <v-row>
                <v-col cols="12" md="8">
                    <v-card rounded="lg" elevation="2" height="100%">
                        <v-card-text>
                            <div class="d-flex justify-space-between align-center flex-wrap ga-3 mb-1">
                                <v-chip size="x-large" label class="text-medium-emphasis">
                                    {{ selectedRoute.name }}
                                </v-chip>
                            </div>
                            <v-card-text class="text-body-large text-medium-emphasis mb-2">
                                {{ selectedRoute.summary}}
                            </v-card-text>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="12" md="4">
                    <v-card rounded="lg" elevation="2">
                        <v-card-text>
                            <div class="d-flex justify-space-between align-center flex-wrap ga-3 mb-2">
                                <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                                    Overall Safety
                                </v-card-title>
                                <v-progress-circular :model-value="selectedRoute.safetyScore" :size="175" :width="20"
                                    bg-color="surface-light" :style="scoreBadgeStyle(selectedRoute.safetyScore)" reveal
                                    rounded>
                                    <v-avatar color="surface-light" size="115"><span class="text-headline-small">{{
                                        selectedRoute.safetyScore }}/100</span></v-avatar></v-progress-circular>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="12" md="7">
                    <v-card rounded="lg" elevation="2" height="100%">
                        <v-card-title>Route Information</v-card-title>
                        <v-card-text>
                            <v-list lines="two">
                                <v-row>
                                    <v-col cols="12" md="5">
                                        <v-list-item title="Distance covered" :subtitle="selectedRoute.distance">
                                            <template v-slot:prepend>
                                                <v-avatar color="grey-lighten-1">
                                                    <v-icon color="white">mdi-road-variant</v-icon>
                                                </v-avatar>
                                            </template>
                                        </v-list-item>
                                    </v-col>
                                    <v-col cols="12" md="7">
                                        <v-list-item title="Estimated duration" :subtitle="selectedRoute.duration">
                                            <template v-slot:prepend>
                                                <v-avatar color="grey-lighten-1">
                                                    <v-icon color="white">mdi-clock-outline</v-icon>
                                                </v-avatar>
                                            </template>
                                        </v-list-item>
                                    </v-col>
                                    <v-col cols="12" md="5">
                                        <v-list-item title="Route type" :subtitle="selectedRoute.routeType">
                                            <template v-slot:prepend>
                                                <v-avatar color="grey-lighten-1">
                                                    <v-icon color="white">mdi-train-car</v-icon>
                                                </v-avatar>
                                            </template>
                                        </v-list-item>
                                    </v-col>
                                    <v-col cols="12" md="7">
                                        <v-list-item title="Journey" :subtitle="displayJourney">
                                            <template v-slot:prepend>
                                                <v-avatar color="grey-lighten-1">
                                                    <v-icon color="white">mdi-map-marker-distance</v-icon>
                                                </v-avatar>
                                            </template>
                                        </v-list-item>
                                    </v-col>
                                </v-row>
                            </v-list>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="12" md="5">
                    <v-card rounded="lg" elevation="2" height="100%">
                        <v-card-title>Safety Score Breakdown</v-card-title>
                        <v-card-text>
                            <div v-for="item in selectedRoute.breakdown" :key="item.label" class="mb-3">
                                <div class="d-flex justify-space-between mb-2">
                                    <span class="font-weight-medium">{{ item.label }}</span>
                                    <span>{{ item.score }}/100</span>
                                </div>
                                <v-progress-linear :model-value="item.score" :color="getSafetyTone(item.score).color"
                                    height="8" rounded />
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="12">
                    <v-card rounded="lg" elevation="2">
                        <v-card-title class="d-flex justify-space-between align-center">
                            <div>
                                <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                                    Navigation Map
                                </v-card-title>
                                <v-card-subtitle class="text-medium-emphasis mb-2">
                                    The selected route is highlighted with the analysis safety color.
                                </v-card-subtitle>
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
const TILE_URL = process.env.VUE_APP_TILE_URL
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
    };
}
function goHome() {
    router.back(); // Browser history will restore the page naturally
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
#detail-map-wrap {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

#detail-map {
    width: 100%;
    height: 68vh;
    min-height: 420px;
}

#chat-container {
    position: fixed;
    right: 24px;
    bottom: 24px;
    width: -webkit-fit-content;
    width: fit-content;
    height: -webkit-fit-content;
    height: fit-content;
    z-index: 2000;
}
</style>