<template>
  <main class="register-page">
    <section class="register-card">
      <aside class="left-panel">
        <h1>SafePath Berlin</h1>
        <p>Create your safer journey today.</p>
      </aside>

      <section class="right-panel">
        <div class="register-content">
          <h2>Create Account</h2>

          <form class="register-form" @submit.prevent="handleRegister">
            <input v-model="name" type="text" placeholder="Full Name" />
            <input v-model="email" type="email" placeholder="Email Address" />
            <input v-model="password" type="password" placeholder="Password" />

            <button type="submit">CREATE ACCOUNT</button>
          </form>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'

const name = ref('')
const email = ref('')
const password = ref('')

const handleRegister = () => {
  console.log(name.value, email.value, password.value)
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0fff4, #eff6ff);
  font-family: Inter, sans-serif;
}

.register-card {
  width: 1100px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 15px 40px rgba(0,0,0,0.12);
}

.left-panel {
  padding: 50px;
  background: linear-gradient(180deg, #d8ffe5, #8be0a7);
}

.right-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 50px;
}

.register-content {
  width: 100%;
  max-width: 420px;
}

.register-form {
  display: grid;
  gap: 18px;
}

.register-form input {
  height: 55px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
}

.register-form button {
  height: 55px;
  border: 0;
  border-radius: 8px;
  background: #00a63e;
  color: white;
  font-weight: bold;
  cursor: pointer;
}
</style>
