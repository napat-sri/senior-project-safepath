<template>
  <main class="login-page">
    <section class="login-card">
      <aside class="brand-panel">
        <div class="brand-header">
          <div class="shield-logo">✓</div>
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
          </form>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'

const email = ref('')
const password = ref('')

const handleLogin = () => {
  console.log(email.value, password.value)
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #effdf5, #eff6ff);
  font-family: Inter, sans-serif;
}

.login-card {
  width: 1100px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 15px 40px rgba(0,0,0,0.12);
}

.brand-panel {
  padding: 50px;
  background: linear-gradient(180deg, #d8ffe5, #8be0a7);
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.shield-logo {
  width: 70px;
  height: 70px;
  display: grid;
  place-items: center;
  background: white;
  border-radius: 18px;
  font-size: 32px;
  font-weight: bold;
  color: #00a63e;
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

.login-form {
  display: grid;
  gap: 18px;
}

.login-form input {
  height: 55px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
}

.login-btn {
  height: 55px;
  border: 0;
  border-radius: 8px;
  background: #00a63e;
  color: white;
  font-weight: bold;
  cursor: pointer;
}
</style>
