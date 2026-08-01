<template>
    <SafePathNavDrawer />

    <v-main>
        <v-container fluid class="pa-4 pa-md-6">
            <v-card class="mb-4" rounded="lg" elevation="2">
                <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                    Report an Incident
                </v-card-title>
                <v-card-subtitle class="text-medium-emphasis mb-2">
                    Share safety incidents in Berlin. Evidence is optional and helps moderation.
                </v-card-subtitle>
            </v-card>

            <v-row>
                <v-col cols="12" lg="7">
                    <v-card rounded="lg" elevation="2">
                        <v-card-title>Incident Details</v-card-title>
                        <v-card-subtitle>Fill in information below to submit a safety report.</v-card-subtitle>
                        <v-card-text>
                            <v-form @submit.prevent="submitReport">
                                <v-row>
                                    <v-col cols="12" md="6">
                                        <v-text-field v-model="form.reporterName" label="Reporter Name"
                                            placeholder="Anonymous or your name" variant="outlined" />
                                    </v-col>
                                    <v-col cols="12" md="6">
                                        <v-select v-model="form.incidentType" label="Incident Type *"
                                            :items="incidentTypes" variant="outlined" required :rules="[rules.type]" />
                                    </v-col>
                                </v-row>

                                <v-text-field v-model="reportLocation" label="Location"
                                    placeholder="e.g., Alexanderplatz" variant="outlined" density="comfortable"
                                    :error-messages="startError ? [startError] : []" @focus="startFocused = true"
                                    @blur="handleFieldBlur('start')" />
                                <v-list v-if="startSuggestions.length && startFocused" density="compact"
                                    class="mb-3 suggestion-list">
                                    <v-list-item v-for="suggestion in startSuggestions"
                                        :key="`start-${suggestion.display_name}`" :title="suggestion.display_name"
                                        @mousedown.prevent="selectSuggestion('start', suggestion)" />
                                </v-list>

                                <v-row>
                                    <v-col cols="12" md="6">
                                        <v-text-field v-model="form.date" label="Date *" type="date" variant="outlined"
                                            required :rules="[rules.date]" />
                                    </v-col>
                                    <v-col cols="12" md="6">
                                        <v-text-field :model-value="form.time" label="Time *" variant="outlined"
                                            prepend-inner-icon="mdi-clock-time-four-outline" required
                                            :rules="[rules.time]">
                                            <v-menu v-model="showMenu" :close-on-content-click="false"
                                                activator="parent" min-width="0">
                                                <v-time-picker format="24hr" color="primary"
                                                    v-model="form.time"></v-time-picker>
                                            </v-menu>
                                        </v-text-field>
                                    </v-col>
                                </v-row>

                                <v-textarea v-model="form.details" label="Incident Details *"
                                    placeholder="Briefly describe what happened." variant="outlined" rows="4"
                                    :error-messages="validationErrors.details ? [validationErrors.details] : []"
                                    required />

                                <v-alert v-if="submitMessage" type="success" variant="tonal" class="mb-4">
                                    {{ submitMessage }}
                                </v-alert>

                                <div class="d-flex justify-space-between align-center flex-wrap ga-3">
                                    <v-btn type="submit" color="primary">Submit Report</v-btn>
                                </div>
                            </v-form>
                        </v-card-text>
                    </v-card>
                </v-col>

                <v-col cols="12" lg="5">
                    <v-card rounded="lg" elevation="2">
                        <v-card-title class="d-flex justify-space-between align-center">
                            <span>Recently Submitted Reports</span>
                            <v-chip color="primary" size="small" variant="tonal">{{ reports.length }}
                                reports</v-chip>
                        </v-card-title>
                        <v-card-subtitle>Latest reports submitted through this page.</v-card-subtitle>
                        <v-card-text>
                            <v-alert v-if="!reports.length" type="info" variant="tonal">No reports submitted
                                yet.</v-alert>

                            <v-card v-for="report in paginatedReports" :key="report.id" variant="outlined"
                                class="mb-2" rounded="lg">
                                <v-card-text>
                                    <div class="d-flex justify-space-between align-start">
                                        <div>
                                            <v-chip :color="incidentTypeColor(report.incidentType)" size="small"
                                                variant="tonal" label>
                                                {{ report.incidentType }}
                                            </v-chip>
                                            <h4 class="text-h6">{{ report.location }}</h4>
                                        </div>
                                    </div>

                                    <div class="d-flex justify-space-between text-caption text-medium-emphasis mb-1">
                                        <span>{{ report.reporterName || 'Anonymous' }}</span>
                                        <span>{{ formatDateTime(report.date, report.time) }}</span>
                                    </div>

                                    <p class="text-body-2">{{ report.details }}</p>
                                </v-card-text>
                            </v-card>
                            <div class="text-center">
                                <v-pagination v-model="page" :length="pageCount" :total-visible="5"></v-pagination>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
    </v-main>
</template>

<script setup>
import { reactive, ref, watch, computed, onMounted } from 'vue';
import { placeService, incidentService } from '../services/api';
import SafePathNavDrawer from '../components/SafePathNavDrawer.vue';
import { validateBerlinLocation } from '../data/routeAnalysis';
import { incidentTypeColor } from '../data/incidentTypes.js'

const reports = ref([]);      // was a 2-item mock array — start empty, load from API

const loadRecent = async () => {
    try {
        const { data } = await incidentService.recent({ limit: 10 });
        reports.value = data.incidents || [];
    } catch (e) {
        reports.value = [];
    }
};
onMounted(loadRecent);

const reportLocation = ref('');
const startSuggestions = ref([]);
const startFocused = ref(false);
const startTouched = ref(false);
const selectedStartPlace = ref(null);
const skipStartWatch = ref(false);
const hasSearched = ref(false);
const startError = computed(() => {
    if (!hasSearched.value) return '';
    return validateBerlinLocation(reportLocation.value);
});
const page = ref(1)
const itemsPerPage = 2

const pageCount = computed(() => Math.ceil(reports.value.length / itemsPerPage))

const paginatedReports = computed(() => {
  const start = (page.value - 1) * itemsPerPage
  return reports.value.slice(start, start + itemsPerPage)
});
const suggestionCache = {};
async function fetchSuggestions(query) {
    if (!query || query.trim().length < 3) return [];
    const normalizedQuery = query.trim().toLowerCase();
    if (suggestionCache[normalizedQuery]) {
        return suggestionCache[normalizedQuery];
    }
    try {
        const { data } = await placeService.search(query);
        console.log("query: ", query)
        console.log("data: ", data)
        const results = data.places || [];
        suggestionCache[normalizedQuery] = results;
        return results;
    } catch (error) {
        return [];
    }
}

let startDebounceTimer = null;
watch(reportLocation, async (value) => {
    if (skipStartWatch.value) {
        skipStartWatch.value = false;
        return;
    }
    clearTimeout(startDebounceTimer);
    startDebounceTimer = setTimeout(async () => {
        startSuggestions.value = await fetchSuggestions(value);
    }, 500);
});

function selectSuggestion(type, suggestion) {
    if (type === 'start') {
        console.log(suggestion)
        skipStartWatch.value = true;
        reportLocation.value = suggestion.display_name;
        selectedStartPlace.value = suggestion;
        startSuggestions.value = [];
        startFocused.value = false;
    }
    else {
        console.log("error")
    }
}

function handleFieldBlur(field) {
    window.setTimeout(() => {
        if (field === 'start') {
            startTouched.value = true;
            startFocused.value = false;
        }
    }, 120);
}

const submitMessage = ref('');
const validationErrors = reactive({
    location: '',
    details: ''
});
const rules = {
    type: (value) => !!value || 'Incident Type is required',
    location: (value) => !!String(value ?? '').trim() || 'Location is required',
    date: (value) => !!value || 'Date is required',
    time: (value) => !!value || 'Time is required',
};
const showMenu = ref(false)

const form = reactive({
    reporterName: '',
    incidentType: '',
    location: reportLocation.value,
    date: '',
    time: '',
    details: '',
    evidence: []
});

watch(reportLocation, (value) => {
    form.location = value;
}, { immediate: true });

const incidentTypes = [
    'Harassment',
    'Theft',
    'Unsafe area',
    'Suspicious activity',
    'Transport issue',
    'Other'
];

const handleEvidenceUpload = (files) => {
    const selected = Array.isArray(files) ? files : [];
    form.evidence = selected.map((file) => file.name);
};

const validateForm = () => {
    validationErrors.location = reportLocation.value.trim() ? '' : 'Location is required.';
    validationErrors.details = form.details.trim() ? '' : 'Incident details are required.';
    console.log(form)

    return (
        form.incidentType &&
        form.location.trim() &&
        form.date &&
        form.time &&
        form.details.trim()
    );
};

const submitReport = async () => {
    hasSearched.value = true;
    submitMessage.value = '';
    if (!validateForm()) return;

    try {
        await incidentService.create({
            reporterName: form.reporterName.trim() || 'Anonymous',
            incidentType: form.incidentType,
            location: form.location.trim(),
            latitude: selectedStartPlace.value?.lat ?? null,
            longitude: selectedStartPlace.value?.lng ?? null,
            date: form.date,
            time: form.time,
            details: form.details.trim(),
            evidence: [...form.evidence],
        });

        // reset the form (same fields as today)
        form.reporterName = '';
        form.incidentType = '';
        form.location = '';
        form.date = '';
        form.time = '';
        form.details = '';
        form.evidence = [];
        reportLocation.value = '';
        selectedStartPlace.value = null;

        submitMessage.value = 'Incident report submitted successfully.';
        await loadRecent();               // refresh the panel from the DB
    } catch (err) {
        submitMessage.value = '';
        // optionally surface err.response?.data?.detail in an error alert
    }
};

const formatDateTime = (date, time) => {
    if (!date || !time) {
        return 'Date/time not provided';
    }

    return `${date} at ${time}`;
};
</script>

<style scoped></style>