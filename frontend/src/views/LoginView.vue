<template>
  <div class="login-page">
    <div class="background-effects">
      <div class="circuit-lines"></div>
      <div class="digital-rain"></div>
    </div>

    <div class="login-container">
      <div class="logo-section">
        <h1 class="logo">
          <span class="dragon">龍</span>
          ДОСТУП
        </h1>
        <div class="tech-line"></div>
      </div>

      <div class="cyber-card">
        <div class="card-glow"></div>
        <h2 class="card-title">
          <span class="bracket">&lt;</span>
          АВТОРИЗАЦИЯ
          <span class="bracket">/&gt;</span>
        </h2>

        <form @submit.prevent="handleLogin" class="cyber-form">
          <div v-if="infoMessage" class="info-alert">
            <span class="alert-icon">ℹ</span>
            {{ infoMessage }}
          </div>

          <div v-if="error" class="error-alert">
            <span class="alert-icon">⚠</span>
            {{ error }}
          </div>

          <!-- Demo User Quick Fill -->
          <div class="demo-users-section">
            <div class="demo-label">DEMO USERS:</div>
            <div class="demo-users-list">
              <button
                type="button"
                @click="fillDemoUser('Li_Mei')"
                class="demo-user-btn"
                :class="{ active: form.username === 'Li_Mei' }"
              >
                <span class="demo-username">Li_Mei</span>
                <span class="demo-bio">👩‍🏫 Teacher</span>
              </button>
              <button
                type="button"
                @click="fillDemoUser('Wang_Wei')"
                class="demo-user-btn"
                :class="{ active: form.username === 'Wang_Wei' }"
              >
                <span class="demo-username">Wang_Wei</span>
                <span class="demo-bio">📚 Student</span>
              </button>
              <button
                type="button"
                @click="fillDemoUser('Chen_Yu')"
                class="demo-user-btn"
                :class="{ active: form.username === 'Chen_Yu' }"
              >
                <span class="demo-username">Chen_Yu</span>
                <span class="demo-bio">🎓 Helper</span>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>ПОЛЬЗОВАТЕЛЬ</label>
            <input
              v-model="form.username"
              type="text"
              required
              placeholder="Введите имя пользователя"
              autocomplete="username"
              class="cyber-input"
            />
          </div>

          <div class="form-group">
            <label>ПАРОЛЬ</label>
            <input
              v-model="form.password"
              type="password"
              required
              placeholder="Введите пароль"
              autocomplete="current-password"
              class="cyber-input"
            />
          </div>

          <button type="submit" :disabled="isLoading" class="submit-btn">
            <span class="btn-text">{{ isLoading ? 'АВТОРИЗАЦИЯ...' : 'ВОЙТИ' }}</span>
            <span class="btn-glitch"></span>
          </button>

          <div class="footer-link">
            Новый пользователь? <router-link to="/register" class="link">Создать аккаунт</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: '',
})

const isLoading = ref(false)
const error = ref('')
const infoMessage = ref('')

onMounted(() => {
  // Check if user was redirected due to expired session
  if (route.query.session_expired === 'true') {
    infoMessage.value = 'Ваша сессия истекла. Пожалуйста, войдите снова или зарегистрируйтесь.'
    // Clear the query param to prevent showing message again on reload
    router.replace({ query: {} })
  }
})

async function handleLogin() {
  isLoading.value = true
  error.value = ''

  // Debug logging
  console.log('[Login] Attempting login with:', {
    username: form.value.username,
    passwordLength: form.value.password.length
  })

  try {
    await authStore.login(form.value)
    // Login successful - redirect will happen via router guard
    console.log('[Login] Login successful, redirecting...')
    router.push('/app')
  } catch (err: any) {
    console.error('[Login] Login failed with error:', err)

    // Better error messages
    if (err.response?.status === 401) {
      error.value = 'Неверное имя пользователя или пароль'
    } else if (err.response?.status === 404) {
      error.value = 'Пользователь не найден. Зарегистрируйтесь.'
    } else if (err.code === 'ERR_NETWORK') {
      error.value = 'Ошибка соединения. Проверьте подключение к интернету.'
    } else {
      error.value = err.response?.data?.detail || err.message || 'Вход не удался. Попробуйте снова.'
    }
  } finally {
    isLoading.value = false
  }
}
  } finally {
    isLoading.value = false
  }
}

function fillDemoUser(username: string) {
  form.value.username = username
  form.value.password = 'DemoUser123'
  error.value = ''
  console.log('[Login] Filled demo user:', username)
}
</script>

<style scoped>
.login-page {
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

.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 450px;
  padding: 2rem;
}

.logo-section {
  text-align: center;
  margin-bottom: 3rem;
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
  margin: 0 auto 2rem;
  box-shadow: var(--shadow-cyan);
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

.info-alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(0, 245, 255, 0.1);
  border: 1px solid var(--color-neon-cyan);
  border-radius: var(--radius-md);
  color: var(--color-neon-cyan);
  font-size: 0.9rem;
  margin-bottom: 1rem;
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

.cyber-input {
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 229, 255, 0.3);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: 1rem;
  transition: all 0.3s;
}

.cyber-input:focus {
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

/* Demo Users Section */
.demo-users-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: var(--radius-md);
}

.demo-label {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--color-accent-cyan);
  margin-bottom: 0.75rem;
  text-shadow: 0 0 8px rgba(0, 229, 255, 0.5);
}

.demo-users-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.demo-user-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem 0.5rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s;
}

.demo-user-btn:hover {
  background: rgba(0, 229, 255, 0.1);
  border-color: var(--color-accent-cyan);
  color: var(--color-neon-cyan);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 229, 255, 0.2);
}

.demo-user-btn.active {
  background: rgba(0, 229, 255, 0.15);
  border-color: var(--color-accent-cyan);
  color: #FFFFFF;
  box-shadow:
    0 0 10px rgba(0, 229, 255, 0.3),
    inset 0 0 10px rgba(0, 229, 255, 0.1);
}

.demo-username {
  font-weight: 700;
  font-size: 0.85rem;
  color: #FFFFFF;
}

.demo-bio {
  font-size: 0.7rem;
  opacity: 0.8;
}
</style>
