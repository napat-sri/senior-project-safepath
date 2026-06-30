<template>
  <v-app-bar color="primary">
    <v-app-bar-nav-icon variant="text" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>

    <v-avatar rounded="lg" size="44">
      <v-img :src="safePathLogo" alt="SafePath Berlin logo" cover />
    </v-avatar>

    <v-toolbar-title>SafePath Berlin</v-toolbar-title>

    <!-- <template v-if="$vuetify.display.mdAndUp">
          <v-btn icon="mdi-magnify" variant="text"></v-btn>

          <v-btn icon="mdi-filter" variant="text"></v-btn>
        </template>

<v-btn icon="mdi-dots-vertical" variant="text"></v-btn> -->
  </v-app-bar>

  <!-- <v-navigation-drawer v-model="drawer" :rail="rail" permanent class="pt-4" :width="width" rail-width="88"> -->
  <v-navigation-drawer expand-on-hover rail permanent class="pt-4">
    <v-list>
      <v-list-item prepend-avatar="https://randomuser.me/api/portraits/men/85.jpg" title="John Leider">
      </v-list-item>
    </v-list>

    <v-divider></v-divider>
    <v-list nav density="comfortable">
      <v-list-item v-for="item in items" :key="item.title" :title="item.title" :prepend-icon="item.icon"
        :to="item.to" />
      <slot />
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { ref } from 'vue';
import safePathLogo from '../assets/Berlin.png';

// The single source of truth for the main app navigation.
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
const rail = ref(false);

const toggleRail = () => {
  rail.value = !rail.value;
};
</script>
