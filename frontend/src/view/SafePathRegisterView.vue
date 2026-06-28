<template>
  <main class="register-page">
    <section class="register-card">
      <aside class="brand-panel">
        <div class="brand-header">
          <img class="brand-logo" :src="safePathLogo" alt="SafePath Berlin logo" />

          <div>
            <h1>SafePath</h1>
            <p>Berlin</p>
          </div>
        </div>

        <h2>Create your safer journey<br />with trusted access</h2>

        <div class="feature-list">
          <div class="feature-item">
            <span class="feature-icon">🔐</span>
            <div>
              <h3>Secure Sign Up</h3>
              <p>Register with your preferred trusted account provider.</p>
            </div>
          </div>

          <div class="feature-item">
            <span class="feature-icon">🛡️</span>
            <div>
              <h3>Protected Account</h3>
              <p>Your SafePath profile helps protect your route and safety preferences.</p>
            </div>
          </div>

          <div class="feature-item">
            <span class="feature-icon">📍</span>
            <div>
              <h3>Personalized Safety</h3>
              <p>Access safer routes, incident reports, and community safety features.</p>
            </div>
          </div>
        </div>
      </aside>

      <section class="form-panel">
        <div class="register-content">
          <div class="form-heading">
            <h2>Create Account</h2>
            <p>Choose how you would like to register with SafePath Berlin.</p>
          </div>

          <div class="provider-list">
            <button
              v-for="provider in primaryProviders"
              :key="provider.key"
              type="button"
              class="provider-btn"
              @click="registerWithProvider(provider.key)"
            >
              <span class="provider-icon">{{ provider.icon }}</span>
              {{ provider.label }}
            </button>
          </div>

          <button
            type="button"
            class="more-options-btn"
            @click="showMoreOptions = !showMoreOptions"
          >
            {{ showMoreOptions ? 'Hide more options' : 'Show more options' }}
          </button>

          <div v-if="showMoreOptions" class="provider-list secondary-provider-list">
            <button
              v-for="provider in secondaryProviders"
              :key="provider.key"
              type="button"
              class="provider-btn"
              :class="{ 'primary-provider': provider.key === 'email' }"
              @click="registerWithProvider(provider.key)"
            >
              <span class="provider-icon">{{ provider.icon }}</span>
              {{ provider.label }}
            </button>
          </div>

          <p class="login-link">
            Already have an account?
            <button type="button" @click="goToLogin">Login here</button>
          </p>

          <p class="security-note">
            Your account is protected with secure sign-in and identity verification.
          </p>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import safePathLogo from '../assets/Berlin.png'

const router = useRouter()
const showMoreOptions = ref(false)

const primaryProviders = [
  {
    key: 'google',
    label: 'Continue with Google',
    icon: 'G'
  },
  {
    key: 'facebook',
    label: 'Continue with Facebook',
    icon: 'f'
  },
  {
    key: 'microsoft',
    label: 'Continue with Microsoft',
    icon: 'M'
  }
]

const secondaryProviders = [

  {
    key: 'github',
    label: 'Continue with GitHub',
    icon: 'GH'
  },
  {
    key: 'apple',
    label: 'Continue with Apple',
    icon: ''
  },
  {
    key: 'email',
    label: 'Continue with Email',
    icon: '✉️'
  }
]

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
}

const registerWithProvider = (provider) => {
  window.location.href = providerUrls[provider]
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background: linear-gradient(135deg, #eef2ff, #eff6ff);
  font-family: 'DM Sans', Inter, sans-serif;
}

.register-card {
  width: 1100px;
  min-height: 680px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
}

.brand-panel {
  padding: 50px;
  background: linear-gradient(180deg, #eef2ff, #c7d2fe);
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.brand-logo {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 20px;
  border: 1px solid #e8e8ec;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.18);
}

.brand-header h1 {
  margin: 0;
  color: #0a0a0a;
  font-size: 32px;
  letter-spacing: -0.03em;
}

.brand-header p {
  margin: 4px 0 0;
  color: #6366f1;
  font-weight: 700;
}

.brand-panel h2 {
  margin-top: 70px;
  font-size: 34px;
  line-height: 1.2;
  color: #111827;
  letter-spacing: -0.03em;
}

.feature-list {
  margin-top: 42px;
  display: grid;
  gap: 22px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-icon {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border-radius: 14px;
  background: rgba(99, 102, 241, 0.12);
}

.feature-item h3 {
  margin: 0 0 4px;
  color: #111827;
  font-size: 17px;
}

.feature-item p {
  margin: 0;
  color: #4b5563;
  line-height: 1.45;
}

.form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 50px;
}

.register-content {
  width: 100%;
  max-width: 420px;
}

.form-heading h2 {
  margin: 0;
  font-size: 32px;
  color: #111827;
  letter-spacing: -0.03em;
}

.form-heading p {
  margin: 10px 0 32px;
  color: #6b7280;
  line-height: 1.5;
}

.provider-list {
  display: grid;
  gap: 14px;
}

.secondary-provider-list {
  margin-top: 14px;
}

.provider-btn {
  width: 100%;
  min-height: 54px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  border: 1px solid #e8e8ec;
  border-radius: 10px;
  background: #ffffff;
  color: #111827;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  transition: 160ms ease;
}

.provider-btn:hover {
  border-color: #6366f1;
  background: #f8faff;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
  transform: translateY(-1px);
}

.provider-icon {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border-radius: 999px;
  background: #eef2ff;
  color: #6366f1;
  font-weight: 800;
  font-size: 14px;
}

.primary-provider {
  background: #6366f1;
  color: #ffffff;
  border-color: #6366f1;
}

.primary-provider .provider-icon {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.primary-provider:hover {
  background: #4f46e5;
  border-color: #4f46e5;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.more-options-btn {
  width: 100%;
  margin-top: 14px;
  border: 0;
  background: transparent;
  color: #6366f1;
  font-weight: 700;
  cursor: pointer;
  padding: 10px;
}

.more-options-btn:hover {
  color: #4f46e5;
  text-decoration: underline;
}

.login-link {
  margin: 22px 0 0;
  text-align: center;
  color: #6b7280;
}

.login-link button {
  border: 0;
  background: transparent;
  color: #6366f1;
  font-weight: 700;
  cursor: pointer;
}

.login-link button:hover {
  color: #4f46e5;
  text-decoration: underline;
}

.security-note {
  margin-top: 28px;
  padding: 14px;
  border-radius: 10px;
  background: #eef2ff;
  color: #4b5563;
  font-size: 14px;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .register-card {
    grid-template-columns: 1fr;
  }

  .brand-panel {
    padding: 36px;
  }

  .brand-panel h2 {
    margin-top: 42px;
    font-size: 28px;
  }

  .form-panel {
    padding: 36px;
  }
}

@media (max-width: 520px) {
  .register-page {
    padding: 18px;
  }

  .brand-header {
    align-items: flex-start;
  }

  .brand-logo {
    width: 120px;
    height: 120px;
  }
}
</style>