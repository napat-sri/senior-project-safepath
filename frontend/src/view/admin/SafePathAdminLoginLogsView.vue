<template>
    <v-layout>
        <v-main>
            <v-container fluid class="pa-4 pa-md-6">
                <v-card id="search-logs" rounded="lg" elevation="2" class="mb-3">
                    <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                        Login Log Explorer
                        <div class="d-flex align-center ga-2">
                            <v-text-field v-model="searchLoginEvent" label="Filter Login events" density="compact"
                                variant="outlined" hide-details prepend-inner-icon="mdi-magnify" style="width: 300px"
                                clearable />
                            <v-btn icon="mdi-refresh" variant="text" :loading="loginsLoading"
                                aria-label="Refresh Login events" @click="refreshLoginLogs" />
                        </div>
                    </v-card-title>
                    <v-progress-linear v-if="loginsLoading" indeterminate color="primary" />
                    <v-card-text>
                        <v-alert v-if="loginsError" type="error" variant="tonal" density="compact" class="mb-3">
                            {{ loginsError }}
                        </v-alert>
                        <v-data-table :headers="loginEventHeaders" :items="filteredLoginEvents"
                            :loading="loginsLoading">
                            <template #item.eventTime="{ item }">
                                {{ item.eventTime }}
                            </template>
                            <template #item.status="{ item }">
                                <v-chip v-if="item.status == 'Success'" color="success" size="small" variant="flat"
                                    label>
                                    {{ item.status }}
                                </v-chip>
                                <v-chip v-else color="error" size="small" variant="flat" label>
                                    {{ item.status }}
                                </v-chip>
                            </template>
                        </v-data-table>
                    </v-card-text>
                </v-card>
            </v-container>
        </v-main>
    </v-layout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { adminService } from '../../services/api.js';

const loginEvents = ref([]);
const loginsLoading = ref(false);
const loginsError = ref('');
const page = ref(1);
const pageSize = 100;
const total = ref(0);

const loginEventHeaders = [
    { title: 'Timestamp', key: 'eventTime' },
    { title: 'Username', key: 'user' },
    { title: 'Email', key: 'email' },
    { title: 'Login via', key: 'provider' },
    { title: 'Status', key: 'status' },
];

const loadLoginLogs = async () => {
    loginsLoading.value = true;
    loginsError.value = '';
    try {
        const { data } = await adminService.loginEvents();
        loginEvents.value = data.events;
        total.value = data.total;
        console.log(data)
    } catch (err) {
        loginsError.value = err.response?.data?.detail || 'Could not load login history.';
    } finally { loginsLoading.value = false; }
};

const refreshLoginLogs = async () => {           // Refresh: poll Keycloak now, then reload
    try { await adminService.syncLoginEvents(); } catch (e) { /* surfaced by load() */ }
    await loadLoginLogs();
};

onMounted(loadLoginLogs);

const searchLoginEvent = ref('');
const filteredLoginEvents = computed(() => {
    const q = searchLoginEvent.value.trim().toLowerCase();
    if (!q) return loginEvents.value;
    return loginEvents.value.filter((i) =>
        [i.eventTime, i.user, i.email, i.provider]
            .join(' ').toLowerCase().includes(q));
});
</script>

<style scoped></style>