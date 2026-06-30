<template>
  <v-navigation-drawer :rail="rail" permanent class="pt-4" :width="width" rail-width="88">
    <v-list-item class="mb-2">
      <template #prepend>
        <v-avatar rounded="lg" size="44">
          <v-img :src="safePathLogo" alt="SafePath Berlin logo" cover />
        </v-avatar>
      </template>
      <v-list-item-title class="font-weight-bold">SafePath</v-list-item-title>
      <v-list-item-subtitle>{{ subtitle }}</v-list-item-subtitle>
      <template #append>
        <v-btn icon="mdi-menu" variant="text" @click="toggleRail" />
      </template>
    </v-list-item>

    <v-list nav density="comfortable">
      <v-list-item
        v-for="item in items"
        :key="item.title"
        :title="item.title"
        :prepend-icon="item.icon"
        :to="item.to"
      />
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
  subtitle: {
    type: String,
    default: 'Berlin'
  },
  items: {
    type: Array,
    default: () => [
      { title: 'Dashboard', icon: 'mdi-map', to: '/home' },
      { title: 'Profile', icon: 'mdi-account', to: '/profile' },
      { title: 'Report Incident', icon: 'mdi-alert', to: '/incident' },
      { title: 'Overview Dashboard', icon: 'mdi-chart-box', to: '/overview' }
    ]
  },
  width: {
    type: [Number, String],
    default: 280
  }
});

const rail = ref(false);

const toggleRail = () => {
  rail.value = !rail.value;
};
</script>
