<template>
  <v-app-bar color="primary" scroll-behavior="elevate">
    <v-app-bar-nav-icon variant="text" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>

    <v-avatar rounded="lg" size="44">
      <v-img :src="safePathLogo" alt="SafePath Berlin logo" cover />
    </v-avatar>

    <v-toolbar-title>SafePath Berlin</v-toolbar-title>

    <template v-if="$vuetify.display.mdAndUp">
      <v-switch v-model="isLight" inset hide-details density="compact" color="black" class="me-2"
        true-icon="mdi-white-balance-sunny" false-icon="mdi-weather-night"></v-switch>
    </template>
  </v-app-bar>

  <v-navigation-drawer v-model="drawer" temporary class="pt-4">
    <v-list>
      <v-list-item v-if="isAuthenticated" :title="username" :subtitle="isAdmin ? 'Admin' : 'Member'">
        <template #prepend>
          <v-avatar size="40" color="primary" variant="tonal">
            <v-img v-if="avatar" :src="avatar" alt="Profile picture" cover />
            <v-icon v-else>mdi-account-circle</v-icon>
          </v-avatar>
        </template>
      </v-list-item>
      <v-list-item v-else title="Guest" subtitle="Not signed in" prepend-icon="mdi-account-outline" />
    </v-list>

    <v-divider></v-divider>

    <v-list density="comfortable">
      <v-list-item v-for="item in navItems" :key="item.title" :title="item.title" :prepend-icon="item.icon"
        :to="item.to" />
      <slot />
    </v-list>

    <template v-slot:append>
      <div class="pa-2">
        <v-btn v-if="isAuthenticated" block color="error" variant="tonal" prepend-icon="mdi-logout"
          @click="logout">Logout</v-btn>
        <v-btn v-else block color="primary" prepend-icon="mdi-login" @click="login">Login</v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTheme } from 'vuetify';
import { userService } from '../services/api';
import safePathLogo from '../assets/Berlin.png';
import keycloak from '../services/keycloak';

const router = useRouter();

// Optional explicit override; when null, the menu is derived from the user's role.
const props = defineProps({
  items: { type: Array, default: null },
  width: { type: [Number, String], default: 280 },
});

const avatar = ref('');

onMounted(async () => {
  if (!keycloak.authenticated) return;
  try {
    const { data } = await userService.getAvatar();
    if (data.avatar) avatar.value = data.avatar;
  } catch (err) {
    console.error('Failed to load avatar', err);
  }
});

const drawer = ref(false);

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

// ---- Identity / roles ----
const isAuthenticated = computed(() => !!keycloak.authenticated);
const isAdmin = computed(() => keycloak.authenticated && keycloak.hasRealmRole('Admin'));
const username = computed(
  () => keycloak.tokenParsed?.name || keycloak.tokenParsed?.preferred_username || 'Account'
);

// console.log('API request config:', keycloak.token);

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
    list.push({ title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/overview' });
  }
  return list;
});

// const login = () => keycloak.login({ redirectUri: window.location.origin + '/home' });
const login = () => router.push('/login');
const logout = () => keycloak.logout({ redirectUri: window.location.origin + '/home' });

</script>