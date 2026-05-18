<template>
  <div class="home-layout">

    <aside :class="['sidebar', { collapsed: sidebarCollapsed }]">
      <div class="brand-section">
        <div class="logo-box">✓</div>

        <div>
          <h1>SafePath</h1>
          <p>Berlin</p>
        </div>

        <button class="sidebar-toggle" type="button" @click="toggleSidebar" aria-label="Toggle sidebar">☰</button>
      </div>

      <nav class="nav-menu">
        <a class="nav-item active">
          <span>⌂</span>
          Dashboard
        </a>

        <a class="nav-item">
          <span>👤</span>
          Profile
        </a>

        <a class="nav-item">
          <span>⚠️</span>
          Report Incident
        </a>

        <a class="nav-item">
          <span>🗺️</span>
          Community Reports
        </a>
      </nav>

      <div class="premium-card">
        <h3>Premium Safety+</h3>
        <p>
          Unlock predictive safety alerts and personalized safe route analysis.
        </p>

        <button>Upgrade</button>
      </div>
    </aside>

    <main class="main-content">

      <div class="topbar">
        <div>
          <h2>Find Your Safe Route</h2>
          <p>Navigate Berlin with confidence and smarter safety insights.</p>
        </div>

        <div class="status-badge">
          <span class="status-dot"></span>
          SafePath Active
        </div>
      </div>

      <section class="content-grid">

        <div class="search-panel">

          <div class="panel-header">
            <h3>Route Search</h3>
            <p>Search safer paths using live route intelligence.</p>
          </div>

          <form @submit.prevent="searchRoute">

            <label>Start Location</label>

            <div class="input-box">
              <span>📍</span>

              <input
                v-model="startLocation"
                type="text"
                placeholder="e.g., Alexanderplatz"
              />
            </div>

            <label>Destination</label>

            <div class="input-box">
              <span>🚩</span>

              <input
                v-model="destination"
                type="text"
                placeholder="e.g., Brandenburg Gate"
              />
            </div>

            <button type="submit" class="search-btn">
              Search Safe Route
            </button>

          </form>

        </div>

        <div class="map-wrapper">

          <div class="map-topbar">
            <h3>Berlin Safety Map</h3>
          </div>

          <div id="map-container">
            <div id="map"></div>
          </div>

        </div>

      </section>

    </main>

    <div id="chat-container"></div>

    <button class="chatbot-btn" type="button">
      💬
    </button>

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

export default {
  name: 'App',
  data() {
    return {
      map: null,
      sidebarCollapsed: false,
      startLocation: '',
      destination: ''
    };
  },
  mounted() {
    this.initMap();
    this.initChat();
  },
  methods: {
    initMap() {
      // Initialize the map
      //this.map = L.map('map').setView([52.5200, 13.4050], 12);
      this.map = L.map('map', {
        zoomControl: false // Disable the default top-left control
      }).setView([52.5200, 13.4050], 12);

      // Add zoom control back to the top-right
      L.control.zoom({ position: 'topright' }).addTo(this.map);
      // Point to your Docker Tile Server (Port 8081)
      L.tileLayer('http://localhost:8081/tile/{z}/{x}/{y}.png', {
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
        // 1. Create the script element
      const script = document.createElement('script');
      script.src = "https://cdn.jsdelivr.net/gh/logspace-ai/langflow-embedded-chat@v1.0.7/dist/build/static/js/bundle.min.js";
      
      script.onload = () => {
        // 2. Inject the custom element once the library is ready
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
          chatContainer.innerHTML = `
            <langflow-chat
              window_title="Simple Agent"
              flow_id="dd195420-870e-4896-8b6c-794902b319b1"
              host_url="http://localhost:7860"
              api_key="sk-XZOSAs4iJxFFXp0081ugpVHcgqko-eR68ZHlaoyNcAY">
            </langflow-chat>
          `;
        }
      };
      
      // 3. Append to body to trigger the download
      document.body.appendChild(script);

    },

    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    }
  }
};

</script>

<style>
body {
  margin: 0;
  background: #f3f6fb;
  font-family: Inter, Arial, sans-serif;
}

.home-layout {
  min-height: 100vh;
  display: flex;
}

.sidebar {
  width: 280px;
  background: white;
  padding: 28px;
  border-right: 1px solid #e5e7eb;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-box {
  width: 48px;
  height: 58px;
  border: 4px solid #16a34a;
  border-radius: 16px;
  display: grid;
  place-items: center;
  color: #16a34a;
  font-weight: bold;
}

.nav-menu {
  margin-top: 42px;
  display: grid;
  gap: 12px;
}

.nav-item {
  padding: 16px;
  border-radius: 12px;
  background: #f8fafc;
}

.main-content {
  flex: 1;
  padding: 28px;
}

.topbar h2 {
  font-size: 42px;
  margin-bottom: 10px;
}

.content-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 24px;
}

.search-panel,
.map-wrapper {
  background: white;
  border-radius: 22px;
  padding: 24px;
}

.input-box {
  height: 60px;
  border: 1px solid #dbe2ea;
  border-radius: 12px;
  display: flex;
  align-items: center;
  padding: 0 14px;
  margin-bottom: 18px;
}

.input-box input {
  flex: 1;
  border: 0;
  outline: 0;
}

.search-btn {
  width: 100%;
  height: 58px;
  border: 0;
  border-radius: 12px;
  background: #247ad2;
  color: white;
  font-weight: 700;
}

#map {
  width: 100%;
  height: 700px;
  border-radius: 18px;
}

.chatbot-btn {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  border: 0;
  background: #247ad2;
  color: white;
  font-size: 30px;
}

/* Sidebar collapsed styles */
.sidebar {
  transition: width 200ms ease;
}

.sidebar.collapsed {
  width: 72px;
  padding: 16px;
}

.sidebar.collapsed .brand-section > div {
  display: none;
}

.sidebar.collapsed .logo-box {
  width: 40px;
  height: 40px;
  border-width: 2px;
}

.sidebar-toggle {
  border: 0;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
  color: #374151;
  margin-left: auto;
}
</style>
