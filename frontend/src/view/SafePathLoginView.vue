<template>
  <main class="login-page">
    <section class="login-card">
      <aside class="brand-panel">
        <div class="brand-header">
          <img class="brand-logo" :src="safepathLogo" alt="SafePath Berlin logo" />
          <div>
            <h1>SafePath</h1>
            <p>Berlin</p>
          </div>
        </div>

        <h2>Your trusted companion<br />for safe routes</h2>

        <div class="feature-list">
          <div class="feature-item">
            <span class="feature-icon">🛡️</span>
            <div>
              <h3>Safe Routes</h3>
              <p>Find the safest routes in real-time</p>
            </div>
          </div>

          <div class="feature-item">
            <span class="feature-icon">🔔</span>
            <div>
              <h3>Smart Alerts</h3>
              <p>Get notified about risks & incidents</p>
            </div>
          </div>
        </div>
      </aside>

      <section class="form-panel">
        <div class="form-content">
          <div class="form-heading">
            <h2>Welcome Back</h2>
            <p>Login to continue to your account</p>
          </div>

          <form @submit.prevent="handleLogin" class="login-form">
            <label>Email *</label>
            <input v-model="email" type="email" placeholder="Enter your email" />

            <label>Password *</label>
            <input v-model="password" type="password" placeholder="Enter your password" />

            <button class="login-btn" type="submit">LOGIN</button>
            <p class="register-link">
              Don’t have an account?
              <button type="button" @click="goToRegister">Click to register</button>
            </p>
          </form>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import safepathLogo from '../assets/Berlin.png'

const email = ref('')
const password = ref('')
const router = useRouter()

const handleLogin = () => {
  console.log(email.value, password.value)
}
const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eef2ff, #eff6ff);
  font-family: 'DM Sans', Inter, sans-serif;
}

.login-card {
  width: 1100px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: white;
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
  width: 74px;
  height: 74px;
  object-fit: cover;
  border-radius: 18px;
  border: 1px solid #e8e8ec;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.18);
}

.brand-header h1 {
  margin: 0;
  color: #0a0a0a;
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
  border-radius: 14px;
  background: rgba(99, 102, 241, 0.12);
}

.feature-item h3 {
  margin: 0 0 4px;
  color: #111827;
}

.feature-item p {
  margin: 0;
  color: #4b5563;
}

.form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 50px;
}

.form-content {
  width: 100%;
  max-width: 420px;
}

.form-heading h2 {
  margin: 0;
  font-size: 30px;
  color: #111827;
}

.form-heading p {
  margin: 8px 0 32px;
  color: #6b7280;
}

.login-form {
  display: grid;
  gap: 18px;
}

.login-form label {
  font-weight: 700;
  color: #111827;
}

.login-form input {
  height: 55px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  font: inherit;
}

.login-form input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.login-btn {
  height: 55px;
  border: 0;
  border-radius: 8px;
  background: #6366f1;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: 160ms ease;
}

.login-btn:hover {
  background: #4f46e5;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
  transform: translateY(-1px);
}
.register-link {
  margin: 4px 0 0;
  text-align: center;
  color: #6b7280;
  font-size: 14px;
}

.register-link button {
  border: 0;
  background: transparent;
  color: #6366f1;
  font-weight: 700;
  cursor: pointer;
  padding: 0;
}

.register-link button:hover {
  color: #4f46e5;
  text-decoration: underline;
}
</style>
