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