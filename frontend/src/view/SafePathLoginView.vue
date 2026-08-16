<template>
    <v-container fluid class="auth-page pa-4 pa-md-8">
        <v-row class="fill-height align-center justify-center">
            <v-col cols="12" lg="10" xl="9">
                <v-card elevation="10" rounded="xl" class="overflow-hidden">
                    <v-row no-gutters>
                        <v-col cols="12" md="6" class="brand-panel pa-4 pa-md-6">
                            <v-card rounded="xl" height="475" :image="brandenburg" class="brand-hero">
                                <v-sheet color="transparent" class="d-flex align-center ga-4 mt-2 ml-4">
                                    <v-avatar size="36" rounded="lg">
                                        <v-img :src="safepathLogo" alt="SafePath Berlin logo" cover />
                                    </v-avatar>
                                    <h3 class="text-h4 brand-panel-title">SafePath Berlin</h3>
                                </v-sheet>

                                <v-spacer class="mx-4 mb-16 pb-16"></v-spacer>
                                <v-spacer class="mx-4 mb-16 pb-16"></v-spacer>
                                <v-spacer class="mx-4 mb-4 pb-4"></v-spacer>

                                <v-card class="mx-2 feature-card" variant="tonal" theme="dark">
                                    <v-list bg-color="transparent" density="comfortable" class="pa-0">
                                        <v-list-item>
                                            <template #prepend>
                                                <v-avatar color="primary">
                                                    <v-icon icon="mdi-magnify"></v-icon>
                                                </v-avatar>
                                            </template>
                                            <v-list-item-title class="font-weight-bold">Safe Routes</v-list-item-title>
                                            <v-list-item-subtitle>Find the safest routes in
                                                real-time</v-list-item-subtitle>
                                        </v-list-item>
                                        <v-list-item>
                                            <template #prepend>
                                                <v-avatar color="warning">
                                                    <v-icon icon="mdi-robot"></v-icon>
                                                </v-avatar>
                                            </template>
                                            <v-list-item-title class="font-weight-bold">AI Safety
                                                Assistant</v-list-item-title>
                                            <v-list-item-subtitle>Ask SafePath Bot about routes and
                                                risks</v-list-item-subtitle>
                                        </v-list-item>
                                    </v-list>
                                </v-card>
                            </v-card>
                        </v-col>

                        <v-col cols="12" md="6" class="pa-8 pa-md-10 d-flex align-center">
                            <v-sheet width="100%" max-width="400" class="mx-auto" color="transparent">
                                <v-card-title class="text-headline-medium font-weight-black">Willkommen!</v-card-title>
                                <v-card-subtitle class="text-body-large font-weight-medium">Login to continue to your
                                    account</v-card-subtitle>

                                <v-form @submit.prevent="handleLogin">
                                    <v-btn color="primary" block rounded="lg" @click="Login" class="mt-10 mb-4">Login
                                        with Email</v-btn>

                                    <v-divider>or</v-divider>

                                    <div class="d-grid mt-4 mb-4">
                                        <v-btn v-for="provider in primaryProviders" :key="provider.key" block
                                            variant="outlined" @click="registerWithProvider(provider.key)" rounded="lg">
                                            <v-icon class="mr-2">{{ provider.icon }}</v-icon>
                                            {{ provider.label }}
                                        </v-btn>
                                    </div>

                                    <p class="text-center text-medium-emphasis">
                                        Don't have an account?
                                        <v-btn variant="text" color="primary" @click="goToRegister">Click to
                                            register</v-btn>
                                    </p>
                                </v-form>
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
import safepathLogo from '../assets/Berlin.png';
import brandenburg from '../assets/Photographing+Brandenburg+Gate_019.webp';
import keycloak from '../services/keycloak';

const router = useRouter();

const primaryProviders = [
    {
        key: 'google',
        label: 'Continue with Google',
        icon: 'mdi-google'
    }
];

// Redirect to Keycloak's hosted login; returns to /home once authenticated.
const Login = () => keycloak.login({ redirectUri: window.location.origin + '/home' });
const handleLogin = Login;                       // Enter-to-submit also works

// Social provider (Google) → jump straight to that IdP.
const registerWithProvider = (providerKey) =>
    keycloak.login({ idpHint: providerKey, redirectUri: window.location.origin + '/home' });

// "Register" → Keycloak's hosted registration page.
const goToRegister = () => keycloak.register({ redirectUri: window.location.origin + '/home' });</script>

<style scoped>
.auth-page {
    height: 100vh;
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

.brand-panel-title {
    color: #ffffff;
}

/* Or a gradient scrim instead of a filter: */
.brand-hero::after {
    content: '';
    position: absolute;
    inset: 0;
    pointer-events: none;
    border-radius: inherit;
}

.brand-hero {
    position: relative;
}

.feature-card {
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: #ffffff !important;
}
</style>