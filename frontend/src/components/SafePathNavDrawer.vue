<template>
  <v-app-bar color="primary">
    <v-app-bar-nav-icon variant="text" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>

    <v-avatar rounded="lg" size="44">
      <v-img :src="safePathLogo" alt="SafePath Berlin logo" cover />
    </v-avatar>

    <v-toolbar-title>SafePath Berlin</v-toolbar-title>

    <template v-if="$vuetify.display.mdAndUp">
      <v-switch v-model="isLight" inset hide-details density="compact" color="black" class="me-2"
        true-icon="mdi-white-balance-sunny" false-icon="mdi-weather-night"></v-switch>
    </template>

    <!-- <template v-if="$vuetify.display.mdAndUp">
          <v-btn icon="mdi-magnify" variant="text"></v-btn>

          <v-btn icon="mdi-filter" variant="text"></v-btn>
        </template>

<v-btn icon="mdi-dots-vertical" variant="text"></v-btn> -->
  </v-app-bar>

  <!-- <v-navigation-drawer v-model="drawer" :rail="rail" permanent class="pt-4" :width="width" rail-width="88"> -->

  <v-navigation-drawer v-model="drawer" temporary class="pt-4">
    <v-list>
      <v-list-item v-if="isAuthenticated" :title="username" :subtitle="isAdmin ? 'Admin' : 'Member'"
        prepend-icon="mdi-account-circle" />
      <v-list-item v-else title="Guest" subtitle="Not signed in" prepend-icon="mdi-account-outline" />
    </v-list>

    <v-divider></v-divider>

    <v-list density="comfortable">
      <v-list-item v-for="item in navItems" :key="item.title" :title="item.title" :prepend-icon="item.icon"
        :to="item.to" />
      <slot />
    </v-list>

    <template #append>
      <div class="pa-2">
        <v-btn v-if="isAuthenticated" block color="error" variant="tonal" prepend-icon="mdi-logout"
          @click="logout">Logout</v-btn>
        <v-btn v-else block color="primary" prepend-icon="mdi-login" @click="login">Login</v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>
<!-- <v-navigation-drawer v-model="drawer" temporary class="pt-4">
    <v-list>
      <v-list-item prepend-avatar="https://randomuser.me/api/portraits/men/85.jpg" title="John Leider">
      </v-list-item>
    </v-list>

    <v-divider></v-divider>
    <v-list density="comfortable">
      <v-list-item v-for="item in items" :key="item.title" :title="item.title" :prepend-icon="item.icon"
        :to="item.to" />
      <slot />
    </v-list>
  </v-navigation-drawer>
</template> -->

<script setup>
import { computed, ref } from 'vue';
import { useTheme } from 'vuetify';
import safePathLogo from '../assets/Berlin.png';
import keycloak from '../services/keycloak';

// Optional explicit override; when null, the menu is derived from the user's role.
const props = defineProps({
  items: { type: Array, default: null },
  width: { type: [Number, String], default: 280 },
});

const drawer = ref(false);

// ---- Identity / roles ----
const isAuthenticated = computed(() => !!keycloak.authenticated);
const isAdmin = computed(() => keycloak.authenticated && keycloak.hasRealmRole('Admin'));
const username = computed(
  () => keycloak.tokenParsed?.name || keycloak.tokenParsed?.preferred_username || 'Account'
);

// Home for everyone; member items when logged in; Dashboard only for admins.
const navItems = computed(() => {
  if (props.items) return props.items;                       // explicit override still works
  const list = [{ title: 'Home', icon: 'mdi-home', to: '/home' }];
  if (isAuthenticated.value) {
    list.push(
      { title: 'Profile', icon: 'mdi-account', to: '/profile' },
      { title: 'Report Incident', icon: 'mdi-alert', to: '/incident' }
    );
  }
  if (isAdmin.value) {
    list.push({ title: 'Dashboard', icon: 'mdi-chart-box', to: '/overview' });
  }
  return list;
});

const login = () => keycloak.login({ redirectUri: window.location.origin + '/home' });
const logout = () => keycloak.logout({ redirectUri: window.location.origin + '/home' });

// ---- Light/dark toggle (unchanged) ----
const theme = useTheme();
const isLight = computed({
  get: () => theme.name.value === 'safepathLight',
  set: (value) => {
    const next = value ? 'safepathLight' : 'safepathDark';
    theme.change(next);
    localStorage.setItem('safepath-theme', next);
  },
});
</script>

<!-- // The single source of truth for the main app navigation.
// Change a label, icon, or route here and every view that uses the
// default menu updates. Pass a custom `items` array (e.g. the admin
// view) to override it.
defineProps({
  items: {
    type: Array,
    default: () => [
      { title: 'Home', icon: 'mdi-home', to: '/home' },
      { title: 'Profile', icon: 'mdi-account', to: '/profile' },
      { title: 'Report Incident', icon: 'mdi-alert', to: '/incident' },
      { title: 'Dashboard', icon: 'mdi-chart-box', to: '/overview' }
    ]
  },
  width: {
    type: [Number, String],
    default: 280
  }
});

const drawer = ref(false)

// Light/dark toggle. The switch is "on" for light mode (sun icon); the choice
// is applied globally via Vuetify and remembered across reloads.
const theme = useTheme();
const isLight = computed({
  get: () => theme.name.value === 'safepathLight',
  set: (value) => {
    const next = value ? 'safepathLight' : 'safepathDark';
    theme.change(next);
    localStorage.setItem('safepath-theme', next);
  }
});
</script> -->
