<template>
    <v-container fluid class="pa-4 pa-md-6">
        <v-card id="search-logs" rounded="lg" elevation="2" class="mb-3">
            <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                User Search Logs
                <div class="d-flex align-center ga-2">
                    <v-text-field v-model="searchLogFilter" label="Filter search logs" density="compact"
                        variant="outlined" hide-details prepend-inner-icon="mdi-magnify" style="width: 300px" />
                    <v-btn icon="mdi-refresh" variant="text" :loading="logsLoading" aria-label="Refresh search logs"
                        @click="loadSearchLogs" />
                </div>
            </v-card-title>
            <v-card-subtitle class="text-medium-emphasis mb-2">
                Track route searches with safety score and status.
            </v-card-subtitle>
            <v-progress-linear v-if="logsLoading" indeterminate color="primary" />
            <v-card-text>
                <v-alert v-if="logsError" type="error" variant="tonal" density="compact" class="mb-3">
                    {{ logsError }}
                </v-alert>
                <v-data-table :headers="searchLogHeaders" :items="filteredSearchLogs" :loading="logsLoading">
                    <!-- User = avatar + name + email -->
                    <template #item.user="{ item }">
                        <div class="d-flex align-center ga-2">
                            <v-avatar v-if="item.user_detail.role == 'Admin'" size="28" color="warning" variant="tonal">
                                {{ item.user_detail.userInitial }}</v-avatar>
                            <v-avatar v-else-if="item.user_detail.role == 'Member'" size="28" color="primary"
                                variant="tonal">
                                {{ item.user_detail.userInitial }}</v-avatar>
                            <v-avatar v-else size="28" color="success" variant="tonal">{{ item.user_detail.userInitial
                                }}</v-avatar>
                            <div v-if="item.user_detail.role == 'Admin'">
                                <div class="font-weight-medium">{{ item.user_detail.user }}</div>
                                <div class="text-caption text-medium-emphasis">{{ item.user_detail.email }}</div>
                            </div>
                            <div v-else-if="item.user_detail.role == 'Member'">
                                <div class="font-weight-medium">{{ item.user_detail.user }}</div>
                                <div class="text-caption text-medium-emphasis">{{ item.user_detail.email }}</div>
                            </div>
                            <div v-else>
                                <div class="font-weight-medium">{{ item.user_detail.role }}</div>
                            </div>
                        </div>
                    </template>

                    <!-- Safety score chip -->
                    <template #item.safetyScore="{ item }">
                        <v-chip size="small" variant="tonal" :color="getSafetyClass(item.safetyScore) === 'safe' ? 'success'
                            : getSafetyClass(item.safetyScore) === 'medium' ? 'warning' : 'error'">
                            {{ item.safetyScore }}/100
                        </v-chip>
                    </template>

                    <!-- Status chip -->
                    <template #item.status="{ item }">
                        <v-chip size="small" color="primary" variant="tonal">{{ item.status }}</v-chip>
                    </template>

                    <!-- Empty state -->
                    <template #no-data>
                        <div class="text-center text-medium-emphasis py-6">
                            {{ logsError ? 'No logs to show.' : 'No route searches yet.' }}
                        </div>
                    </template>
                </v-data-table>
            </v-card-text>
        </v-card>
    </v-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { adminService } from '../../services/api';

const router = useRouter();

const searchLogFilter = ref('');
const searchLogHeaders = [
    { title: 'Date/Time', key: 'timestamp' },
    { title: 'User', key: 'user' },
    { title: 'Start', key: 'start' },
    { title: 'Destination', key: 'destination' },
    { title: 'Safety Score', key: 'safetyScore' },
    { title: 'Status', key: 'status', sortable: false },
];

// Real route-search logs, fetched from the backend (Langfuse-sourced).
const searchLogs = ref([]);
const logsLoading = ref(false);
const logsError = ref('');

const loadSearchLogs = async () => {
    logsLoading.value = true;
    logsError.value = '';

    try {
        const { data } = await adminService.searchLogs({ minutes: 10080, limit: 100 });
        searchLogs.value = data.logs ?? [];
        console.log(data)
    } catch (err) {
        logsError.value =
            err.response?.data?.detail ||
            'Could not load search logs. Please try again.';
        searchLogs.value = [];
    } finally {
        logsLoading.value = false;
    }
};

onMounted(loadSearchLogs);

const filteredSearchLogs = computed(() => {
    const query = searchLogFilter.value.trim().toLowerCase();

    if (!query) {
        return searchLogs.value;
    }

    return searchLogs.value.filter((log) => {
        return [
            log.user,
            log.email,
            log.start,
            log.destination,
            log.date,
            log.time,
            log.status
        ]
            .join(' ')
            .toLowerCase()
            .includes(query);
    });
});

const getSafetyClass = (score) => {
    if (score >= 80) {
        return 'safe';
    }

    if (score >= 60) {
        return 'medium';
    }

    return 'risk';
};
</script>

<style scoped></style>