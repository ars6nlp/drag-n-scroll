<template>
  <div class="register-view">
    <div class="background-effects">
      <div class="circuit-lines"></div>
      <div class="digital-rain"></div>
    </div>

    <div class="register-container">
      <div class="logo-section">
        <h1 class="logo">
          <span class="dragon">龍</span>
          ДОСТУП
        </h1>
        <div class="tech-line"></div>
        <p class="subtitle">НАЧНИТЕ СВОЕ ПУТЕШЕСТВИЕ</p>
      </div>

      <div class="cyber-card">
        <div class="card-glow"></div>
        <h2 class="card-title">
          <span class="bracket">&lt;</span>
          РЕГИСТРАЦИЯ
          <span class="bracket">/&gt;</span>
        </h2>

        <form @submit.prevent="handleRegister" class="cyber-form">
          <div v-if="error" class="error-alert">
            <span class="alert-icon">⚠</span>
            {{ error }}
          </div>

          <div v-if="success" class="success-alert">
            <span class="alert-icon">✓</span>
            {{ success }}
          </div>

          <div class="form-group">
            <label>ПОЛЬЗОВАТЕЛЬ</label>
            <input
              v-model="form.username"
              type="text"
              required
              placeholder="Придумайте имя пользователя"
              autocomplete="username"
              class="cyber-input"
            />
          </div>

          <div class="form-group">
            <label>EMAIL</label>
            <input
              v-model="form.email"
              type="email"
              required
              placeholder="Введите ваш email"
              autocomplete="email"
              class="cyber-input"
            />
          </div>

          <div class="form-group">
            <label>ПАРОЛЬ</label>
            <input
              v-model="form.password"
              type="password"
              required
              placeholder="Придумайте пароль"
              autocomplete="new-password"
              class="cyber-input"
            />
          </div>

          <div class="form-group">
            <label>ЯЗЫК ОБУЧЕНИЯ</label>
            <select v-model="form.learning_language" required class="cyber-select">
              <option value="RU">РУССКИЙ</option>
              <option value="KZ">КАЗАХСКИЙ</option>
            </select>
          </div>

          <button type="submit" :disabled="isLoading" class="submit-btn">
            <span class="btn-text">{{ isLoading ? 'РЕГИСТРАЦИЯ...' : 'СОЗДАТЬ АККАУНТ' }}</span>
            <span class="btn-glitch"></span>
          </button>

          <div class="footer-link">
            Уже есть аккаунт?
            <router-link to="/login" class="link">Войти</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { RegisterData } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const form = ref<RegisterData>({
  username: '',
  email: '',
  password: '',
  learning_language: 'RU',
})

const isLoading = ref(false)
const error = ref('')
const success = ref('')

async function handleRegister() {
  isLoading.value = true
  error.value = ''
  success.value = ''

  try {
    await authStore.register(form.value)
    // Registration successful - user is now automatically logged in
    success.value = 'Регистрация успешна! Перенаправление...'
    setTimeout(() => {
      router.push('/app')
    }, 1000)
  } catch (err: any) {
    const errors = err.response?.data
    if (typeof errors === 'object') {
      error.value = Object.values(errors).flat().join('. ')
    } else {
      error.value = err.response?.data?.detail || 'Registration failed. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: var(--color-bg-primary);
}

.background-effects {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  pointer-events: none;
}

.circuit-lines {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(0, 229, 255, 0.05) 1px,
    transparent 1px
  ),
    linear-gradient(90deg, rgba(0, 229, 255, 0.05) 1px,
    transparent 1px
  );
  background-size: 30px 30px;
  animation: circuitPulse 10s ease-in-out infinite;
}

@keyframes circuitPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.digital-rain {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.digital-rain::before,
.digital-rain::after {
  content: '0 1';
  position: absolute;
  top: -50%;
  left: 50%;
  color: var(--color-accent-cyan);
  font-family: monospace;
  font-size: 1rem;
  opacity: 0.3;
  animation: rain 5s linear infinite;
  text-shadow: 0 0 10px var(--color-accent-cyan);
}

.digital-rain::before {
  animation-delay: 0s;
}

.digital-rain::after {
  content: '1 0';
  animation-delay: 2.5s;
}

@keyframes rain {
  0% { transform: translateY(0); }
  100% { transform: translateY(200vh); }
}

.register-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 450px;
  padding: 2rem;
}

.logo-section {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  font-size: 3rem;
  font-weight: 900;
  margin: 0 0 1rem 0;
  text-transform: uppercase;
  letter-spacing: 8px;
  color: #FFFFFF;
  text-shadow:
    0 0 10px rgba(0, 245, 255, 0.8),
    0 0 20px rgba(0, 245, 255, 0.6),
    0 0 40px rgba(0, 245, 255, 0.4);
}

.logo .dragon {
  color: #FF6B35;
  text-shadow:
    0 0 20px rgba(255, 107, 53, 0.8),
    0 0 40px rgba(255, 107, 53, 0.6);
}

.tech-line {
  width: 120px;
  height: 2px;
  background: var(--gradient-cyber);
  margin: 0 auto 1rem;
  box-shadow: var(--shadow-cyan);
}

.subtitle {
  color: #E0E7FF;
  font-size: 0.9rem;
  letter-spacing: 3px;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.cyber-card {
  background: rgba(17, 19, 24, 0.9);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(0, 229, 255, 0.3);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-card);
}

.card-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: var(--gradient-cyber);
  border-radius: var(--radius-xl);
  z-index: -1;
  opacity: 0.4;
  filter: blur(15px);
}

.card-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin: 0 0 2rem 0;
  font-size: 1.8rem;
  font-weight: 900;
  letter-spacing: 4px;
  color: #FFFFFF;
  text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
}

.card-title .bracket {
  color: #00F5FF;
  font-size: 1.2rem;
  text-shadow: 0 0 15px rgba(0, 245, 255, 0.8);
}

.cyber-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.error-alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255, 46, 46, 0.1);
  border: 1px solid var(--color-accent-red);
  border-radius: var(--radius-md);
  color: var(--color-accent-red);
  font-size: 0.9rem;
}

.success-alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(0, 245, 89, 0.1);
  border: 1px solid #00F559;
  border-radius: var(--radius-md);
  color: #00F559;
  font-size: 0.9rem;
}

.alert-icon {
  font-size: 1.2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 2px;
  color: #00F5FF;
  margin-left: 0.25rem;
  text-shadow: 0 0 8px rgba(0, 245, 255, 0.5);
}

.cyber-input,
.cyber-select {
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 229, 255, 0.3);
  border-radius: var(--radius-md);
  color: #FFFFFF;
  font-size: 1rem;
  transition: all 0.3s;
}

.cyber-select option {
  background: #1a1a2e;
  color: #FFFFFF;
}

.cyber-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2300e5ff'%3E%3Cpath d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  padding-right: 3rem;
}

.cyber-input:focus,
.cyber-select:focus {
  outline: none;
  border-color: var(--color-accent-cyan);
  box-shadow:
    0 0 10px rgba(0, 229, 255, 0.3),
    0 0 20px rgba(0, 229, 255, 0.1),
    inset 0 0 10px rgba(0, 229, 255, 0.1);
}

.cyber-input::placeholder {
  color: #A0A8C0;
}

.submit-btn {
  position: relative;
  background: var(--gradient-cyber);
  border: none;
  border-radius: var(--radius-md);
  padding: 1rem;
  color: var(--color-bg-primary);
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: var(--shadow-cyan);
}

.submit-btn:hover:not(:disabled) {
  box-shadow:
    var(--shadow-cyan),
    0 0 30px rgba(0, 229, 255, 0.5);
  transform: translateY(-2px);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.footer-link {
  text-align: center;
  font-size: 0.9rem;
  color: #B0B8C8;
  margin-top: 1rem;
}

.footer-link .link {
  color: #00F5FF;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
}

.footer-link .link:hover {
  text-shadow: 0 0 15px rgba(0, 245, 255, 0.8);
  color: #FFFFFF;
}
</style>
