<template>
    <div class="page-shell">
        <aside :class="['sidebar', { collapsed: sidebarCollapsed }]">
            <div class="brand-section">
                <img class="brand-logo" :src="safePathLogo" alt="SafePath Berlin logo" />

                <div class="brand-copy">
                    <h2>SafePath</h2>
                    <span>Berlin</span>
                </div>

                <button class="sidebar-toggle" type="button" @click="toggleSidebar" aria-label="Toggle sidebar">
                    ☰
                </button>
            </div>

            <nav class="nav-menu" aria-label="Primary navigation">
                <button type="button" class="nav-item active" aria-label="Dashboard" @click="$router.push('/')">
                    <span>🗺️</span>
                    Dashboard
                </button>

                <button type="button" class="nav-item" aria-label="Profile" @click="$router.push('/profile')">
                    <span>👤</span>
                    Profile
                </button>

                <button type="button" class="nav-item" aria-label="Report Incident" @click="$router.push('/incident')">
                    <span>⚠️</span>
                    Report Incident
                </button>

                <button type="button" class="nav-item" aria-label="Overview Dashboard"
                    @click="$router.push('/overview')">
                    <span>📊</span>
                    Overview Dashboard
                </button>

                <button type="button" class="nav-item">
                    <span>📋</span>
                    Community Reports
                </button>


            </nav>

            <!-- <div class="premium-card card">
                <p class="premium-label">Premium Safety+</p>
                <h3>Unlock predictive safety alerts</h3>
                <p>
                    Get proactive warnings, route intelligence, and personalized safe route analysis.
                </p>

                <button type="button" class="premium-btn btn btn-ghost">Upgrade</button>
            </div> -->
        </aside>

        <main class="main-content">
            <header class="topbar card">
                <div>
                    <h2>Find your safest Berlin route</h2>
                    <p class="muted">Compare route options, validate Berlin-only locations, and inspect detailed route
                        safety before you go.</p>
                </div>
            </header>

            <section class="content-grid">
                <section class="search-panel card">
                    <div class="panel-header">
                        <h3>Route Search</h3>
                        <span>Search safer paths using live route intelligence.</span>
                    </div>

                    <form class="search-form" @submit.prevent="searchRoute" novalidate>
                        <label for="start-location">Start Location *</label>

                        <div class="input-wrap" :class="{ invalid: startError }">
                            <span>📍</span>
                            <input id="start-location" v-model="startLocation" class="search-input" type="text"
                                placeholder="e.g., Alexanderplatz" autocomplete="off" @focus="startFocused = true"
                                @blur="handleFieldBlur('start')" />
                        </div>

                        <ul v-if="startSuggestions.length && startFocused" class="suggestion-list card">
                            <li v-for="suggestion in startSuggestions" :key="`start-${suggestion.name}`">
                                <button type="button" @mousedown.prevent="selectSuggestion('start', suggestion)">
                                    {{ suggestion.name }}
                                </button>
                            </li>
                        </ul>

                        <p v-if="startError" class="field-error">{{ startError }}</p>

                        <label for="destination-location">Destination *</label>

                        <div class="input-wrap" :class="{ invalid: destinationError }">
                            <span>🚩</span>
                            <input id="destination-location" v-model="destination" class="search-input" type="text"
                                placeholder="e.g., Brandenburg Gate" autocomplete="off"
                                @focus="destinationFocused = true" @blur="handleFieldBlur('destination')" />
                        </div>

                        <ul v-if="destinationSuggestions.length && destinationFocused" class="suggestion-list card">
                            <li v-for="suggestion in destinationSuggestions" :key="`destination-${suggestion.name}`">
                                <button type="button" @mousedown.prevent="selectSuggestion('destination', suggestion)">
                                    {{ suggestion.name }}
                                </button>
                            </li>
                        </ul>

                        <p v-if="destinationError" class="field-error">{{ destinationError }}</p>

                        <p class="helper-copy">
                            Type a Berlin district, station, or landmark to see geocoding suggestions.
                        </p>

                        <p v-if="searchError" class="global-error">{{ searchError }}</p>

                        <button type="submit" class="search-btn btn btn-primary" :disabled="searchLoading">
                            <span v-if="searchLoading" class="spinner"></span>
                            {{ searchLoading ? 'Analyzing...' : 'Search Safe Route' }}
                        </button>
                        <button type="button" @click="searchClear()" class="search-btn btn">
                            Clear
                        </button>
                    </form>

                    <section class="results-block">
                        <div v-if="showResults" class="route-card-list">
                            <div class="results-header">
                                <div>
                                    <h3>Suggested Routes</h3>
                                    <p class="muted">Route options appear below your search and can be opened in detail.
                                    </p>
                                </div>
                                <span v-if="showResults" class="results-count">{{ routes.length }} routes</span>
                            </div>

                            <article v-for="route in routes" :key="route.id" class="route-card card">
                                <div class="route-card-top">
                                    <div>
                                        <p class="route-type">{{ route.routeType }}</p>
                                        <h4>{{ route.name }}</h4>
                                    </div>

                                    <div class="score-pill" :style="scorePillStyle(route.safetyScore)">
                                        {{ route.safetyScore }}/100
                                    </div>
                                </div>

                                <div class="route-meta">
                                    <span>Distance {{ route.distance }}</span>
                                    <span>Time {{ route.duration }}</span>
                                </div>

                                <div class="score-track" :aria-label="`Safety score ${route.safetyScore} out of 100`">
                                    <span :style="scoreTrackStyle(route.safetyScore, route.accentColor)"></span>
                                </div>

                                <p class="route-summary">{{ route.summary }}</p>

                                <div class="route-footer">
                                    <span class="route-pair">{{ route.origin }} to {{ route.destination }}</span>
                                    <button type="button" class="view-details-btn btn btn-ghost"
                                        @click="openRouteDetails(route.id)">
                                        View Details
                                    </button>
                                </div>
                            </article>
                        </div>
                        <div v-if="showResults && routes.length === 0" class="empty-results">
                            No routes found.
                        </div>
                    </section>
                </section>

                <section class="map-panel card">
                    <div class="panel-header map-header">
                        <h3>Berlin Safety Map</h3>
                    </div>

                    <div id="map-container">
                        <div id="home-map"></div>
                    </div>
                </section>
            </section>
        </main>
        <div id="chat-container"></div>
    </div>
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
import safePathLogo from '../assets/Berlin.png';

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
const sidebarCollapsed = ref(true);
const startLocation = ref('');
const destination = ref('');
const startTouched = ref(false);
const destinationTouched = ref(false);
const startFocused = ref(false);
const destinationFocused = ref(false);
const showResults = ref(false);
const searchError = ref('');

const searchLoading = ref(false);

const routes = ref([]); // Replace the computed with a ref
const selectedRoute = computed(() => (routes.value && routes.value.length > 0 ? routes.value[0] : null));
// console.log('Selected route:', selectedRoute.value, routes.value);

const hasSearched = ref(false);

const startError = computed(() => {
    if (!hasSearched.value) return '';
    return validateBerlinLocation(startLocation.value);
});

const destinationError = computed(() => {
    if (!hasSearched.value) return '';
    return validateBerlinLocation(destination.value);
});

// Fetch geocoding suggestions from API

// Add a simple cache object outside the function
const suggestionCache = {};

async function fetchSuggestions(query) {
    if (!query || query.trim().length < 3) return [];

    const normalizedQuery = query.trim().toLowerCase();

    // 1. Check if we already fetched this exact query
    if (suggestionCache[normalizedQuery]) {
        return suggestionCache[normalizedQuery];
    }

    try {
        // 2. If not in cache, fetch from API
        const { data } = await placeService.search(query);
        // console.log("query: ", query)
        // console.log("data: ", data)
        const results = data.places || [];

        // 3. Save to cache for future use
        suggestionCache[normalizedQuery] = results;
        return results;
    } catch (error) {
        // console.error("Error fetching places:", error);
        return [];
    }
    // const { data } = await placeService.search(query);
    // return data.places || [];
}

// Start Location
const startSuggestions = ref([]);
const selectedStartPlace = ref(null);
const skipStartWatch = ref(false);
let startDebounceTimer = null; // Add timer variable

watch(startLocation, async (value) => {
    if (skipStartWatch.value) {
        skipStartWatch.value = false;
        return;
    }

    // Clear the existing timer on every keystroke
    clearTimeout(startDebounceTimer);

    // Set a new timer
    startDebounceTimer = setTimeout(async () => {
        const results = await fetchSuggestions(value);
        startSuggestions.value = results.filter(
            (item) => item.name !== destination.value
        );
    }, 500);

    // startSuggestions.value = (await fetchSuggestions(value)).filter(
    //     (item) => item.name !== destination.value
    // );
});

// Destination
const destinationSuggestions = ref([]);
const selectedDestinationPlace = ref(null);
const skipDestinationWatch = ref(false);
let destinationDebounceTimer = null; // Add timer variable

watch(destination, async (value) => {
    if (skipDestinationWatch.value) {
        skipDestinationWatch.value = false;
        return;
    }

    // Clear the existing timer on every keystroke
    clearTimeout(destinationDebounceTimer);

    // Set a new timer
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
        // console.log('Selected destination:', suggestion);
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

function scoreTrackStyle(score, accentColor) {
    return {
        width: `${score}%`,
        backgroundColor: accentColor
    };
}

function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value;
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
//----- Get Safe Route Logic -----
async function fetchSafeRoute() {

    searchLoading.value = true;

    try {
        // --- Call backend with hardcoded coordinates ---
        const startCoords = selectedStartPlace.value
        const destCoords = selectedDestinationPlace.value

        const payload = {
            start: { lat: startCoords.lat, lng: startCoords.lng },
            destination: { lat: destCoords.lat, lng: destCoords.lng },
            startName: startLocation.value,
            destinationName: destination.value
        };
        // console.log("Requesting safe routes with payload:", payload);
        const res = await routeService.safe(payload);
        // console.log("API response for safe route:", res);

        if (res.status !== 200) throw new Error("API error: " + res.status);

        const data = await res.data;
        routes.value = data.route_suggestions || [];
        searchResult.value = data;
        showResults.value = routes.value.length > 0;
        setRouteSuggestions(routes.value); // Update the route suggestions in the data module
        // console.log("/api/routes/safe search result:", data);
        // console.log("Extracted saferoutes:", routes.value);
        renderRoutePreview();
    } catch (err) {
        searchResult.value = { error: err.message };
        // console.error("/api/routes/safe search error:", err);
    } finally {
        searchLoading.value = false;
    }

}


function renderRoutePreview() {
    if (!map.value || !routes.value.length) return;

    // Clear previous overlays
    if (routeOverlay.value) {
        routeOverlay.value.clearLayers();
    }

    routes.value.forEach((route, idx) => {
        const tone = getSafetyTone(route.safetyScore);
        const color = route.accentColor || tone.color;

        // Draw route polyline
        const path = L.polyline(route.coordinates, {
            color: color,
            weight: 6,
            opacity: 0.7 + (idx === 0 ? 0.2 : 0), // Highlight first route a bit more
        });
        routeOverlay.value.addLayer(path);

        // Start marker
        const startMarker = L.circleMarker(route.coordinates[0], {
            radius: 9,
            color: '#FFFFFF',
            weight: 3,
            fillColor: color,
            fillOpacity: 1
        });
        routeOverlay.value.addLayer(startMarker);

        // End marker
        const endMarker = L.circleMarker(route.coordinates[route.coordinates.length - 1], {
            radius: 9,
            color: '#FFFFFF',
            weight: 3,
            fillColor: '#0A0A0A',
            fillOpacity: 1
        });
        routeOverlay.value.addLayer(endMarker);
    });

    // Fit map to all routes
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
    // Save search state to sessionStorage before navigating
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
    showResults.value = false;
}

// --- Safe Route Search Result State ---
const searchResult = ref(null);

onMounted(() => {
    // Restore search data from sessionStorage if available
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
/* =========================
   Global Page Setup
========================= */

:global(body) {
    margin: 0;
    background: var(--color-bg);
}

.page-shell {
    min-height: 100vh;
    display: flex;
    color: var(--color-text);
}


/* =========================
   Sidebar Container
========================= */

.sidebar {
    width: 248px;
    flex-shrink: 0;
    padding: 24px 18px;
    border-right: 1px solid var(--color-border);
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(14px);
    transition: width 200ms ease, padding 200ms ease;
}

.sidebar.collapsed {
    width: auto;
    padding: 16px;
}


/* =========================
   Sidebar Brand / Logo Area
========================= */

.brand-section {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
}

.brand-logo {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
    border-radius: 14px;
    object-fit: cover;
    border: 1px solid var(--color-border);
    background: var(--color-surface);
}

.brand-copy {
    flex: 1;
    min-width: 0;
}

.brand-copy span {
    display: block;
    margin-top: 2px;
    color: var(--color-primary);
    font-weight: 700;
}

.brand-copy p,
.panel-header p,
.topbar p,
.route-summary,
.route-pair,
.muted,
.helper-copy


/* =========================
   Sidebar Collapsed State
========================= */

.sidebar.collapsed .brand-logo,
.sidebar.collapsed .brand-copy {
    display: block;
}
.sidebar.collapsed .nav-menu {
    display: grid;
}


/* =========================
   Sidebar Toggle Button
========================= */

.sidebar-toggle {
    margin-left: auto;
    border: 0;
    background: transparent;
    color: var(--color-text-secondary);
    font-size: 20px;
    cursor: pointer;
}


/* =========================
   Sidebar Navigation Menu
========================= */


.nav-menu {
    display: grid;
    gap: 10px;
    margin-top: 32px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 16px;
    border-radius: var(--radius-md);
    border: 1px solid transparent;
    background: #f8fafc;
    color: var(--color-text);
    text-decoration: none;
    cursor: pointer;
}

.nav-item.active {
    border-color: rgba(99, 102, 241, 0.22);
    background: rgba(99, 102, 241, 0.08);
    color: var(--color-primary);
}
.side-note {
    margin-top: 28px;
    padding: 18px;
}

.side-note h3 {
    margin: 0 0 8px;
}

.side-note p,
.brand-copy p,
.panel-header p,
.topbar p,
.muted {
    color: var(--color-text-secondary);
}

.side-label,
.eyebrow {
    margin: 0 0 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 11px;
    color: var(--color-neutral);
}


/* =========================
   Sidebar Premium Card
========================= */
.eyebrow {
    margin: 0 0 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 11px;
    color: var(--color-neutral);
}

.route-type {
    margin: 0 0 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 11px;
    color: var(--color-neutral);
}


/* =========================
   Old Logo Box - Currently Disabled
========================= */

/* .logo-box {
    width: 48px;
    height: 56px;
    display: grid;
    place-items: center;
    border: 2px solid var(--color-success);
    border-radius: 16px;
    color: var(--color-success);
    font-weight: 700;
    background: rgba(16, 185, 129, 0.08);
} */


/* =========================
   Main Content Layout
========================= */

.main-content {
    flex: 1;
    padding: 28px;
}

.topbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 10px;
    padding: 12px;
    margin-bottom: 12px;
}

.content-grid {
    display: grid;
    grid-template-columns: minmax(340px, 420px) minmax(0, 1fr);
    gap: 24px;
    align-items: start;
}


/* =========================
   Shared Badges / Tags
========================= */

.status-badge,
.results-count,
.map-route-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: var(--radius-pill);
    border: 1px solid var(--color-border);
    background: rgba(255, 255, 255, 0.9);
    color: var(--color-text-secondary);
    white-space: nowrap;
}


/* =========================
   Panels / Cards
========================= */

.search-panel,
.map-panel,
.premium-card,
.empty-results,
.route-card,
.suggestion-list {
    background: var(--color-surface);
}

.search-panel,
.map-panel {
    padding: 12px;
}

.panel-header {
    margin-bottom: 18px;
}


/* =========================
   Search Form
========================= */

.search-form {
    display: grid;
    gap: 10px;
}

label {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text);
}

.input-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 14px;
    min-height: 56px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: #fff;
}

.input-wrap.invalid {
    border-color: rgba(239, 68, 68, 0.6);
}

.search-input {
    width: 100%;
    border: 0;
    outline: 0;
    font: inherit;
    color: var(--color-text);
    background: transparent;
}

.search-input::placeholder {
    color: var(--color-neutral);
}

.field-error,
.global-error,
.helper-copy {
    margin: 0;
    font-size: 13px;
    line-height: 1.5;
}

.field-error,
.global-error {
    color: var(--color-error);
}

.search-btn {
    margin-top: 6px;
}


/* =========================
   Suggestions Dropdown
========================= */

.suggestion-list {
    list-style: none;
    margin: -4px 0 4px;
    padding: 6px;
    border-radius: 10px;
    border: 1px solid var(--color-border);
}

.suggestion-list li+li {
    margin-top: 4px;
}

.suggestion-list button {
    width: 100%;
    border: 0;
    background: transparent;
    padding: 10px 12px;
    text-align: left;
    border-radius: 8px;
    cursor: pointer;
    color: var(--color-text);
}

.suggestion-list button:hover {
    background: rgba(99, 102, 241, 0.08);
    color: var(--color-primary);
}


/* =========================
   Search Results
========================= */

.results-block {
    margin-top: 7px;
}

.results-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
}

.route-card-list {
    display: grid;
    gap: 14px;
}

.route-card {
    padding: 18px;
    transition: transform 180ms ease, box-shadow 180ms ease;
}

.route-card:hover {
    box-shadow: var(--shadow-hover-card);
    transform: translateY(-2px);
}

.route-card-top,
.route-meta,
.route-footer {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
}

.route-card h4,
.map-header h3 {
    margin: 0;
}

.route-meta {
    margin: 14px 0 10px;
    color: var(--color-text-secondary);
    font-size: 13px;
}

.route-summary {
    margin: 12px 0 16px;
}

.route-footer {
    align-items: center;
}

.view-details-btn {
    padding-left: 0;
    padding-right: 0;
}

.empty-results {
    padding: 18px;
    border: 1px dashed var(--color-border);
}


/* =========================
   Safety Score UI
========================= */

.score-pill {
    min-width: 76px;
    padding: 8px 10px;
    border-radius: var(--radius-pill);
    text-align: center;
    font-size: 13px;
    font-weight: 700;
}

.score-track {
    height: 8px;
    border-radius: var(--radius-pill);
    background: #eef2f7;
    overflow: hidden;
}

.score-track span {
    display: block;
    height: 100%;
    border-radius: inherit;
}


/* =========================
   Map Section
========================= */

.map-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
}

#map-container {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid var(--color-border);
    height: 400px;
}

#home-map {
    width: 100%;
    height: 100%;
}


/* =========================
    Loading Spinner
========================= */

.spinner {
    display: inline-block;
    width: 18px;
    height: 18px;
    border: 3px solid #fff;
    border-radius: 50%;
    border-top-color: #6366f1;
    animation: spin 0.7s linear infinite;
    margin-right: 8px;
    vertical-align: middle;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}


/* =========================
    Responsive - Large Screens
========================= */

@media (min-width: 1440px) {
    .content-grid {
        grid-template-columns: 1fr 3fr;
    }

    #home-map,
    #map-container {
        height: 850px;
    }
}


/* =========================
    Responsive - Medium Screens
========================= */

@media (max-width: 1200px) {
    /* .page-shell {
        flex-direction: column;
    } */

    .content-grid {
        grid-template-columns: 2fr;
    }

    #home-map,
    #map-container {
        height: 400px;
    }

    .brand-section {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    }

    .sidebar-toggle {
        margin-left: auto;
        border: 0;
        background: transparent;
        color: var(--color-text-secondary);
        font-size: 20px;
        cursor: pointer;
    }

    .main-content {
        padding: 18px;
        padding-bottom: 110px;
    }

    .topbar,
    .results-header,
    .route-card-top,
    .route-footer,
    .map-header {
        flex-direction: column;
        align-items: flex-start;
    }
}


/* =========================
    Responsive - Below 1440px
========================= */

@media (max-width: 1440px) {

    #home-map,
    #map-container {
        height: 450px;
    }
}
</style>