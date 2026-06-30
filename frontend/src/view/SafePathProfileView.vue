<template>
    <v-layout class="app-shell">
        <SafePathNavDrawer />

        <v-main>
            <v-container fluid class="pa-4 pa-md-6">
                <v-card class="mb-4" rounded="lg" elevation="2">
                    <v-card-text class="d-flex justify-space-between align-center flex-wrap ga-3">
                        <div>
                            <h2 class="text-h5 text-md-h4">Profile Settings</h2>
                            <p class="text-medium-emphasis mt-2">Manage account details, image, and privacy-sensitive
                                actions.
                            </p>
                        </div>
                        <v-btn variant="tonal" color="primary" @click="logout">Logout</v-btn>
                    </v-card-text>
                </v-card>

                <v-row>
                    <v-col cols="12">
                        <v-card rounded="lg" elevation="2" class="mb-4">
                            <v-card-text class="d-flex align-center flex-wrap ga-4">
                                <v-avatar size="76" rounded="xl" color="primary" variant="tonal">
                                    <v-img v-if="profilePreview" :src="profilePreview" alt="Profile preview" cover />
                                    <span v-else class="text-h6">{{ userInitials }}</span>
                                </v-avatar>

                                <div>
                                    <p class="text-overline text-medium-emphasis">Account Overview</p>
                                    <h3 class="text-h5">{{ user.name }}</h3>
                                    <p class="text-body-2 text-medium-emphasis">{{ user.email }}</p>
                                </div>

                                <v-spacer />
                                <v-chip color="success" variant="tonal">Active</v-chip>
                            </v-card-text>

                            <v-divider />

                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="4">
                                        <v-card variant="outlined" rounded="lg">
                                            <v-card-text>
                                                <p class="text-caption text-medium-emphasis">Login Provider</p>
                                                <strong>{{ user.provider }}</strong>
                                            </v-card-text>
                                        </v-card>
                                    </v-col>
                                    <v-col cols="12" md="4">
                                        <v-card variant="outlined" rounded="lg">
                                            <v-card-text>
                                                <p class="text-caption text-medium-emphasis">Member Since</p>
                                                <strong>{{ user.memberSince }}</strong>
                                            </v-card-text>
                                        </v-card>
                                    </v-col>
                                    <v-col cols="12" md="4">
                                        <v-card variant="outlined" rounded="lg">
                                            <v-card-text>
                                                <p class="text-caption text-medium-emphasis">Account Type</p>
                                                <strong>{{ user.accountType }}</strong>
                                            </v-card-text>
                                        </v-card>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-col>

                    <v-col cols="12" lg="8">
                        <v-card rounded="lg" elevation="2" class="mb-4">
                            <v-card-title>Edit Profile</v-card-title>
                            <v-card-subtitle>Update display name and profile picture for your SafePath
                                account.</v-card-subtitle>
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="4" class="d-flex flex-column align-center ga-3">
                                        <v-avatar size="132" rounded="xl" color="primary" variant="tonal">
                                            <v-img v-if="profilePreview" :src="profilePreview" alt="Profile image"
                                                cover />
                                            <span v-else class="text-h4">{{ userInitials }}</span>
                                        </v-avatar>

                                        <v-file-input accept="image/*" label="Change picture" density="comfortable"
                                            variant="outlined" prepend-icon="mdi-camera"
                                            @change="handleProfileImageChange" />

                                        <v-btn v-if="profilePreview" color="error" variant="text"
                                            @click="removeProfileImage">
                                            Remove picture
                                        </v-btn>
                                    </v-col>

                                    <v-col cols="12" md="8">
                                        <v-text-field v-model="editableProfile.name" label="Display Name"
                                            placeholder="Enter your display name" variant="outlined" class="mb-3" />

                                        <v-text-field v-model="editableProfile.email" label="Email Address"
                                            variant="outlined" class="mb-2" disabled />

                                        <p class="text-caption text-medium-emphasis mb-4">
                                            Email is managed by your sign-in provider and cannot be changed here.
                                        </p>

                                        <v-btn color="primary" @click="saveProfile">Save Profile</v-btn>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card rounded="lg" elevation="2" class="mb-4">
                            <v-card-title>Privacy Notice</v-card-title>
                            <v-card-text class="text-medium-emphasis">
                                SafePath Berlin uses account information only for login, profile settings, route
                                features, and
                                safety preferences.
                            </v-card-text>
                        </v-card>

                        <v-card rounded="lg" elevation="2" border color="error" variant="outlined">
                            <v-card-title class="text-error">Danger Zone</v-card-title>
                            <v-card-text class="d-flex justify-space-between align-center flex-wrap ga-3">
                                <p class="text-medium-emphasis mb-0">
                                    Permanently delete your account. This action cannot be undone.
                                </p>
                                <v-btn color="error" @click="openDeleteModal">Delete my account</v-btn>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
        </v-main>
    </v-layout>

    <v-dialog v-model="showDeleteModal" max-width="480">
        <v-card rounded="lg">
            <v-card-title>Delete account?</v-card-title>
            <v-card-text>
                <p class="text-medium-emphasis mb-3">This action cannot be undone. Type DELETE to confirm.</p>
                <v-text-field v-model="deleteConfirmText" label="Type DELETE" variant="outlined"
                    density="comfortable" />
            </v-card-text>
            <v-card-actions>
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