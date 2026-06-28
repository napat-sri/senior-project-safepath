<template>
    <div class="page-shell">
        <aside :class="['sidebar', { collapsed: sidebarCollapsed }]">
            <div class="brand-section">
                <img class="brand-logo" :src="safePathLogo" alt="SafePath Berlin logo" />

                <div class="brand-copy">
                    <h2>SafePath</h2>
                    <span>Berlin</span>
                </div>

                <button 
                    class="sidebar-toggle" 
                    type="button" 
                    @click="toggleSidebar"
                    aria-label="Toggle sidebar"
                >
                    ☰
                </button>
            </div>

            <nav class="nav-menu" aria-label="Primary navigation">
                <button type="button" class="nav-item active" aria-current="page">
                    <span>🗺️</span>
                    Dashboard
                </button>

                <button type="button" class="nav-item" aria-label="Profile" @click="$router.push('/profile')">
                    <span>👤</span>
                    Profile
                </button>

                <button type="button" class="nav-item" aria-label="Report an incident" @click="goToIncidentReport">
                    <span>⚠️</span>
                    Report Incident
                </button>

                <button type="button" class="nav-item" aria-label="Overview Dashboard" @click="$router.push('/overview')">
                    <span>📊</span>
                    Overview Dashboard
                </button>

                <button type="button" class="nav-item">
                    <span>📋</span>
                    Community Reports
                </button>
            </nav>

            <div class="premium-card card">
                <p class="premium-label">Premium Safety+</p>
                <h3>Unlock predictive safety alerts</h3>
                <p>
                    Get proactive warnings, route intelligence, and personalized safe route analysis.
                </p>

                <button type="button" class="premium-btn btn btn-ghost">Upgrade</button>
            </div>
        </aside>

        <main class="main-content">
            <header class="topbar card">
                <div>
                    <h2>Route Detailed Analysis</h2>
                    <p class="muted">Inspect the overall score, the breakdown, and the selected route on the map.</p>
                </div>

                <button type="button" class="back-btn btn btn-ghost" @click="goHome">
                    Back to Search
                </button>
            </header>

            <section class="detail-grid">
                <article class="summary-card card">
                    <div class="summary-header">
                        <div>
                            <p class="eyebrow">Overall safety</p>
                            <h3>{{ selectedRoute.name }}</h3>
                        </div>

                        <div class="score-badge" :style="scoreBadgeStyle(selectedRoute.safetyScore)">
                            {{ selectedRoute.safetyScore }}/100
                        </div>
                    </div>

                    <p class="route-summary">{{ selectedRoute.summary }}</p>

                    <div class="score-track">
                        <span :style="scoreTrackStyle(selectedRoute.safetyScore, selectedRoute.accentColor)"></span>
                    </div>
                </article>

                <article class="info-card card">
                    <p class="eyebrow">Route information</p>
                    <div class="info-grid">
                        <div>
                            <span class="info-label">Distance covered</span>
                            <strong>{{ selectedRoute.distance }}</strong>
                        </div>

                        <div>
                            <span class="info-label">Estimated duration</span>
                            <strong>{{ selectedRoute.duration }}</strong>
                        </div>

                        <div>
                            <span class="info-label">Route type</span>
                            <strong>{{ selectedRoute.routeType }}</strong>
                        </div>

                        <div>
                            <span class="info-label">Journey</span>
                            <strong>{{ displayJourney }}</strong>
                        </div>
                    </div>
                </article>

                <article class="breakdown-card card">
                    <p class="eyebrow">Safety score breakdown</p>

                    <div class="breakdown-list">
                        <div v-for="item in selectedRoute.breakdown" :key="item.label" class="breakdown-row">
                            <div class="breakdown-label-row">
                                <span>{{ item.label }}</span>
                                <strong>{{ item.score }}/100</strong>
                            </div>

                            <div class="score-track">
                                <span :style="scoreTrackStyle(item.score, selectedRoute.accentColor)"></span>
                            </div>
                        </div>
                    </div>
                </article>

                <article class="map-card card">
                    <p class="eyebrow">Map view</p>
                    <div class="map-header">
                        <div>
                            <h3>Navigation Map</h3>
                            <p class="muted">The selected route is highlighted with the safety color from the analysis.
                            </p>
                        </div>

                        <span class="map-route-tag">{{ selectedRoute.routeType }}</span>
                    </div>

                    <div id="detail-map-wrap">
                        <div id="detail-map"></div>
                    </div>
                </article>
            </section>
        </main>
        <div id="chat-container"></div>
    </div>
</template>

<script setup>
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import 'leaflet/dist/leaflet.css';
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { getRouteById, getRouteSuggestions, getSafetyTone } from '../data/routeAnalysis';
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
const sidebarCollapsed = ref(true);

const selectedRoute = computed(() => getRouteById(route.params.routeId));
// const selectedRoute = route.params.routeId;
console.log(route.value);

const displayJourney = computed(() => {
    console.log(getRouteSuggestions());
    const start = String(route.query.start || selectedRoute.value.origin).trim();
    const destination = String(route.query.destination || selectedRoute.value.destination).trim();
    console.log(selectedRoute.value, route.query);
    return `${start} to ${destination}`;
});

function scoreBadgeStyle(score) {
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

function goHome() {
    router.push({ name: 'home' });
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
    console.log(route.value);
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
:global(body) {
    margin: 0;
    background: var(--color-bg);
}

.page-shell {
    min-height: 100vh;
    display: flex;
    color: var(--color-text);
}

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
    width: 36px;
    padding: 16px;
}

.brand-section {
    display: flex;
    align-items: center;
    gap: 14px;
}

.brand-copy {
    min-width: 0;
}

.sidebar.collapsed .brand-copy,
.sidebar.collapsed .nav-menu,
.sidebar.collapsed .premium-card {
    display: none;
}

.logo-box {
    width: 48px;
    height: 56px;
    display: grid;
    place-items: center;
    border: 2px solid var(--color-success);
    border-radius: 16px;
    color: var(--color-success);
    font-weight: 700;
    background: rgba(16, 185, 129, 0.08);
}

.sidebar-toggle {
    margin-left: auto;
    border: 0;
    background: transparent;
    color: var(--color-text-secondary);
    font-size: 20px;
    cursor: pointer;
}

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

.premium-card {
    margin-top: 28px;
    padding: 18px;
}

.premium-label,
.eyebrow {
    margin: 0 0 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 11px;
    color: var(--color-neutral);
}

.premium-btn {
    margin-top: 12px;
}

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

.detail-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 24px;
}

.summary-card,
.info-card,
.breakdown-card,
.map-card {
    padding: 24px;
}

.summary-card,
.map-card {
    grid-column: span 2;
}

.summary-header,
.map-header,
.breakdown-label-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
}

.score-badge {
    min-width: 88px;
    padding: 12px 14px;
    border-radius: var(--radius-pill);
    text-align: center;
    font-size: 16px;
    font-weight: 700;
}

.route-summary,
.muted,
.info-label {
    color: var(--color-text-secondary);
}

.route-summary {
    margin: 14px 0 18px;
}

.score-track {
    height: 10px;
    border-radius: var(--radius-pill);
    background: #eef2f7;
    overflow: hidden;
}

.score-track span {
    display: block;
    height: 100%;
    border-radius: inherit;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    margin-top: 16px;
}

.info-grid strong {
    display: block;
    margin-top: 6px;
    font-size: 18px;
}

.breakdown-list {
    display: grid;
    gap: 16px;
    margin-top: 16px;
}

.breakdown-row {
    display: grid;
    gap: 8px;
}

#detail-map-wrap {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid var(--color-border);
    margin-top: 18px;
}

#detail-map {
    width: 100%;
    height: 540px;
}

@media (max-width: 1180px) {
    .detail-grid {
        grid-template-columns: 1fr;
    }

    .summary-card,
    .map-card {
        grid-column: auto;
    }
}

@media (max-width: 860px) {
    .page-shell {
        flex-direction: column;
    }

    .sidebar {
        width: auto;
        border-right: 0;
        border-bottom: 1px solid var(--color-border);
    }

    .sidebar.collapsed {
        width: auto;
    }

    .sidebar.collapsed .brand-copy,
    .sidebar.collapsed .nav-menu,
    .sidebar.collapsed .premium-card {
        display: block;
    }

    .main-content {
        padding: 18px;
    }

    .topbar,
    .summary-header,
    .map-header,
    .breakdown-label-row {
        flex-direction: column;
    }

    #detail-map {
        height: 420px;
    }
}
</style>