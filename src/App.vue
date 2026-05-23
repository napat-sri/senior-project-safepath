<template>
  <SafePathHomeView />
</template>

<script>
import SafePathHomeView from './view/SafePathHomeView.vue'
import SafePathLoginView from './view/SafePathLoginView.vue'
import SafePathRegisterView from './view/SafePathRegisterView.vue'

// 4. Resolve environment-driven configuration with sensible fallbacks so the
//    app still boots if a teammate forgot to copy .env.example to .env.
const TILE_URL =
  process.env.VUE_APP_TILE_URL || 'http://localhost:8081/tile/{z}/{x}/{y}.png';
const LANGFLOW_HOST =
  process.env.VUE_APP_LANGFLOW_HOST || 'http://localhost:7860';
const LANGFLOW_FLOW_ID = process.env.VUE_APP_LANGFLOW_FLOW_ID || '';
const LANGFLOW_API_KEY = process.env.VUE_APP_LANGFLOW_API_KEY || '';

export default {
  components: {
    SafePathHomeView
  }
}
</script>
