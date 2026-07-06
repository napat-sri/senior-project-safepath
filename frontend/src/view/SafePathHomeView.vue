<template>
    <v-layout class="app-shell">
        <SafePathNavDrawer />

        <v-main>
            <v-container fluid>
                <v-card class="mb-4" rounded="lg">
                    <v-card-text>
                        <v-card-title>Find your safest Berlin route</v-card-title>
                        <v-card-subtitle>
                            Compare route options, validate Berlin-only locations, and inspect detailed route safety
                            before you
                            go.
                        </v-card-subtitle>
                    </v-card-text>
                </v-card>

                <v-row>
                    <v-col cols="12" lg="4">
                        <v-card rounded="lg" elevation="2" class="mb-4">
                            <v-card-title>Route Search</v-card-title>
                            <v-card-subtitle>Search safer paths using live route intelligence.</v-card-subtitle>
                            <v-card-subtitle>Type a district, station, or landmark to see suggestions.</v-card-subtitle>
                            <v-card-text>
                                <v-form @submit.prevent="searchRoute">
                                    <v-text-field v-model="startLocation" label="📍 Start Location"
                                        placeholder="e.g., Alexanderplatz" variant="outlined" density="comfortable"
                                        :error-messages="startError ? [startError] : []" @focus="startFocused = true"
                                        @blur="handleFieldBlur('start')" />

                                    <v-list v-if="startSuggestions.length && startFocused" density="compact"
                                        class="mb-3 suggestion-list">
                                        <v-list-item v-for="suggestion in startSuggestions"
                                            :key="`start-${suggestion.name}`" :title="suggestion.name"
                                            @mousedown.prevent="selectSuggestion('start', suggestion)" />
                                    </v-list>

                                    <v-text-field v-model="destination" label="🚩 Destination"
                                        placeholder="e.g., Brandenburg Gate" variant="outlined" density="comfortable"
                                        :error-messages="destinationError ? [destinationError] : []"
                                        @focus="destinationFocused = true" @blur="handleFieldBlur('destination')" />

                                    <v-list v-if="destinationSuggestions.length && destinationFocused" density="compact"
                                        class="mb-3 suggestion-list">
                                        <v-list-item v-for="suggestion in destinationSuggestions"
                                            :key="`destination-${suggestion.name}`" :title="suggestion.name"
                                            @mousedown.prevent="selectSuggestion('destination', suggestion)" />
                                    </v-list>

                                    <v-alert v-if="searchError" type="error" variant="tonal" density="compact"
                                        class="mb-3">
                                        {{ searchError }}
                                    </v-alert>

                                    <div class="d-flex ga-2">
                                        <v-btn color="primary" type="submit" :loading="searchLoading">Search Safe
                                            Route</v-btn>
                                        <v-btn variant="outlined" @click="searchClear">Clear</v-btn>
                                    </div>
                                </v-form>
                            </v-card-text>
                        </v-card>

                        <v-card v-if="showResults" rounded="lg" elevation="2">
                            <v-card-title class="d-flex justify-space-between align-center">
                                <span>Suggested Routes</span>
                                <v-chip size="small" color="primary" variant="tonal">{{ routes.length }} routes</v-chip>
                            </v-card-title>
                            <v-card-subtitle>Route options appear below your search and can be opened in
                                detail.</v-card-subtitle>
                            <v-card-text>
                                <v-alert v-if="routes.length === 0" type="info" variant="tonal">No routes
                                    found.</v-alert>

                                <v-card v-for="route in routes" :key="route.id" variant="outlined" class="mb-3"
                                    rounded="lg">
                                    <v-card-text>
                                        <div class="d-flex justify-space-between align-start mb-2">
                                            <div>
                                                <p class="text-overline text-medium-emphasis">{{ route.routeType }}</p>
                                                <h4 class="text-h6">{{ route.name }}</h4>
                                            </div>
                                            <v-chip :style="scorePillStyle(route.safetyScore)">{{ route.safetyScore
                                                }}/100</v-chip>
                                        </div>

                                        <div
                                            class="d-flex justify-space-between text-caption text-medium-emphasis mb-2">
                                            <span>Distance {{ route.distance }}</span>
                                            <span>Time {{ route.duration }}</span>
                                        </div>

                                        <v-progress-linear :model-value="route.safetyScore" height="9" rounded
                                            :color="route.accentColor || getSafetyTone(route.safetyScore).color"
                                            class="mb-3" />

                                        <p class="text-body-2 mb-3">{{ route.summary }}</p>

                                        <div class="d-flex justify-space-between align-center">
                                            <v-btn size="small" variant="tonal" color="primary"
                                                @click="openRouteDetails(route.id)">
                                                View Details
                                            </v-btn>
                                        </div>
                                    </v-card-text>
                                </v-card>
                            </v-card-text>
                        </v-card>
                    </v-col>

                    <v-col cols="12" lg="8">
                        <v-card rounded="lg" elevation="2">
                            <v-card-title>Berlin Safety Map</v-card-title>
                            <v-card-text>
                                <div id="map-container">
                                    <div id="home-map"></div>
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
                <div id="chat-container"></div>
            </v-container>
        </v-main>
    </v-layout>
</template>

<script setup>
import L from 'leaflet';
import 'leaflet-control-geocoder';
import 'leaflet-control-geocoder/dist/Control.Geocoder.css';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import 'leaflet/dist/leaflet.css';
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import SafePathNavDrawer from '../components/SafePathNavDrawer.vue';

import {
    getSafetyTone,
    setRouteSuggestions,
    validateBerlinLocation
} from '../data/routeAnalysis';
import { mountLangflowChat } from '../utils/langflowChat';

import { placeService, routeService } from '../services/api';

const TILE_URL = process.env.VUE_APP_TILE_URL || 'http://localhost:8081/tile/{z}/{x}/{y}.png';

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const router = useRouter();
const map = ref(null);
const routeOverlay = ref(null);
const startLocation = ref('');
const destination = ref('');
const startTouched = ref(false);
const destinationTouched = ref(false);
const startFocused = ref(false);
const destinationFocused = ref(false);
const showResults = ref(false);
const searchError = ref('');

const searchLoading = ref(false);
const routes = ref([]);
const selectedRoute = computed(() => (routes.value && routes.value.length > 0 ? routes.value[0] : null));
const hasSearched = ref(false);

const startError = computed(() => {
    if (!hasSearched.value) return '';
    return validateBerlinLocation(startLocation.value);
});

const destinationError = computed(() => {
    if (!hasSearched.value) return '';
    return validateBerlinLocation(destination.value);
});

const suggestionCache = {};

async function fetchSuggestions(query) {
    if (!query || query.trim().length < 3) return [];

    const normalizedQuery = query.trim().toLowerCase();

    if (suggestionCache[normalizedQuery]) {
        return suggestionCache[normalizedQuery];
    }

    try {
        const { data } = await placeService.search(query);
        const results = data.places || [];
        suggestionCache[normalizedQuery] = results;
        return results;
    } catch (error) {
        return [];
    }
}

const startSuggestions = ref([]);
const selectedStartPlace = ref(null);
const skipStartWatch = ref(false);
let startDebounceTimer = null;

watch(startLocation, async (value) => {
    if (skipStartWatch.value) {
        skipStartWatch.value = false;
        return;
    }

    clearTimeout(startDebounceTimer);

    startDebounceTimer = setTimeout(async () => {
        const results = await fetchSuggestions(value);
        startSuggestions.value = results.filter(
            (item) => item.name !== destination.value
        );
    }, 500);
});

const destinationSuggestions = ref([]);
const selectedDestinationPlace = ref(null);
const skipDestinationWatch = ref(false);
let destinationDebounceTimer = null;

watch(destination, async (value) => {
    if (skipDestinationWatch.value) {
        skipDestinationWatch.value = false;
        return;
    }

    clearTimeout(destinationDebounceTimer);

    destinationDebounceTimer = setTimeout(async () => {
        destinationSuggestions.value = (await fetchSuggestions(value)).filter(
            (item) => item.name !== startLocation.value
        );
    }, 500);
});

function selectSuggestion(type, suggestion) {
    if (type === 'start') {
        skipStartWatch.value = true;
        startLocation.value = suggestion.name;
        selectedStartPlace.value = suggestion;
        startSuggestions.value = [];
        startFocused.value = false;
    }
    if (type === 'destination') {
        skipDestinationWatch.value = true;
        destination.value = suggestion.name;
        selectedDestinationPlace.value = suggestion;
        destinationSuggestions.value = [];
        destinationFocused.value = false;
    }
}

function scorePillStyle(score) {
    const tone = getSafetyTone(score);

    return {
        color: tone.color,
        backgroundColor: tone.soft
    };
}

function handleFieldBlur(field) {
    window.setTimeout(() => {
        if (field === 'start') {
            startTouched.value = true;
            startFocused.value = false;
        }

        if (field === 'destination') {
            destinationTouched.value = true;
            destinationFocused.value = false;
        }
    }, 120);
}

async function fetchSafeRoute() {
    searchLoading.value = true;

    try {
        const startCoords = selectedStartPlace.value;
        const destCoords = selectedDestinationPlace.value;

        const payload = {
            start: { lat: startCoords.lat, lng: startCoords.lng },
            destination: { lat: destCoords.lat, lng: destCoords.lng },
            startName: startLocation.value,
            destinationName: destination.value
        };

        const res = await routeService.safe(payload);

        if (res.status !== 200) throw new Error('API error: ' + res.status);

        const data = await res.data;
        routes.value = data.route_suggestions || [];
        searchResult.value = data;
        showResults.value = routes.value.length > 0;
        setRouteSuggestions(routes.value);
        renderRoutePreview();
    } catch (err) {
        searchResult.value = { error: err.message };
    } finally {
        searchLoading.value = false;
    }
}

function renderRoutePreview() {
    if (!map.value || !routes.value.length) return;

    if (routeOverlay.value) {
        routeOverlay.value.clearLayers();
    }

    routes.value.forEach((route, idx) => {
        const tone = getSafetyTone(route.safetyScore);
        const color = route.accentColor || tone.color;

        const path = L.polyline(route.coordinates, {
            color: color,
            weight: 6,
            opacity: 0.7 + (idx === 0 ? 0.2 : 0)
        });
        routeOverlay.value.addLayer(path);

        const startMarker = L.circleMarker(route.coordinates[0], {
            radius: 9,
            color: '#FFFFFF',
            weight: 3,
            fillColor: color,
            fillOpacity: 1
        });
        routeOverlay.value.addLayer(startMarker);

        const endMarker = L.circleMarker(route.coordinates[route.coordinates.length - 1], {
            radius: 9,
            color: '#FFFFFF',
            weight: 3,
            fillColor: '#0A0A0A',
            fillOpacity: 1
        });
        routeOverlay.value.addLayer(endMarker);
    });

    const allCoords = routes.value.flatMap(r => r.coordinates);
    if (allCoords.length) {
        map.value.fitBounds(allCoords, { padding: [40, 40] });
    }
}

function initMap() {
    if (map.value) {
        return;
    }

    map.value = L.map('home-map', {
        zoomControl: false
    }).setView([52.52, 13.405], 12);

    L.control.zoom({ position: 'topright' }).addTo(map.value);

    L.tileLayer(TILE_URL, {
        maxZoom: 18,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map.value);

    L.Control.geocoder({
        defaultMarkGeocode: false,
        placeholder: 'Search Berlin locations'
    }).addTo(map.value);

    routeOverlay.value = L.layerGroup().addTo(map.value);
    renderRoutePreview();
}

function initChat() {
    mountLangflowChat('chat-container');
}

function openRouteDetails(routeId) {
    sessionStorage.setItem('searchState', JSON.stringify({
        startLocation: startLocation.value,
        destination: destination.value,
        routes: routes.value,
        selectedStartPlace: selectedStartPlace.value,
        selectedDestinationPlace: selectedDestinationPlace.value,
        showResults: showResults.value
    }));

    router.push({
        name: 'route-details',
        params: { routeId },
        query: {
            start: selectedStartPlace.value?.name || '',
            destination: selectedDestinationPlace.value?.name || ''
        }
    });
}

function searchRoute() {
    hasSearched.value = true;
    searchError.value = '';
    showResults.value = true;
    fetchSafeRoute();
}

function searchClear() {
    hasSearched.value = false;
    searchError.value = '';
    startLocation.value = '';
    destination.value = '';
    routes.value = [];
    selectedStartPlace.value = null;
    selectedDestinationPlace.value = null;
    routeOverlay.value.clearLayers();
    showResults.value = false;
}

const searchResult = ref(null);

onMounted(() => {
    const saved = sessionStorage.getItem('searchState');
    if (saved) {
        const searchData = JSON.parse(saved);
        startLocation.value = searchData.startLocation;
        destination.value = searchData.destination;
        routes.value = searchData.routes;
        selectedStartPlace.value = searchData.selectedStartPlace;
        selectedDestinationPlace.value = searchData.selectedDestinationPlace;
        showResults.value = searchData.showResults;

        sessionStorage.removeItem('searchState');
    }

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

.suggestion-list {
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    border-radius: 12px;
}

#map-container {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

#home-map {
    width: 100%;
    min-height: 380px;
}

/*
 * The Langflow widget is injected into #chat-container. By default the div is a
 * full-width block at the bottom of <v-main>, so it overlaps the page and blocks
 * clicks. Pin it to a corner and shrink it to the widget's own size.
 * Adjust right/bottom to move the button; raise z-index if it sits under a card.
 */
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