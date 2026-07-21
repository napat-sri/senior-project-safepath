import Keycloak from 'keycloak-js';

// One shared Keycloak instance for the whole app.
const keycloak = new Keycloak({
  url: process.env.VUE_APP_KEYCLOAK_URL,            // http://localhost:8090 || https://login.safepath.duckdns.org
  realm: process.env.VUE_APP_KEYCLOAK_REALM,        // safepath
  clientId: process.env.VUE_APP_KEYCLOAK_CLIENT_ID, // safepath-frontend
});

export default keycloak;