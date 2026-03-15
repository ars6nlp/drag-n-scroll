<template>
  <div class="learn-view">
    <div class="bg-effects">
      <div class="grid-overlay"></div>
      <div class="ambient-glow"></div>
      <div class="floating-orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && authStore.isAuthenticated" class="loading">
      <div class="warm-loader"></div>
      <div class="loading-text">ЗАГРУЗКА...</div>
    </div>

    <!-- Main Content -->
    <div v-else class="content">
      <!-- Empty Course Warning -->
      <div v-if="authStore.isAuthenticated && isEmptyCourse" class="empty-course-warning">
        <div class="warning-content">
          <p class="warning-title">📚 Курс пустой</p>
          <p class="warning-text">Нажмите кнопку ниже, чтобы добавить демо-уроки</p>
          <button @click="initializeDemo" class="init-btn" :disabled="isInitializing">
            {{ isInitializing ? 'СОЗДАНИЕ...' : 'СОЗДАТЬ ДЕМО-КУРС' }}
          </button>
          <p v-if="initError" class="error-message">{{ initError }}</p>
        </div>
      </div>

      <!-- Auth Warning for non-authenticated users -->
      <div v-if="!authStore.isAuthenticated" class="auth-warning">
        <p class="warning-text">⚠️ Войдите в аккаунт для сохранения прогресса</p>
      </div>

      <!-- Header -->
      <div class="header" v-if="!isEmptyCourse">
        <div class="day-info">
          <div class="hsk-selector">
            <button @click="changeHSKLevel(-1)" class="hsk-nav-btn" :disabled="currentHSKLevel <= 1">−</button>
            <div class="hsk-badge">HSK {{ currentHSKLevel }}</div>
            <button @click="changeHSKLevel(1)" class="hsk-nav-btn" :disabled="currentHSKLevel >= 6">+</button>
          </div>
          <div class="day-selector">
            <button @click="changeDay(-1)" class="day-nav-btn" :disabled="currentDay <= 1">←</button>
            <div class="day-number">ДЕНЬ {{ currentDay }}</div>
            <button @click="changeDay(1)" class="day-nav-btn" :disabled="currentDay >= 5">→</button>
          </div>
          <span class="day-title">{{ displayData?.current_course_day.title }}</span>
        </div>
        <div class="stats-row">
          <div class="stat-badge stat-primary">
            <img src="/src/images/coin.png" alt="coin" class="coin-icon-learn">
            <span>{{ displayData?.xp_total }}</span> СКРОЛЛЫ
          </div>
          <div class="stat-badge stat-pink">
            <span class="icon">🔥</span>
            <span>{{ displayData?.streak_days }}</span>
          </div>
          <div class="stat-badge stat-tertiary">
            <span class="icon">📚</span>
            <span>{{ displayData?.total_learning_words }}</span>
          </div>
        </div>
      </div>

      <!-- Session Cards -->
      <div class="sessions-grid">
        <!-- Session A Card -->
        <div
          class="session-card"
          :class="{
            'completed': displayData?.session_a?.is_completed,
            'in-progress': displayData?.session_a && !displayData.session_a.is_completed
          }"
          @click="authStore.isAuthenticated ? startSession('A') : router.push('/login')"
        >
          <div class="card-glow"></div>
          <div class="session-header">
            <div class="session-label">СЕССИЯ A</div>
            <div v-if="displayData?.session_a?.is_completed" class="status-badge completed">
              ✓ ГОТОВО
            </div>
            <div v-else-if="displayData?.session_a" class="status-badge progress">
              В ПРОЦЕССЕ
            </div>
            <div v-else class="status-badge new">
              НОВАЯ
            </div>
          </div>

          <div class="session-steps">
            <div
              v-for="step in steps"
              :key="step.id"
              class="step-indicator"
              :class="{ active: isStepActive('A', step.number), completed: isStepCompleted('A', step.number) }"
            >
              <span class="step-number">{{ step.number }}</span>
              <span class="step-label">{{ step.label }}</span>
              <span class="step-time">{{ step.time }}</span>
            </div>
          </div>

          <div v-if="displayData?.session_a" class="session-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: getProgress('A') + '%' }"></div>
            </div>
            <div class="progress-text">{{ getProgress('A') }}% Выполнено</div>
          </div>

          <div class="start-btn">
            <span v-if="!authStore.isAuthenticated">ВОЙТИ →</span>
            <span v-else-if="!displayData?.session_a">НАЧАТЬ СЕССИЮ →</span>
            <span v-else-if="displayData.session_a.is_completed">ПОВТОРИТЬ СЕССИЮ →</span>
            <span v-else>ПРОДОЛЖИТЬ →</span>
          </div>
        </div>

        <!-- Session B Card -->
        <div
          class="session-card"
          :class="{
            'completed': displayData?.session_b?.is_completed,
            'in-progress': displayData?.session_b && !displayData.session_b.is_completed
          }"
          @click="authStore.isAuthenticated ? startSession('B') : router.push('/login')"
        >
          <div class="card-glow"></div>
          <div class="session-header">
            <div class="session-label">СЕССИЯ B</div>
            <div v-if="displayData?.session_b?.is_completed" class="status-badge completed">
              ✓ ГОТОВО
            </div>
            <div v-else-if="displayData?.session_b" class="status-badge progress">
              В ПРОЦЕССЕ
            </div>
            <div v-else class="status-badge new">
              НОВАЯ
            </div>
          </div>

          <div class="session-steps">
            <div
              v-for="step in steps"
              :key="step.id"
              class="step-indicator"
              :class="{ active: isStepActive('B', step.number), completed: isStepCompleted('B', step.number) }"
            >
              <span class="step-number">{{ step.number }}</span>
              <span class="step-label">{{ step.label }}</span>
              <span class="step-time">{{ step.time }}</span>
            </div>
          </div>

          <div v-if="displayData?.session_b" class="session-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: getProgress('B') + '%' }"></div>
            </div>
            <div class="progress-text">{{ getProgress('B') }}% Выполнено</div>
          </div>

          <div class="start-btn">
            <span v-if="!authStore.isAuthenticated">ВОЙТИ →</span>
            <span v-else-if="!displayData?.session_b">НАЧАТЬ СЕССИЮ →</span>
            <span v-else-if="displayData.session_b.is_completed">ПОВТОРИТЬ СЕССИЮ →</span>
            <span v-else>ПРОДОЛЖИТЬ →</span>
          </div>
        </div>
      </div>

      <!-- Back Button -->
      <div class="back-section">
        <button @click="goBack" class="back-btn">
          <span class="icon">←</span>
          <span>НАЗАД ДОМОЙ</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useAuthStore } from '@/stores/auth'
import { learningAPI } from '@/api/learning'

const router = useRouter()
const sessionStore = useSessionStore()
const authStore = useAuthStore()

const isLoading = ref(true)
const error = ref('')
const currentDay = ref(1)
const isEmptyCourse = computed(() => {
  return displayData.value && !displayData.value.session_a && !displayData.value.session_b
})
const isInitializing = ref(false)
const initError = ref('')

// Initialize HSK level from user profile (will be updated in onMounted)
const currentHSKLevel = ref(1)

const steps = [
  { id: 1, number: 1, label: 'SRS Повторение', time: '2 мин' },
  { id: 2, number: 2, label: 'Новые слова', time: '8 мин' },
  { id: 3, number: 3, label: 'Грамматика', time: '2 мин' },
  { id: 4, number: 4, label: 'Диалог', time: '2 мин' },
  { id: 5, number: 5, label: 'Практика', time: '1 мин' },
]

const mainScreenData = computed(() => sessionStore.mainScreenData)

// Fallback data to always show something
const fallbackData = computed(() => ({
  current_course_day: {
    id: 1,
    day_number: currentDay.value,
    title: `День ${currentDay.value}: Изучение китайского`
  },
  xp_total: authStore.user?.progress?.total_xp || 0,
  streak_days: authStore.user?.progress?.streak_days || 0,
  total_learning_words: 0,
  session_a: null,
  session_b: null
}))

const displayData = computed(() => mainScreenData.value || fallbackData.value)

onMounted(async () => {
  // Initialize HSK level from user profile after auth is loaded
  if (authStore.user?.profile?.current_hsk_level) {
    currentHSKLevel.value = authStore.user.profile.current_hsk_level
  }

  // Only load if authenticated
  if (authStore.isAuthenticated) {
    await loadMainScreen()
  } else {
    // Show fallback data for non-authenticated users
    isLoading.value = false
  }
})

async function loadMainScreen() {
  isLoading.value = true
  error.value = ''

  try {
    await sessionStore.loadMainScreen()
    // Update currentDay from loaded data (keep current HSK level as is)
    if (sessionStore.mainScreenData?.current_course_day) {
      currentDay.value = sessionStore.mainScreenData.current_course_day.day_number
    }
  } catch (err: any) {
    // Don't show error - use fallback data instead
    console.warn('Failed to load main screen, using fallback data:', err)
    error.value = '' // Clear error so content shows
  } finally {
    isLoading.value = false
  }
}

async function changeHSKLevel(delta: number) {
  const newLevel = currentHSKLevel.value + delta
  if (newLevel < 1 || newLevel > 6) return

  currentHSKLevel.value = newLevel
  currentDay.value = 1 // Reset to day 1 when changing HSK level

  // Only load if authenticated
  if (authStore.isAuthenticated) {
    isLoading.value = true
    error.value = ''

    try {
      await sessionStore.loadMainScreenForDay(1, newLevel)
    } catch (err: any) {
      // Don't show error - fallback data will be used
      console.warn('Failed to load HSK level:', err)
    } finally {
      isLoading.value = false
    }
  }
  // If not authenticated, fallback data will update automatically
}

async function changeDay(delta: number) {
  const newDay = currentDay.value + delta
  if (newDay < 1 || newDay > 5) return

  currentDay.value = newDay

  // Only load if authenticated
  if (authStore.isAuthenticated) {
    isLoading.value = true
    error.value = ''

    try {
      await sessionStore.loadMainScreenForDay(currentDay.value)
    } catch (err: any) {
      // Don't show error - fallback data will be used
      console.warn('Failed to load day:', err)
    } finally {
      isLoading.value = false
    }
  }
  // If not authenticated, fallback data will update automatically
}

async function startSession(type: 'A' | 'B') {
  if (!displayData.value || !authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  try {
    // Resume existing session or start new one
    const existingSession = type === 'A'
      ? displayData.value.session_a
      : displayData.value.session_b

    // Check if session exists and is not completed (current_step < 6)
    if (existingSession && !existingSession.is_completed && existingSession.current_step < 6) {
      // Resume existing session
      await sessionStore.resumeSession(existingSession.id)
    } else {
      // Start new session
      await sessionStore.startSession(displayData.value.current_course_day.id, type)
    }

    // Navigate to session view
    router.push('/session')
  } catch (err: any) {
    // Don't show error - just stay on page
    console.warn('Failed to start session:', err)
  }
}

function isStepActive(sessionType: 'A' | 'B', stepNumber: number): boolean {
  const session = sessionType === 'A'
    ? displayData.value?.session_a
    : displayData.value?.session_b
  return session?.current_step === stepNumber || false
}

function isStepCompleted(sessionType: 'A' | 'B', stepNumber: number): boolean {
  const session = sessionType === 'A'
    ? displayData.value?.session_a
    : displayData.value?.session_b
  if (!session) return false
  return session.is_completed || session.current_step > stepNumber || session.current_step >= 6
}

function getProgress(sessionType: 'A' | 'B'): number {
  const session = sessionType === 'A'
    ? displayData.value?.session_a
    : displayData.value?.session_b
  if (!session) return 0
  return Math.round((session.current_step / 6) * 100)
}

function goBack() {
  router.push('/app')
}

async function initializeDemo() {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  isInitializing.value = true
  initError.value = ''

  try {
    console.log('[LearnView] Initializing demo course...')
    const result = await learningAPI.initializeDemoCourse(currentHSKLevel.value)
    console.log('[LearnView] Demo course initialized:', result)

    // Reload main screen to show new data
    await loadMainScreen()
  } catch (err: any) {
    console.error('[LearnView] Failed to initialize demo:', err)
    initError.value = err.response?.data?.detail || err.message || 'Failed to initialize demo course'
  } finally {
    isInitializing.value = false
  }
}
</script>

<style scoped>
.learn-view {
  min-height: 100vh;
  background: var(--color-bg-primary);
  padding: 2rem;
  position: relative;
  overflow-x: hidden;
}

.bg-effects {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  pointer-events: none;
}

.grid-overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(255, 107, 53, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 107, 53, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridMove 30s linear infinite;
}

@keyframes gridMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(50px, 50px); }
}

.ambient-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(255, 107, 53, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  animation: glowPulse 10s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
  50% { transform: translate(-50%, -50%) scale(1.3); opacity: 1; }
}

.floating-orbs {
  position: absolute;
  width: 100%;
  height: 100%;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: rgba(255, 107, 53, 0.2);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: rgba(157, 78, 221, 0.15);
  top: 60%;
  right: 10%;
  animation-delay: -7s;
}

.orb-3 {
  width: 250px;
  height: 250px;
  background: rgba(255, 117, 143, 0.15);
  bottom: 10%;
  left: 30%;
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(50px, -50px) scale(1.1); }
  50% { transform: translate(-30px, 30px) scale(0.9); }
  75% { transform: translate(-50px, -30px) scale(1.05); }
}

.loading,
.error {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 2rem;
}

.warm-loader {
  width: 60px;
  height: 60px;
  border: 3px solid transparent;
  border-top-color: var(--color-accent-primary);
  border-right-color: var(--color-accent-secondary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  box-shadow: var(--shadow-primary);
}

.loading-text {
  color: var(--color-accent-primary);
  font-size: 0.9rem;
  letter-spacing: 2px;
  font-weight: 600;
  animation: flicker 1.5s infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.error-text {
  color: var(--color-accent-pink);
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 1px;
}

.retry-btn {
  padding: 1rem 2rem;
  background: var(--gradient-primary);
  color: var(--color-text-primary);
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 2px;
  cursor: pointer;
  box-shadow: var(--shadow-primary);
  transition: all 0.3s;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-primary), 0 0 30px rgba(255, 107, 53, 0.5);
}

.content {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
}

.auth-warning {
  background: rgba(255, 107, 53, 0.1);
  border: 1px solid rgba(255, 107, 53, 0.3);
  border-radius: var(--radius-lg);
  padding: 1rem 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.warning-text {
  color: var(--color-accent-primary);
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 1px;
  margin: 0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(37, 29, 45, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 107, 53, 0.2);
  border-radius: var(--radius-xl);
  flex-wrap: wrap;
  gap: 1rem;
}

.day-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.hsk-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: center;
}

.hsk-nav-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 107, 53, 0.1);
  border: 1px solid var(--color-accent-primary);
  color: var(--color-accent-primary);
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.hsk-nav-btn:hover:not(:disabled) {
  background: var(--color-accent-primary);
  color: var(--color-text-primary);
  transform: scale(1.1);
  box-shadow: var(--shadow-warm);
}

.hsk-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.hsk-badge {
  background: var(--gradient-sunset);
  color: var(--color-text-primary);
  padding: 0.5rem 1.5rem;
  border-radius: var(--radius-lg);
  font-size: 1rem;
  font-weight: 900;
  letter-spacing: 2px;
  box-shadow: var(--shadow-warm);
  min-width: 100px;
  text-align: center;
}

.day-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.day-nav-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 107, 53, 0.1);
  border: 1px solid var(--color-accent-primary);
  color: var(--color-accent-primary);
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.day-nav-btn:hover:not(:disabled) {
  background: var(--color-accent-primary);
  color: var(--color-text-primary);
  transform: scale(1.1);
}

.day-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.day-number {
  font-size: 0.9rem;
  color: var(--color-accent-primary);
  font-weight: 700;
  letter-spacing: 2px;
  min-width: 80px;
  text-align: center;
}

.day-title {
  font-size: 1.5rem;
  color: var(--color-text-primary);
  font-weight: 700;
  letter-spacing: 1px;
}

.stats-row {
  display: flex;
  gap: 1rem;
}

.stat-badge {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 0.9rem;
}

.stat-primary {
  background: rgba(255, 107, 53, 0.15);
  border: 1px solid var(--color-accent-primary);
  color: var(--color-accent-primary);
}

.stat-pink {
  background: rgba(255, 117, 143, 0.15);
  border: 1px solid var(--color-accent-pink);
  color: var(--color-accent-pink);
}

.stat-tertiary {
  background: rgba(255, 230, 109, 0.15);
  border: 1px solid var(--color-accent-tertiary);
  color: var(--color-accent-tertiary);
}

.coin-icon-learn {
  width: 24px;
  height: 24px;
  object-fit: contain;
  animation: coinFloat 2s ease-in-out infinite;
  filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.6));
}

@keyframes coinFloat {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-3px) rotate(10deg);
  }
}

.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.session-card {
  background: rgba(37, 29, 45, 0.9);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 107, 53, 0.2);
  border-radius: var(--radius-xl);
  padding: 2rem;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.session-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-primary);
}

.session-card:hover {
  border-color: var(--color-accent-primary);
  transform: translateY(-6px);
  box-shadow: var(--shadow-card), var(--shadow-primary);
}

.session-card.completed {
  border-color: var(--color-accent-tertiary);
}

.session-card.completed::before {
  background: var(--gradient-secondary);
}

.session-card.in-progress {
  border-color: rgba(255, 107, 53, 0.4);
}

.card-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: var(--gradient-primary);
  border-radius: inherit;
  z-index: -1;
  opacity: 0;
  filter: blur(20px);
  transition: opacity 0.3s;
}

.session-card:hover .card-glow {
  opacity: 0.2;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.session-label {
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--color-text-primary);
  letter-spacing: 2px;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 900;
  letter-spacing: 1px;
}

.status-badge.new {
  background: var(--gradient-primary);
  color: var(--color-text-primary);
}

.status-badge.progress {
  background: rgba(255, 107, 53, 0.2);
  border: 1px solid var(--color-accent-primary);
  color: var(--color-accent-primary);
}

.status-badge.completed {
  background: var(--gradient-secondary);
  color: var(--color-bg-primary);
}

.session-steps {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.step-indicator {
  display: grid;
  grid-template-columns: 30px 1fr 60px;
  gap: 1rem;
  align-items: center;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s;
}

.step-indicator.active {
  background: rgba(255, 107, 53, 0.15);
  border-color: var(--color-accent-primary);
}

.step-indicator.completed {
  background: rgba(6, 214, 160, 0.08);
  border-color: rgba(6, 214, 160, 0.3);
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text-muted);
}

.step-indicator.completed .step-number {
  background: var(--gradient-success);
  color: var(--color-bg-primary);
}

.step-indicator.active .step-number {
  background: var(--gradient-primary);
  color: var(--color-text-primary);
  animation: pulse 2s ease-in-out infinite;
}

.step-label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.step-indicator.active .step-label {
  color: var(--color-text-primary);
  font-weight: 600;
}

.step-time {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-align: right;
}

.session-progress {
  margin-bottom: 1.5rem;
}

.progress-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--gradient-primary);
  transition: width 0.5s ease;
}

.session-card.completed .progress-fill {
  background: var(--gradient-secondary);
}

.progress-text {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  text-align: right;
}

.start-btn {
  background: var(--gradient-primary);
  color: var(--color-text-primary);
  padding: 1rem 2rem;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-align: center;
  transition: all 0.3s;
}

.session-card.completed .start-btn {
  background: var(--gradient-secondary);
  color: var(--color-bg-primary);
}

.session-card:hover .start-btn {
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.5);
}

.back-section {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.back-btn {
  background: rgba(37, 29, 45, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 107, 53, 0.15);
  border-radius: var(--radius-lg);
  padding: 1.5rem 3rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 1px;
}

.back-btn:hover {
  transform: translateY(-4px);
  background: rgba(255, 107, 53, 0.15);
  border-color: var(--color-accent-primary);
  box-shadow: var(--shadow-primary);
}

.back-btn .icon {
  font-size: 1.5rem;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.empty-course-warning {
  background: rgba(255, 107, 53, 0.1);
  border: 2px solid rgba(255, 107, 53, 0.3);
  border-radius: var(--radius-xl);
  padding: 3rem 2rem;
  text-align: center;
  margin: 2rem auto;
  max-width: 600px;
}

.warning-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.warning-title {
  font-size: 1.5rem;
  color: var(--color-accent-primary);
  font-weight: 700;
  letter-spacing: 1px;
  margin: 0;
}

.warning-text {
  color: var(--color-text-secondary);
  font-size: 1rem;
  margin: 0;
}

.init-btn {
  background: var(--gradient-primary);
  color: var(--color-text-primary);
  padding: 1rem 3rem;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s;
}

.init-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-primary), 0 0 30px rgba(255, 107, 53, 0.5);
}

.init-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: var(--color-accent-pink);
  font-size: 0.9rem;
  margin: 0;
}
</style>
