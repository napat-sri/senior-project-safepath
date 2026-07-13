<template>
    <v-container fluid class="auth-page pa-4 pa-md-8">
        <v-row class="fill-height" align="center" justify="center">
            <v-col cols="12" lg="10" xl="9">
                <v-card elevation="10" rounded="xl" class="overflow-hidden">
                    <v-row no-gutters>
                        <v-col cols="12" md="6" class="brand-panel pa-8 pa-md-12">
                            <v-sheet color="transparent" class="d-flex align-center ga-4 mb-8">
                                <v-avatar size="72" rounded="lg">
                                    <v-img :src="safepathLogo" alt="SafePath Berlin logo" cover />
                                </v-avatar>
                                <div>
                                    <h1 class="text-h4 text-high-emphasis">SafePath Berlin</h1>
                                </div>
                            </v-sheet>

                            <h2 class="text-h4 text-md-h3 mb-8">Your trusted companion for safer routes</h2>

                            <v-list bg-color="transparent" density="comfortable" class="pa-0">
                                <v-list-item>
                                    <template #prepend>
                                        <v-avatar color="primary" variant="tonal">
                                            <v-icon icon="mdi-magnify"></v-icon>
                                        </v-avatar>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">Safe Routes</v-list-item-title>
                                    <v-list-item-subtitle>Find the safest routes in real-time</v-list-item-subtitle>
                                </v-list-item>
                                <v-list-item>
                                    <template #prepend>
                                        <v-avatar color="warning" variant="tonal">
                                            <v-icon icon="mdi-bell-outline"></v-icon>
                                        </v-avatar>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">Smart Alerts</v-list-item-title>
                                    <v-list-item-subtitle>Get notified about risks and incidents</v-list-item-subtitle>
                                </v-list-item>
                            </v-list>
                        </v-col>

                        <v-col cols="12" md="6" class="pa-8 pa-md-10 d-flex align-center">
                            <v-sheet width="100%" max-width="375" class="mx-auto" color="transparent">
                                <v-card-title class="text-headline-medium font-weight-black">Welcome Back</v-card-title>
                                <v-card-subtitle class="text-body-large font-weight-medium">Login to continue to your account</v-card-subtitle>

                                <v-form @submit.prevent="handleLogin">
                                    <v-text-field v-model="email" type="email" label="Email"
                                        placeholder="Enter your email" variant="outlined" density="comfortable"
                                         class="mt-5 my-0" required />

                                    <v-text-field v-model="password" type="password" label="Password"
                                        placeholder="Enter your password" variant="outlined" density="comfortable"
                                        class="my-0" required />

                                    <v-btn color="primary" block type="submit" class="mt-1 mb-4">LOGIN</v-btn>

                                    <v-divider>or</v-divider>

                                <div class="d-grid mt-4">
                                    <v-btn v-for="provider in primaryProviders" :key="provider.key" block
                                        variant="outlined" @click="registerWithProvider(provider.key)">
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

const email = ref('');
const password = ref('');
const router = useRouter();

const primaryProviders = [
    {
        key: 'google',
        label: 'Continue with Google',
        icon: 'mdi-google'
    }
];

const handleLogin = () => {
    console.log(email.value, password.value);
};

const goToRegister = () => {
    router.push('/register');
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