<template>
  <div class="page-shell">
    <aside :class="['sidebar', { collapsed: sidebarCollapsed }]">
      <div class="brand-section">
        <img class="brand-logo" :src="safePathLogo" alt="SafePath Berlin logo" />

        <div class="brand-copy">
          <h2>SafePath</h2>
          <span>Berlin</span>
        </div>

        <button
          class="sidebar-toggle"
          type="button"
          aria-label="Toggle sidebar"
          @click="toggleSidebar"
        >
          ☰
        </button>
      </div>

      <nav class="nav-menu" aria-label="Primary navigation">
        <button type="button" class="nav-item" @click="goToHome">
          <span>🗺️</span>
          Dashboard
        </button>

        <button type="button" class="nav-item" aria-current="page" @click="$router.push('/profile')">
          <span>👤</span>
          Profile
        </button>

        <button type="button" class="nav-item active" aria-current="page" @click="$router.push('/incident')">
          <span>⚠️</span>
          Report Incident
        </button>

        <button type="button" class="nav-item" aria-label="Overview Dashboard" @click="$router.push('/overview')">
          <span>📊</span>
          Overview Dashboard
        </button>

        <button type="button" class="nav-item">
          <span>📋</span>
          Community Reports
        </button>
      </nav>

      <!-- <div class="premium-card card">
        <p class="premium-label">Community Safety</p>
        <h3>Report recent incidents</h3>
        <p>
          Your report helps SafePath Berlin improve community awareness and safer route suggestions.
        </p>
      </div> -->
    </aside>

    <main class="main-content">
      <header class="topbar card">
        <div>
          <h2>Report an Incident</h2>
          <p class="muted">
            Share recent safety incidents in Berlin. Evidence is optional, but it can help the team review the report.
          </p>
        </div>
      </header>

      <section class="content-grid incident-grid">
        <section class="search-panel card incident-panel">
          <div class="panel-header">
            <h3>Incident Details</h3>
            <span class="muted">Fill in the information below to submit a community safety report.</span>
          </div>

          <form class="incident-form" @submit.prevent="submitReport" novalidate>
            <div class="form-row two-columns">
              <div class="field-group">
                <label for="reporter-name">Reporter Name</label>
                <input
                  id="reporter-name"
                  v-model="form.reporterName"
                  class="input"
                  type="text"
                  placeholder="Anonymous or your name"
                />
              </div>

              <div class="field-group">
                <label for="incident-type">Incident Type *</label>
                <select id="incident-type" v-model="form.incidentType" class="input" required>
                  <option disabled value="">Select incident type</option>
                  <option>Harassment</option>
                  <option>Theft</option>
                  <option>Unsafe area</option>
                  <option>Suspicious activity</option>
                  <option>Transport issue</option>
                  <option>Other</option>
                </select>
              </div>
            </div>

            <div class="field-group">
              <label for="incident-location">Location *</label>
              <div class="input-wrap" :class="{ invalid: validationErrors.location }">
                <span>📍</span>
                <input
                  id="incident-location"
                  v-model="form.location"
                  class="search-input"
                  type="text"
                  placeholder="e.g., Alexanderplatz, Berlin"
                  required
                />
              </div>
              <p v-if="validationErrors.location" class="field-error">{{ validationErrors.location }}</p>
            </div>

            <div class="form-row two-columns">
              <div class="field-group">
                <label for="incident-date">Date *</label>
                <input id="incident-date" v-model="form.date" class="input" type="date" required />
              </div>

              <div class="field-group">
                <label for="incident-time">Time *</label>
                <input id="incident-time" v-model="form.time" class="input" type="time" required />
              </div>
            </div>

            <div class="field-group">
              <label for="incident-details">Incident Details *</label>
              <textarea
                id="incident-details"
                v-model="form.details"
                class="input textarea-input"
                placeholder="Briefly describe what happened. Avoid sharing highly sensitive personal information."
                required
              ></textarea>
              <p v-if="validationErrors.details" class="field-error">{{ validationErrors.details }}</p>
            </div>

            <div class="field-group">
              <label for="incident-evidence">Evidence Upload</label>
              <input
                id="incident-evidence"
                class="input"
                type="file"
                multiple
                accept="image/*,.pdf"
                @change="handleEvidenceUpload"
              />
              <p class="helper-copy">Optional: images or PDF files.</p>
            </div>

            <p v-if="submitMessage" class="success-message">{{ submitMessage }}</p>

            <div class="submit-row">
              <p class="helper-copy">
                Submitted reports are shown below as a frontend preview. Backend storage can be connected later.
              </p>

              <button type="submit" class="btn btn-primary">Submit Report</button>
            </div>
          </form>
        </section>

        <section class="search-panel card recent-panel">
          <div class="results-header">
            <div>
              <h3>Recently Submitted Reports</h3>
              <p class="muted">Latest reports submitted through this page.</p>
            </div>
            <span class="results-count">{{ reports.length }} reports</span>
          </div>

          <div v-if="reports.length" class="route-card-list">
            <article v-for="report in reports" :key="report.id" class="route-card card report-card">
              <div class="route-card-top">
                <div>
                  <p class="route-type">{{ report.incidentType }}</p>
                  <h4>{{ report.location }}</h4>
                </div>

                <div class="status-badge">
                  <span class="status-dot warning-dot"></span>
                  Pending Review
                </div>
              </div>

              <div class="route-meta">
                <span>{{ report.reporterName || 'Anonymous' }}</span>
                <span>{{ formatDateTime(report.date, report.time) }}</span>
              </div>

              <p class="route-summary">{{ report.details }}</p>

              <div v-if="report.evidence.length" class="evidence-list">
                <span v-for="file in report.evidence" :key="`${report.id}-${file}`">📎 {{ file }}</span>
              </div>
            </article>
          </div>

          <div v-else class="empty-results">
            No reports submitted yet.
          </div>
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import safePathLogo from '../assets/Berlin.png';

const router = useRouter();
const sidebarCollapsed = ref(true);
const submitMessage = ref('');
const validationErrors = reactive({
  location: '',
  details: '',
});

const form = reactive({
  reporterName: '',
  incidentType: '',
  location: '',
  date: '',
  time: '',
  details: '',
  evidence: [],
});

const reports = ref([
  {
    id: 1,
    reporterName: 'Anonymous',
    incidentType: 'Unsafe area',
    location: 'Kottbusser Tor, Berlin',
    date: '2026-06-25',
    time: '21:30',
    details: 'Poor lighting and uncomfortable crowding near the station entrance.',
    evidence: ['area-photo.jpg'],
  },
  {
    id: 2,
    reporterName: 'M. P.',
    incidentType: 'Suspicious activity',
    location: 'Alexanderplatz, Berlin',
    date: '2026-06-24',
    time: '18:15',
    details: 'A user reported repeated suspicious behavior near the tram stop.',
    evidence: [],
  },
]);

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};

const goToHome = () => {
  router.push('/home');
};

const handleEvidenceUpload = (event) => {
  form.evidence = Array.from(event.target.files || []).map((file) => file.name);
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
    evidence: [...form.evidence],
  });

  form.reporterName = '';
  form.incidentType = '';
  form.location = '';
  form.date = '';
  form.time = '';
  form.details = '';
  form.evidence = [];

  const evidenceInput = document.getElementById('incident-evidence');
  if (evidenceInput) {
    evidenceInput.value = '';
  }

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
/* =========================
   Global Page Setup
========================= */

:global(body) {
    margin: 0;
    background: var(--color-bg);
}

.page-shell {
    min-height: 100vh;
    display: flex;
    color: var(--color-text);
}


/* =========================
   Sidebar Container
========================= */

.sidebar {
    width: 248px;
    flex-shrink: 0;
    padding: 24px 18px;
    border-right: 1px solid var(--color-border);
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(14px);
    transition: width 200ms ease, padding 200ms ease;
}

.sidebar.collapsed {
    width: auto;
    padding: 16px;
}


/* =========================
   Sidebar Brand / Logo Area
========================= */

.brand-section {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
}

.brand-logo {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
    border-radius: 14px;
    object-fit: cover;
    border: 1px solid var(--color-border);
    background: var(--color-surface);
}

.brand-copy {
    flex: 1;
    min-width: 0;
}

.brand-copy span {
    display: block;
    margin-top: 2px;
    color: var(--color-primary);
    font-weight: 700;
}

.brand-copy p,
.panel-header p,
.topbar p,
.route-summary,
.route-pair,
.muted,
.helper-copy,
.premium-card p {
    color: var(--color-text-secondary);
}


/* =========================
   Sidebar Collapsed State
========================= */

.sidebar.collapsed .brand-logo,
.sidebar.collapsed .brand-copy,
.sidebar.collapsed .nav-menu,
.sidebar.collapsed .side-note {
    display: grid;
}

.sidebar.collapsed .premium-card {
    display: none;
}


/* =========================
   Sidebar Toggle Button
========================= */

.sidebar-toggle {
    margin-left: auto;
    border: 0;
    background: transparent;
    color: var(--color-text-secondary);
    font-size: 20px;
    cursor: pointer;
}


/* =========================
   Sidebar Navigation Menu
========================= */

.nav-menu {
    display: grid;
    gap: 10px;
    margin-top: 32px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 16px;
    border-radius: var(--radius-md);
    border: 1px solid transparent;
    background: #f8fafc;
    color: var(--color-text);
    text-decoration: none;
    cursor: pointer;
}

.nav-item.active {
    border-color: rgba(99, 102, 241, 0.22);
    background: rgba(99, 102, 241, 0.08);
    color: var(--color-primary);
}

.route-type {
  margin: 0 0 6px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 11px;
  color: var(--color-neutral);
}

/* =========================
   Main Content Layout
========================= */

.main-content {
    flex: 1;
    padding: 28px;
}

.topbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 10px;
    padding: 12px;
    margin-bottom: 12px;
}

.content-grid {
    display: grid;
    grid-template-columns: minmax(340px, 420px) minmax(0, 1fr);
    gap: 24px;
    align-items: start;
}

.content-grid.incident-grid {
  display: grid;
  grid-template-columns: minmax(340px, 820px);
  gap: 24px;
  align-items: start;
}

.search-panel,
.premium-card,
.empty-results,
.route-card {
  background: var(--color-surface);
}

.search-panel {
  padding: 18px;
}

.panel-header {
  margin-bottom: 18px;
}

.panel-header span {
  display: block;
  margin-top: 6px;
}

.incident-form {
  display: grid;
  gap: 14px;
}

.form-row.two-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.field-group {
  display: grid;
  gap: 8px;
}

label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  min-height: 56px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
}

.input-wrap.invalid {
  border-color: rgba(239, 68, 68, 0.6);
}

.search-input {
  width: 100%;
  border: 0;
  outline: 0;
  font: inherit;
  color: var(--color-text);
  background: transparent;
}

.textarea-input {
  min-height: 132px;
  resize: vertical;
  line-height: 1.5;
}

.field-error,
.helper-copy,
.success-message {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
}

.field-error {
  color: var(--color-error);
}

.success-message {
  color: var(--color-success);
  font-weight: 600;
}

.submit-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 4px;
}

.results-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.results-header p {
  margin: 6px 0 0;
}

.results-count,
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.9);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.route-card-list {
  display: grid;
  gap: 14px;
}

.route-card {
  padding: 18px;
}

.route-card-top,
.route-meta {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.route-card h4 {
  margin: 0;
}

.route-meta {
  margin: 14px 0 10px;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.route-summary {
  margin: 12px 0 0;
}

.evidence-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.evidence-list span {
  display: inline-flex;
  align-items: center;
  padding: 7px 10px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--color-border);
  background: #f8fafc;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.warning-dot {
  background: var(--color-warning);
}

.empty-results {
  padding: 18px;
  border: 1px dashed var(--color-border);
  color: var(--color-text-secondary);
}

@media (max-width: 1379px) {
  .content-grid.incident-grid {
    grid-template-columns: 1fr;
  }

  .brand-section {
    position: sticky;
    top: 0;
    z-index: 1;
    padding-bottom: 8px;
    background: var(--color-surface);
  }

  .sidebar-toggle {
    width: 36px;
    height: 36px;
    border-radius: 999px;
    border: 1px solid var(--color-border);
    background: rgba(255, 255, 255, 0.9);
  }

  .main-content {
    padding: 18px;
    padding-bottom: 110px;
  }

  .topbar,
  .results-header,
  .route-card-top,
  .route-meta,
  .submit-row {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .form-row.two-columns {
    grid-template-columns: 1fr;
  }
}
</style>
