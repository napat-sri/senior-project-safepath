<template>
    <v-container fluid class="auth-page pa-4 pa-md-8">
        <v-row class="fill-height" align="center" justify="center">
            <v-col cols="12" lg="10" xl="9">
                <v-card elevation="10" rounded="xl" class="overflow-hidden">
                    <v-row no-gutters>
                        <v-col cols="12" md="6" class="brand-panel pa-8 pa-md-12">
                            <v-sheet color="transparent" class="d-flex align-center ga-4 mb-8">
                                <v-avatar size="80" rounded="lg">
                                    <v-img :src="safePathLogo" alt="SafePath Berlin logo" cover />
                                </v-avatar>
                                <div>
                                    <h1 class="text-h4 text-high-emphasis">SafePath</h1>
                                    <p class="text-primary text-subtitle-1 font-weight-bold">Berlin</p>
                                </div>
                            </v-sheet>

                            <h2 class="text-h4 text-md-h3 mb-8">Create your safer journey with trusted access</h2>

                            <v-list bg-color="transparent" density="comfortable" class="pa-0">
                                <v-list-item>
                                    <template #prepend>
                                        <v-avatar color="primary" variant="tonal" size="36">L</v-avatar>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">Secure Sign Up</v-list-item-title>
                                    <v-list-item-subtitle>Register with your preferred trusted account
                                        provider.</v-list-item-subtitle>
                                </v-list-item>
                                <v-list-item>
                                    <template #prepend>
                                        <v-avatar color="success" variant="tonal" size="36">P</v-avatar>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">Protected Account</v-list-item-title>
                                    <v-list-item-subtitle>Your account helps protect your route and safety
                                        preferences.</v-list-item-subtitle>
                                </v-list-item>
                                <v-list-item>
                                    <template #prepend>
                                        <v-avatar color="info" variant="tonal" size="36">R</v-avatar>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">Personalized Safety</v-list-item-title>
                                    <v-list-item-subtitle>Access safer routes, reports, and community safety
                                        features.</v-list-item-subtitle>
                                </v-list-item>
                            </v-list>
                        </v-col>

                        <v-col cols="12" md="6" class="pa-8 pa-md-12 d-flex align-center">
                            <v-sheet width="100%" max-width="460" class="mx-auto" color="transparent">
                                <h2 class="text-h4 mb-2">Create Account</h2>
                                <p class="text-medium-emphasis mb-8">Choose how you would like to register with SafePath
                                    Berlin.</p>

                                <div class="d-grid ga-3">
                                    <v-btn v-for="provider in primaryProviders" :key="provider.key" block size="large"
                                        variant="outlined" @click="registerWithProvider(provider.key)">
                                        <span class="mr-2">{{ provider.icon }}</span>
                                        {{ provider.label }}
                                    </v-btn>
                                </div>

                                <v-btn class="mt-4" block variant="text" color="primary"
                                    @click="showMoreOptions = !showMoreOptions">
                                    {{ showMoreOptions ? 'Hide more options' : 'Show more options' }}
                                </v-btn>

                                <v-expand-transition>
                                    <div v-show="showMoreOptions" class="mt-3 d-grid ga-3">
                                        <v-btn v-for="provider in secondaryProviders" :key="provider.key" block
                                            size="large" :variant="provider.key === 'email' ? 'flat' : 'outlined'"
                                            :color="provider.key === 'email' ? 'primary' : undefined"
                                            @click="registerWithProvider(provider.key)">
                                            <span class="mr-2">{{ provider.icon || 'A' }}</span>
                                            {{ provider.label }}
                                        </v-btn>
                                    </div>
                                </v-expand-transition>

                                <p class="text-center mt-6 text-medium-emphasis">
                                    Already have an account?
                                    <v-btn variant="text" color="primary" @click="goToLogin">Login here</v-btn>
                                </p>

                                <v-alert class="mt-4" type="info" variant="tonal" density="comfortable">
                                    Your account is protected with secure sign-in and identity verification.
                                </v-alert>
                            </v-sheet>
                        </v-col>
                    </v-row>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import safePathLogo from '../assets/Berlin.png';

const router = useRouter();
const showMoreOptions = ref(false);

const primaryProviders = [
    {
        key: 'google',
        label: 'Continue with Google',
        icon: 'G'
    },
    {
        key: 'facebook',
        label: 'Continue with Facebook',
        icon: 'F'
    },
    {
        key: 'microsoft',
        label: 'Continue with Microsoft',
        icon: 'M'
    }
];

const secondaryProviders = [
    {
        key: 'github',
        label: 'Continue with GitHub',
        icon: 'GH'
    },
    {
        key: 'apple',
        label: 'Continue with Apple',
        icon: 'A'
    },
    {
        key: 'email',
        label: 'Continue with Email',
        icon: 'E'
    }
];

const providerUrls = {
    google:
        process.env.VUE_APP_REGISTER_GOOGLE_URL ||
        'http://localhost:8080/realms/safepath/broker/google/login?client_id=safepath-frontend&redirect_uri=http://localhost:5173/home',

    facebook:
        process.env.VUE_APP_REGISTER_FACEBOOK_URL ||
        'http://localhost:8080/realms/safepath/broker/facebook/login?client_id=safepath-frontend&redirect_uri=http://localhost:5173/home',

    apple:
        process.env.VUE_APP_REGISTER_APPLE_URL ||
        'http://localhost:8080/realms/safepath/broker/apple/login?client_id=safepath-frontend&redirect_uri=http://localhost:5173/home',

    microsoft:
        process.env.VUE_APP_REGISTER_MICROSOFT_URL ||
        'http://localhost:8080/realms/safepath/broker/microsoft/login?client_id=safepath-frontend&redirect_uri=http://localhost:5173/home',

    github:
        process.env.VUE_APP_REGISTER_GITHUB_URL ||
        'http://localhost:8080/realms/safepath/broker/github/login?client_id=safepath-frontend&redirect_uri=http://localhost:5173/home',

    email:
        process.env.VUE_APP_REGISTER_EMAIL_URL ||
        'http://localhost:8080/realms/safepath/protocol/openid-connect/registrations?client_id=safepath-frontend&response_type=code&scope=openid&redirect_uri=http://localhost:5173/home'
};

const registerWithProvider = (provider) => {
    window.location.href = providerUrls[provider];
};

const goToLogin = () => {
    router.push('/login');
};
</script>

<style scoped>
.auth-page {
    min-height: 100vh;
}

/* Auth backdrops follow the active theme. */
.v-theme--safepathLight .auth-page {
    background: linear-gradient(135deg, #eef2ff, #eff6ff);
}

.v-theme--safepathDark .auth-page {
    background: linear-gradient(135deg, #121212, #1a1a1a);
}

.v-theme--safepathLight .brand-panel {
    background: linear-gradient(180deg, #eef2ff, #c7d2fe);
}

.v-theme--safepathDark .brand-panel {
    background: linear-gradient(160deg, #16252b, #0c1a1f);
}
</style>