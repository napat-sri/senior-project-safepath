<template>
  <v-app>
    <v-main>
      <RouterView />
    </v-main>
  </v-app>
</template>

<script setup>
import { watch } from 'vue';
import { useTheme } from 'vuetify';

// Keep the root <html> background in sync with the active theme so the area
// behind <v-app> (overscroll, short pages) never flashes the wrong colour.
const theme = useTheme();
watch(
  () => theme.current.value.colors.background,
  (background) => {
    document.documentElement.style.backgroundColor = background;
  },
  { immediate: true }
);
</script>
