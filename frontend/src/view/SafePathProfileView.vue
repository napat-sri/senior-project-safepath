<template>
    <SafePathNavDrawer />

    <v-main>
        <v-container fluid class="pa-3 pa-md-6">
            <v-row class="align-center justify-center">
                <v-col cols="9">
                    <v-card-title>
                        Profile Settings
                    </v-card-title>
                </v-col>
            </v-row>

            <v-row class="align-start justify-center">
                <v-col cols="9">
                    <v-card rounded="lg" elevation="2" class="mb-2">
                        <v-card-text class="d-flex align-center flex-wrap ga-4 ml-3">
                            <v-avatar size="60" variant="tonal" color="primary">
                                <v-icon v-if="isAdmin" icon="mdi-account-cog" color="warning" size="36"></v-icon>
                                <v-icon v-else icon="mdi-account" color="primary" size="36"></v-icon>
                            </v-avatar>

                            <v-list>
                                <v-list-item :title=user.name :subtitle="isAdmin ? 'Admin' : 'Member'" />
                            </v-list>
                        </v-card-text>
                    </v-card>

                    <v-card rounded="lg" elevation="2" class="mb-2 pa-md-3">
                        <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-2">
                            Personal Information
                        </v-card-title>
                        <v-divider />
                        <v-card-text>
                            <v-row>
                                <v-col cols="12" md="4">
                                    <h4>First Name</h4>
                                    <p class="font-weight-medium">{{ user.firstname }}</p>
                                </v-col>
                                <v-col cols="12" md="3">
                                    <h4>Last Name</h4>
                                    <p class="font-weight-medium">{{ user.lastname }}</p>
                                </v-col>
                            </v-row>
                            <v-row>
                                <v-col cols="12" md="4">
                                    <h4>Email address</h4>
                                    <p class="font-weight-medium">{{ user.email }}</p>
                                </v-col>
                                <v-col cols="12" md="3">
                                    <h4>Login Provider</h4>
                                    <p class="font-weight-medium">{{ user.provider }}</p>
                                </v-col>
                                <v-col cols="12" md="3">
                                    <h4>Member Since</h4>
                                    <p class="font-weight-medium">{{ user.memberSince }}</p>
                                </v-col>
                            </v-row>
                        </v-card-text>
                    </v-card>
                    <v-card rounded="lg" elevation="2" class="mb-3">
                        <v-card-text>
                            <v-btn variant="outlined" color="error" @click="openDeleteModal">Delete my
                                account</v-btn>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
    </v-main>

    <v-dialog v-model="showDeleteModal" max-width="500">
        <v-card rounded="lg" color="error">
            <template v-slot:title>
                <span class="font-weight-black">Delete account?</span>
            </template>
            <v-card-text class="bg-surface-light pt-4">
                <p class="text-emphasis mb-3">Permanently delete your SafePath account.<br>
                    Your saved profile data may be removed,
                    while incident reports may be anonymized for community safety.</p>
                <p class="text-medium-emphasis mb-3">This action cannot be undone. Type DELETE to confirm.</p>
                <v-text-field v-model="deleteConfirmText" label="Type DELETE" variant="outlined" density="comfortable"
                    :rules="confirmDelete" />
            </v-card-text>
            <v-card-actions class="bg-surface-light pt-4">
                <v-spacer />
                <v-btn variant="text" @click="closeDeleteModal">Cancel</v-btn>
                <v-btn color="error" :disabled="deleteConfirmText !== 'DELETE'" @click="deleteAccount">
                    Delete permanently
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { userService } from '../services/api.js';
import SafePathNavDrawer from '../components/SafePathNavDrawer.vue';
import keycloak from '../services/keycloak';

const router = useRouter();

const showDeleteModal = ref(false);
const deleteConfirmText = ref('');
const showEditModal = ref(false);
const isAdmin = computed(() => keycloak.authenticated && keycloak.hasRealmRole('Admin'));

console.log(keycloak.tokenParsed)

const user = ref({
    name: keycloak.tokenParsed?.name || keycloak.tokenParsed?.preferred_username || 'SafePath User',
    firstname: keycloak.tokenParsed?.given_name || '',
    lastname: keycloak.tokenParsed?.family_name || '',
    email: keycloak.tokenParsed?.email || '',
    provider: keycloak.tokenParsed?.identity_provider || 'email',
    memberSince: '',
});

onMounted(async () => {
    try {
        const { data } = await userService.me();
        if (data.memberSince) {
            user.value.memberSince = new Date(data.memberSince)
                .toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        }
        const avatarRes = await userService.getAvatar();
        if (avatarRes.data.avatar) {
            profilePreview.value = avatarRes.data.avatar;
        }
    } catch (err) {
        console.error('Failed to load profile', err);
    }
});

const editableProfile = ref({
    name: user.value.name,
    email: user.value.email
});

const userInitials = computed(() => {
    return user.value.name
        .split(' ')
        .map((part) => part.charAt(0))
        .join('')
        .slice(0, 2)
        .toUpperCase();
});

const openEditModal = () => {
    showEditModal.value = true;
};

const closeEditModal = () => {
    showEditModal.value = false;
};

const openDeleteModal = () => {
    deleteConfirmText.value = '';
    showDeleteModal.value = true;
};

const closeDeleteModal = () => {
    showDeleteModal.value = false;
    deleteConfirmText.value = '';
};

const confirmDelete = [
    value => {
        if (deleteConfirmText.value != "DELETE")
            return 'Enter DELETE to confirm'
    },
]

const deleteAccount = async () => {
    if (deleteConfirmText.value !== 'DELETE') {
        return;
    }

    try {
        await userService.deleteMe();
        closeDeleteModal();
        // Clears the session + token, then redirects. Don't use router.push here:
        // the browser would still hold a valid token for a now-deleted account.
        keycloak.logout({ redirectUri: window.location.origin });
    } catch (err) {
        console.error('Failed to delete account', err);
        // optionally surface an error message to the user here
    }
};
</script>

<style scoped></style>