import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

// Dark "technical dashboard" theme (see DESIGN.md visual system).
const safepathDark = {
  dark: true,
  colors: {
    background: '#121212',
    surface: '#1E1E1E',
    'surface-light': '#252525',
    'surface-variant': '#2C2C2E',
    'on-surface-variant': '#98989D',
    primary: '#00E5FF',
    'on-primary': '#00131A',
    secondary: '#32D74B',
    'on-secondary': '#06210C',
    success: '#32D74B',
    warning: '#FF9F0A',
    error: '#FF453A',
    info: '#00E5FF',
    'on-background': '#FFFFFF',
    'on-surface': '#FFFFFF',
  },
};

// Light counterpart: same structure, inverted surfaces. The cyan accent is
// darkened so it stays readable on white.
const safepathLight = {
  dark: false,
  colors: {
    background: '#F2F2F7',
    surface: '#FFFFFF',
    'surface-light': '#F2F2F5',
    'surface-variant': '#E2E2E6',
    'on-surface-variant': '#6B6B70',
    primary: '#0097B2',
    'on-primary': '#FFFFFF',
    secondary: '#2AA745',
    'on-secondary': '#FFFFFF',
    success: '#2AA745',
    warning: '#C77700',
    error: '#D7362B',
    info: '#0097B2',
    'on-background': '#1A1A1A',
    'on-surface': '#1A1A1A',
  },
};

// Remember the user's choice across reloads; default to dark.
const savedTheme =
  (typeof localStorage !== 'undefined' && localStorage.getItem('safepath-theme')) || 'safepathDark';

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },
  theme: {
    defaultTheme: savedTheme,
    themes: { safepathDark, safepathLight },
  },
});

const app = createApp(App);
app.use(router);
app.use(vuetify);
app.mount('#app');