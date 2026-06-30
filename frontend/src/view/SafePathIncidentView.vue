<template>
    <v-layout class="app-shell">
        <SafePathNavDrawer />

        <v-main>
            <v-container fluid class="pa-4 pa-md-6">
                <v-card class="mb-4" rounded="lg" elevation="2">
                    <v-card-text>
                        <h2 class="text-h5 text-md-h4">Report an Incident</h2>
                        <p class="text-medium-emphasis mt-2">
                            Share safety incidents in Berlin. Evidence is optional and helps moderation.
                        </p>
                    </v-card-text>
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
                                            <v-select v-model="form.incidentType" label="Incident Type"
                                                :items="incidentTypes" variant="outlined" required />
                                        </v-col>
                                    </v-row>

                                    <v-text-field v-model="form.location" label="Location"
                                        placeholder="e.g., Alexanderplatz, Berlin" variant="outlined"
                                        :error-messages="validationErrors.location ? [validationErrors.location] : []"
                                        required />

                                    <v-row>
                                        <v-col cols="12" md="6">
                                            <v-text-field v-model="form.date" label="Date" type="date"
                                                variant="outlined" required />
                                        </v-col>
                                        <v-col cols="12" md="6">
                                            <v-text-field v-model="form.time" label="Time" type="time"
                                                variant="outlined" required />
                                        </v-col>
                                    </v-row>

                                    <v-textarea v-model="form.details" label="Incident Details"
                                        placeholder="Briefly describe what happened." variant="outlined" rows="4"
                                        :error-messages="validationErrors.details ? [validationErrors.details] : []"
                                        required />

                                    <v-file-input id="incident-evidence" label="Evidence Upload" variant="outlined"
                                        multiple accept="image/*,.pdf" prepend-icon="mdi-paperclip"
                                        @change="handleEvidenceUpload" />

                                    <p class="text-caption text-medium-emphasis mb-3">Optional: images or PDF files.</p>

                                    <v-alert v-if="submitMessage" type="success" variant="tonal" class="mb-4">
                                        {{ submitMessage }}
                                    </v-alert>

                                    <div class="d-flex justify-space-between align-center flex-wrap ga-3">
                                        <p class="text-caption text-medium-emphasis mb-0">
                                            Reports below are shown as frontend preview.
                                        </p>
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

                                <v-card v-for="report in reports" :key="report.id" variant="outlined" class="mb-3"
                                    rounded="lg">
                                    <v-card-text>
                                        <div class="d-flex justify-space-between align-start mb-2">
                                            <div>
                                                <p class="text-overline text-medium-emphasis">{{ report.incidentType }}
                                                </p>
                                                <h4 class="text-h6">{{ report.location }}</h4>
                                            </div>
                                            <v-chip size="small" color="warning" variant="tonal">Pending Review</v-chip>
                                        </div>

                                        <div
                                            class="d-flex justify-space-between text-caption text-medium-emphasis mb-2">
                                            <span>{{ report.reporterName || 'Anonymous' }}</span>
                                            <span>{{ formatDateTime(report.date, report.time) }}</span>
                                        </div>

                                        <p class="text-body-2">{{ report.details }}</p>

                                        <div v-if="report.evidence.length" class="d-flex flex-wrap ga-2 mt-3">
                                            <v-chip v-for="file in report.evidence" :key="`${report.id}-${file}`"
                                                size="small" variant="outlined">
                                                {{ file }}
                                            </v-chip>
                                        </div>
                                    </v-card-text>
                                </v-card>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
        </v-main>
    </v-layout>
</template>

<script setup>
import { reactive, ref } from 'vue';
import SafePathNavDrawer from '../components/SafePathNavDrawer.vue';

const submitMessage = ref('');
const validationErrors = reactive({
    location: '',
    details: ''
});

const form = reactive({
    reporterName: '',
    incidentType: '',
    location: '',
    date: '',
    time: '',
    details: '',
    evidence: []
});

const incidentTypes = [
    'Harassment',
    'Theft',
    'Unsafe area',
    'Suspicious activity',
    'Transport issue',
    'Other'
];

const reports = ref([
    {
        id: 1,
        reporterName: 'Anonymous',
        incidentType: 'Unsafe area',
        location: 'Kottbusser Tor, Berlin',
        date: '2026-06-25',
        time: '21:30',
        details: 'Poor lighting and uncomfortable crowding near the station entrance.',
        evidence: ['area-photo.jpg']
    },
    {
        id: 2,
        reporterName: 'M. P.',
        incidentType: 'Suspicious activity',
        location: 'Alexanderplatz, Berlin',
        date: '2026-06-24',
        time: '18:15',
        details: 'A user reported repeated suspicious behavior near the tram stop.',
        evidence: []
    }
]);

const handleEvidenceUpload = (files) => {
    const selected = Array.isArray(files) ? files : [];
    form.evidence = selected.map((file) => file.name);
};

const validateForm = () => {
    validationErrors.location = form.location.trim() ? '' : 'Location is required.';
    validationErrors.details = form.details.trim() ? '' : 'Incident details are required.';

    return (
        form.incidentType &&
        form.location.trim() &&
        form.date &&
        form.time &&
        form.details.trim()
    );
};

const submitReport = () => {
    submitMessage.value = '';

    if (!validateForm()) {
        return;
    }

    reports.value.unshift({
        id: Date.now(),
        reporterName: form.reporterName.trim() || 'Anonymous',
        incidentType: form.incidentType,
        location: form.location.trim(),
        date: form.date,
        time: form.time,
        details: form.details.trim(),
        evidence: [...form.evidence]
    });

    form.reporterName = '';
    form.incidentType = '';
    form.location = '';
    form.date = '';
    form.time = '';
    form.details = '';
    form.evidence = [];

    submitMessage.value = 'Incident report submitted successfully.';
};

const formatDateTime = (date, time) => {
    if (!date || !time) {
        return 'Date/time not provided';
    }

    return `${date} at ${time}`;
};
</script>

<style scoped>
.app-shell {
    min-height: 100vh;
}
</style>