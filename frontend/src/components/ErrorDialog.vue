<template>
  <v-dialog v-model="errorState.show" max-width="440" persistent>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
        <span v-if="errorState.status">{{ errorState.status }} — </span>
        <span>{{ errorState.title }}</span>
      </v-card-title>
      <v-card-text>{{ errorState.message }}</v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="clearError">OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { errorState, clearError } from '@/services/errorStore';
</script>