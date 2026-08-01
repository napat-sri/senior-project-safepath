<template>
    <v-layout>
        <v-main>
            <v-container fluid class="pa-4 pa-md-6">
                <v-card id="users" rounded="lg" elevation="2">
                    <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                        User Management
                        <div class="d-flex align-center ga-2">
                            <v-text-field v-model="userSearch" label="Search by name or email" variant="outlined"
                                density="compact" prepend-inner-icon="mdi-magnify" hide-details style="width: 300px"
                                name="admin-user-search" autocomplete="off" clearable />
                            <v-btn variant="outlined" color="primary" @click="openUserModal()"
                                prepend-icon="mdi-account-plus">
                                Add User
                            </v-btn>
                            <v-btn icon="mdi-refresh" variant="text" :loading="usersLoading" aria-label="Refresh user"
                                @click="fetchUsers" />
                        </div>
                    </v-card-title>
                    <v-card-subtitle class="text-medium-emphasis mb-2">
                        Manage user roles and account status.
                    </v-card-subtitle>
                    <v-progress-linear v-if="usersLoading" indeterminate color="primary" />
                    <v-card-text>

                        <v-alert v-if="usersError" type="error" variant="tonal" class="mb-3" closable
                            @click:close="usersError = null">
                            {{ usersError }}
                        </v-alert>

                        <v-data-table>
                            <thead>
                                <tr>
                                    <th>Name/Email</th>
                                    <th>Role</th>
                                    <th>Provider</th>
                                    <th>Created At</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-if="!logsLoading && !users.length">
                                    <td colspan="6" class="text-center text-medium-emphasis py-6">No users found.</td>
                                </tr>
                                <tr v-for="user in users" :key="user.id">
                                    <td>
                                        <div class="d-flex align-center ga-2">
                                            <v-avatar size="28" color="primary" variant="tonal">{{ user.initial
                                            }}</v-avatar>
                                            <div>
                                                <div class="font-weight-medium">{{ user.name }}</div>
                                                <div class="text-caption text-medium-emphasis">{{ user.email }}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>{{ user.role }}</td>
                                    <td>{{ user.provider }}</td>
                                    <td>{{ user.createdAt }}</td>
                                    <td>
                                        <div class="d-flex ga-2">
                                            <v-tooltip text="Edit">
                                                <template v-slot:activator="{ props }">
                                                    <v-btn size="small" variant="text" color="primary" v-bind="props"
                                                        @click="openUserModal(user)" icon="mdi-pencil"></v-btn>
                                                </template>
                                            </v-tooltip>
                                            <v-tooltip text="Delete">
                                                <template v-slot:activator="{ props }">
                                                    <v-btn size="small" variant="text" color="error" v-bind="props"
                                                        @click="openDeleteUserModal(user)" icon="mdi-delete"></v-btn>
                                                    <!-- @click="deleteUser(user.id)" icon="mdi-delete"></v-btn> -->
                                                </template>
                                            </v-tooltip>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </v-data-table>
                        <div class="d-flex justify-end mt-3" v-if="totalUsers > pageSize">
                            <v-pagination v-model="page" :length="Math.ceil(totalUsers / pageSize)" density="compact" />
                        </div>
                    </v-card-text>
                </v-card>
            </v-container>
        </v-main>
    </v-layout>

    <v-dialog v-model="showUserModal" max-width="560">
        <v-card rounded="lg" color="info">
            <template v-slot:title>
                <span class="font-weight-black">{{ selectedUser ? 'Update user access' : 'Add new user' }}</span>
            </template>
            <v-card-text class="bg-surface-light pt-4">
                <v-text-field v-model="userForm.name" label="Name" variant="outlined" class="mb-3" />
                <v-text-field v-model="userForm.email" label="Email" variant="outlined" class="mb-3" />
                <v-select v-model="userForm.role" :items="['Admin', 'Member']" label="Role" variant="outlined"
                    class="mb-3" />
            </v-card-text>
            <v-card-actions class="bg-surface-light pt-4">
                <v-spacer />
                <v-btn variant="text" @click="closeUserModal">Cancel</v-btn>
                <v-btn color="primary" @click="saveUser">Save User</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-dialog v-model="showDeleteUserModal" max-width="500">
        <v-card rounded="lg" color="error">
            <template v-slot:title>
                <span class="font-weight-black">Delete account?</span>
            </template>
            <v-card-text class="bg-surface-light pt-1">
                <p class="text-emphasis mb-2">Are you sure you want to delete "<b>{{ userToDelete?.name }}</b>"?</p>
                <p class="text-medium-emphasis mb-2">This action cannot be undone.</p>
            </v-card-text>
            <v-card-actions class="bg-surface-light">
                <v-spacer />
                <v-btn variant="text" @click="closeDeleteUserModal">Cancel</v-btn>
                <v-btn color="error" @click="deleteUser">
                    Delete
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000" timer="top" location="bottom"
        prepend-icon="mdi-check-circle">
        {{ snackbar.text }}
        <template v-slot:actions>
            <v-btn variant="text" @click="snackbar.show = false">Close</v-btn>
        </template>
    </v-snackbar>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { adminService } from '../../services/api.js';
import SafePathNavDrawer from '../../components/SafePathNavDrawer.vue';
import SafePathAdminSearchLogs from '../admin/SafePathAdminSearchLogsView.vue'

const router = useRouter();

const adminMenu = [
    { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/overview' },
    { title: 'Profile', icon: 'mdi-account', to: '/profile' },
    { title: 'Report Incident', icon: 'mdi-alert', to: '/incident' }
];

const searchLogFilter = ref('');
const incidentStatusFilter = ref('All');
const showUserModal = ref(false);
const selectedUser = ref(null);
const showDeleteUserModal = ref(false);
const userToDelete = ref(null);
const snackbar = ref({
    show: false,
    text: '',
    color: 'success',
});

const notify = (text, color = 'success') => {
    snackbar.value = { show: true, text, color };
};

const tab = ref('Overview')

const users = ref([]);
const usersLoading = ref(false);
const usersError = ref(null);
const userSearch = ref('');
const page = ref(1);
const pageSize = 20;
const totalUsers = ref(0);

const fetchUsers = async () => {
    usersLoading.value = true;
    usersError.value = '';
    try {
        const { data } = await adminService.listUsers({
            search: userSearch.value,
            first: (page.value - 1) * pageSize,
            max: pageSize,
        });
        users.value = data.users;
        totalUsers.value = data.total;
    } catch (err) {
        usersError.value = err.response?.data?.detail || 'Failed to load users.';
    } finally {
        usersLoading.value = false;
    }
};

onMounted(fetchUsers);

// Debounce search so we don't fire a request on every keystroke; reset to
// page 1 whenever the query changes (a stale page number could be out of
// range for the new, smaller result set).
let searchDebounce;
watch(userSearch, () => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => {
        page.value = 1;
        fetchUsers();
    }, 300);
});
watch(page, fetchUsers);

const userForm = ref({
    name: '',
    email: '',
    role: 'Member',
});

const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
};

const openUserModal = (user = null) => {
    selectedUser.value = user;

    if (user) {
        userForm.value = {
            name: user.name,
            email: user.email,
            role: user.role,
        };
    } else {
        userForm.value = {
            name: '',
            email: '',
            role: 'Member',
        };
    }

    showUserModal.value = true;
};

const closeUserModal = () => {
    showUserModal.value = false;
    selectedUser.value = null;
};

const saveUser = async () => {
    usersError.value = null;
    try {
        if (selectedUser.value) {
            await adminService.updateUser(selectedUser.value.id, { ...userForm.value });
            notify(`User "${userForm.value.name}" updated.`);        // <-- edit success
        } else {
            await adminService.createUser({ ...userForm.value });
            notify(`User "${userForm.value.name}" added.`);          // <-- add success
        }
        closeUserModal();
        await fetchUsers();
    } catch (err) {
        usersError.value = err.response?.data?.detail || 'Failed to save user.';
    }
};

const openDeleteUserModal = (user) => {
    userToDelete.value = user;
    showDeleteUserModal.value = true;
};

const closeDeleteUserModal = () => {
    showDeleteUserModal.value = false;
    userToDelete.value = null;
};

const deleteUser = async () => {
    if (!userToDelete.value) return;
    usersError.value = null;
    try {
        const name = userToDelete.value.name;
        await adminService.deleteUser(userToDelete.value.id);
        closeDeleteUserModal();
        await fetchUsers();
        notify(`User "${name}" deleted.`, 'success');                // <-- delete success
    } catch (err) {
        usersError.value = err.response?.data?.detail || 'Failed to delete user.';
    }
};
</script>

<style scoped></style>