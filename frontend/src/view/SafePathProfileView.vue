<template>
    <v-layout class="app-shell">
        <SafePathNavDrawer />

        <v-main>
            <v-container fluid class="pa-4 pa-md-6">
                <v-card class="mb-3" rounded="lg" elevation="2">
                    <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                        Profile Settings
                        <v-btn variant="outlined" color="error" @click="logout">Logout</v-btn>
                    </v-card-title>
                    <v-card-subtitle class="text-medium-emphasis mb-2">Manage account details, image, and
                        privacy-sensitive actions.
                    </v-card-subtitle>
                </v-card>

                <v-alert variant="outlined" color="warning" icon="$warning" rounded="lg" elevation="2" class="mb-4"
                    title="Privacy Notice" text="SafePath Berlin uses account information only for login, profile settings, 
                    route features, and safety preferences.">
                </v-alert>

                <v-row>
                    <v-col cols="12">
                        <v-card rounded="lg" elevation="2" class="mb-4">
                            <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-3">
                                Account Overview
                                <div></div>
                                <v-btn variant="outlined" color="primary" @click="openEditModal()">Edit Profile</v-btn>
                            </v-card-title>

                            <v-card-text class="d-flex align-center flex-wrap ga-4">
                                <v-avatar size="76" rounded="xl" color="primary" variant="tonal">
                                    <v-img v-if="profilePreview" :src="profilePreview" alt="Profile preview" cover />
                                    <span v-else class="text-h6">{{ userInitials }}</span>
                                </v-avatar>

                                <div>
                                    <v-card-text class="text-h3">{{ user.name }}</v-card-text>
                                    <v-card-subtitle class="text-medium-emphasis">{{ user.email }}</v-card-subtitle>
                                </div>

                                <v-spacer />
                                <v-chip color="success" variant="tonal">Active</v-chip>
                            </v-card-text>

                            <v-divider />

                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="4">
                                        <v-card variant="outlined" rounded="lg" subtitle="Login Provider"
                                            prepend-icon="mdi-cog">
                                            <v-card-text class="bg-surface-light pt-4">
                                                <strong>{{ user.provider }}</strong>
                                            </v-card-text>
                                        </v-card>
                                    </v-col>
                                    <v-col cols="12" md="4">
                                        <v-card variant="outlined" rounded="lg" subtitle="Member Since"
                                            prepend-icon="mdi-calendar">
                                            <v-card-text class="bg-surface-light pt-4">
                                                <strong>{{ user.memberSince }}</strong>
                                            </v-card-text>
                                        </v-card>
                                    </v-col>
                                    <v-col cols="12" md="4">
                                        <v-card variant="outlined" rounded="lg" subtitle="Account Type"
                                            prepend-icon="mdi-account">
                                            <v-card-text class="bg-surface-light pt-4">
                                                <strong>{{ user.accountType }}</strong>
                                            </v-card-text>
                                        </v-card>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                            <v-divider />
                            <v-card-text>
                                <v-btn variant="outlined" color="error" @click="openDeleteModal">Delete my
                                    account</v-btn>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
        </v-main>
    </v-layout>

    <v-dialog v-model="showEditModal" max-width="560">
        <v-card rounded="lg" elevation="2" class="mb-4" color="primary">
            <template v-slot:title>
                <span class="font-weight-black">Edit Profile</span>
            </template>
            <template v-slot:subtitle>
                <span class="font-medium-black">Update display name and profile picture for your SafePath
                    account.</span>
            </template>
            <v-card-text class="bg-surface-light pt-4">
                <v-row>
                    <v-col cols="12" md="4" class="d-flex flex-column align-center ga-3">
                        <v-avatar size="132" rounded="xl" color="primary" variant="tonal">
                            <v-img v-if="profilePreview" :src="profilePreview" alt="Profile image" cover />
                            <span v-else class="text-h4">{{ userInitials }}</span>
                        </v-avatar>

                    </v-col>

                    <v-col cols="12" md="8">
                        <v-text-field v-model="editableProfile.name" label="Display Name"
                            placeholder="Enter your display name" variant="outlined" class="mb-3" />

                        <v-text-field v-model="editableProfile.email" label="Email Address" variant="outlined"
                            class="mb-2" disabled
                            hint="Email is managed by your sign-in provider and cannot be changed here."
                            persistent-hint />

                        <v-file-input accept="image/*" label="Change picture" density="comfortable" variant="outlined"
                            prepend-icon="mdi-camera" @change="handleProfileImageChange" />

                        <v-btn v-if="profilePreview" color="error" variant="text" @click="removeProfileImage">
                            Remove picture
                        </v-btn>

                        <v-card-actions>
                            <v-spacer />
                            <v-btn variant="text" @click="closeEditModal">Cancel</v-btn>
                            <v-btn color="primary" @click="saveProfile">Save Profile</v-btn>
                        </v-card-actions>

                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </v-dialog>

    <v-dialog v-model="showDeleteModal" max-width="500">
        <v-card rounded="lg" color="error">
            <template v-slot:title>
                <span class="font-weight-black">Delete account?</span>
            </template>
            <v-card-text class="bg-surface-light pt-4">
                <p class="text-emphasis mb-3">Permanently delete your SafePath account.
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
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import SafePathNavDrawer from '../components/SafePathNavDrawer.vue';

const router = useRouter();

const showDeleteModal = ref(false);
const deleteConfirmText = ref('');
const profilePreview = ref('');
const showEditModal = ref(false);

const user = ref({
    name: 'SafePath User',
    email: 'user@example.com',
    provider: 'Google',
    memberSince: 'June 2026',
    accountType: 'Standard'
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

const handleProfileImageChange = (event) => {
    const file = Array.isArray(event) ? event[0] : event?.target?.files?.[0];

    if (!file) {
        return;
    }

    profilePreview.value = URL.createObjectURL(file);
};

const removeProfileImage = () => {
    profilePreview.value = '';
};

const saveProfile = () => {
    user.value.name = editableProfile.value.name;

    console.log('Profile saved:', {
        name: editableProfile.value.name,
        profileImage: profilePreview.value
    });

    closeEditModal();
};

const openEditModal = () => {
    showEditModal.value = true;
};

const closeEditModal = () => {
    showEditModal.value = false;
};


const logout = () => {
    console.log('Logout user');
    router.push('/login');
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

const deleteAccount = () => {
    if (deleteConfirmText.value !== 'DELETE') {
        return;
    }

    console.log('Delete account requested');

    closeDeleteModal();
    router.push('/login');
};
</script>

<style scoped>
.app-shell {
    min-height: 100vh;
}
</style>