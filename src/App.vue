<template>
  <div id="app">
    <h1>Welcome to SafePath</h1>
    <p>Your trusted companion for navigating safe routes.</p>
    <div id="chat-container"></div>
    <div id="map-container">
      <div id="map"></div>
    </div>
  </div>
</template>

<script>
// 1. Import Leaflet and its CSS
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// 2. Import Geocoder (optional, if you want the search bar)
import 'leaflet-control-geocoder/dist/Control.Geocoder.css';
import 'leaflet-control-geocoder';

// 3. Fix for missing Marker Icons (Common Leaflet bug in Vue/Webpack)
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// 4. Resolve environment-driven configuration with sensible fallbacks so the
//    app still boots if a teammate forgot to copy .env.example to .env.
const TILE_URL =
  process.env.VUE_APP_TILE_URL || 'http://localhost:8081/tile/{z}/{x}/{y}.png';
const LANGFLOW_HOST =
  process.env.VUE_APP_LANGFLOW_HOST || 'http://localhost:7860';
const LANGFLOW_FLOW_ID = process.env.VUE_APP_LANGFLOW_FLOW_ID || '';
const LANGFLOW_API_KEY = process.env.VUE_APP_LANGFLOW_API_KEY || '';

export default {
  name: 'App',
  data() {
    return {
      map: null
    };
  },
  mounted() {
    this.initMap();
    this.initChat();
  },
  methods: {
    initMap() {
      // Initialize the map (zoom control moved to top-right)
      this.map = L.map('map', {
        zoomControl: false
      }).setView([52.5200, 13.4050], 12);

      L.control.zoom({ position: 'topright' }).addTo(this.map);

      // Tile server URL is driven by VUE_APP_TILE_URL so the same code works
      // against the local Docker tile server, the public OSM tile server, or
      // a hosted environment without modification.
      L.tileLayer(TILE_URL, {
        maxZoom: 18,
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(this.map);

      // Add the Search Bar
      L.Control.geocoder().addTo(this.map);

      // Add the Test Marker
      const testLat = 52.53966;
      const testLng = 13.39465;
      const marker = L.marker([testLat, testLng]).addTo(this.map);
      marker.bindPopup("<b>Berlin Center</b><br>SafePath is active.").openPopup();

      this.map.flyTo([testLat, testLng], 15);
    },
    initChat() {
      // Skip the chat widget entirely if Langflow config is missing — better
      // than rendering a broken widget with no flow_id / api_key.
      if (!LANGFLOW_FLOW_ID || !LANGFLOW_API_KEY) {
        console.warn(
          '[SafePath] Langflow chat disabled: VUE_APP_LANGFLOW_FLOW_ID or ' +
          'VUE_APP_LANGFLOW_API_KEY is not set. Copy .env.example to .env ' +
          'and fill in the values to enable the chat assistant.'
        );
        return;
      }

      const script = document.createElement('script');
      script.src = "https://cdn.jsdelivr.net/gh/logspace-ai/langflow-embedded-chat@v1.0.7/dist/build/static/js/bundle.min.js";

      script.onload = () => {
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
          // Build the custom element programmatically to avoid HTML-escaping
          // surprises with values that come from environment variables.
          const chat = document.createElement('langflow-chat');
          chat.setAttribute('window_title', 'SafePath Assistant');
          chat.setAttribute('flow_id', LANGFLOW_FLOW_ID);
          chat.setAttribute('host_url', LANGFLOW_HOST);
          chat.setAttribute('api_key', LANGFLOW_API_KEY);
          chatContainer.innerHTML = '';
          chatContainer.appendChild(chat);
        }
      };

      document.body.appendChild(script);
    }
  }
};
</script>

<style>
/* Essential: Map must have a height to be visible */
#map {
  height: 500px;
  width: 90%;
  max-width: 1000px;
  margin: 20px auto;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  border: 2px solid #eee;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  padding-top: 40px;
}
</style>
