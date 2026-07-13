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
                                    <h1 class="text-h4 text-high-emphasis">SafePath Berlin</h1>
                                </div>
                            </v-sheet>

                            <h2 class="text-h4 text-md-h3 mb-8">Create your safer journey with trusted access</h2>

                            <v-list bg-color="transparent" density="comfortable" class="pa-0">
                                <v-list-item>
                                    <template #prepend>
                                        <v-avatar color="primary" variant="tonal">
                                            <v-icon icon="mdi-lock"></v-icon>
                                        </v-avatar>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">Secure Sign Up</v-list-item-title>
                                    <v-list-item-subtitle>Register with your preferred trusted account
                                        provider.</v-list-item-subtitle>
                                </v-list-item>
                                <v-list-item>
                                    <template #prepend>
                                        <v-avatar color="success" variant="tonal">
                                            <v-icon icon="mdi-security"></v-icon>
                                        </v-avatar>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">Protected Account</v-list-item-title>
                                    <v-list-item-subtitle>Your account helps protect your route and safety
                                        preferences.</v-list-item-subtitle>
                                </v-list-item>
                                <v-list-item>
                                    <template #prepend>
                                        <v-avatar color="info" variant="tonal">
                                            <v-icon icon="mdi-account"></v-icon>
                                        </v-avatar>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">Personalized Safety</v-list-item-title>
                                    <v-list-item-subtitle>Access safer routes, reports, and community safety
                                        features.</v-list-item-subtitle>
                                </v-list-item>
                            </v-list>
                        </v-col>

                        <v-col cols="12" md="6" class="pa-6 pa-md-6 d-flex align-center">
                            <v-sheet width="100%" max-width="375" class="mx-auto" color="transparent">
                                <v-card-title class="text-headline-medium font-weight-black">Create Your
                                    Account</v-card-title>
                                <v-card-subtitle class="text-body-large font-weight-medium">Join SafePath
                                    Berlin</v-card-subtitle>

                                <v-form ref="form">
                                    <v-text-field v-model="name" label="Name" placeholder="Enter your name"
                                        variant="outlined" density="compact" class="mt-3 my-0" required />

                                    <v-text-field v-model="email" type="email" label="Email"
                                        placeholder="Enter your email" variant="outlined" density="compact" class="my-0"
                                        required />

                                    <v-text-field v-model="password" type="password" label="Password"
                                        placeholder="Enter your password" variant="outlined" density="compact"
                                        class="my-0" required />

                                    <v-btn color="info" block type="submit" class="mt-1 mb-3">Create
                                        account</v-btn>
                                </v-form>

                                <v-divider>or</v-divider>

                                <div class="d-grid mt-3">
                                    <v-btn v-for="provider in primaryProviders" :key="provider.key" block
                                        variant="outlined" @click="registerWithProvider(provider.key)">
                                        <v-icon class="mr-2">{{ provider.icon }}</v-icon>
                                        {{ provider.label }}
                                    </v-btn>
                                </div>

                                <p class="text-center mt-4 text-medium-emphasis">
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
        label: 'Sign in with Google',
        icon: 'mdi-google'
    }
];

const secondaryProviders = [
    {
        key: 'facebook',
        label: 'Continue with Facebook',
        icon: 'F'
    },
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
    },
    {
        key: 'microsoft',
        label: 'Continue with Microsoft',
        icon: 'mdi-email'
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