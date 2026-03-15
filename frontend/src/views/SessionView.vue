<template>
  <div class="session-view">
    <div class="bg-effects">
      <div class="grid-overlay"></div>
      <div class="ambient-glow"></div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading">
      <div class="cyber-loader"></div>
      <div class="loading-text">ЗАГРУЗКА СЕССИИ...</div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error">
      <p class="error-text">{{ error }}</p>
      <button @click="goBack" class="retry-btn">НАЗАД К ОБУЧЕНИЮ</button>
    </div>

    <!-- Session Content -->
    <div v-else-if="currentSession" class="session-content">
      <!-- Header -->
      <div class="header">
        <button @click="goBack" class="back-btn">
          <span>←</span> ВЫЙТИ
        </button>
        <div class="session-info">
          <span class="session-type">СЕССИЯ {{ currentSession.session_type }}</span>
          <span class="step-indicator">ШАГ {{ currentStep }}/5</span>
        </div>
        <div class="timer">
          <span class="icon">⏱️</span>
          <span>{{ formattedTime }}</span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="progress-container">
        <div class="progress-bar">
          <div
            v-for="i in 5"
            :key="i"
            class="progress-segment"
            :class="{
              active: i === currentStep,
              completed: i < currentStep
            }"
          ></div>
        </div>
      </div>

      <!-- Step Navigation -->
      <div class="step-navigation">
        <button
          @click="goToPreviousStep"
          class="nav-btn prev-btn"
          :disabled="currentStep <= 1"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
          НАЗАД
        </button>

        <div class="step-indicators">
          <button
            v-for="step in 5"
            :key="step"
            @click="goToStep(step)"
            class="step-indicator-btn"
            :disabled="step > sessionStore.currentStep"
            :class="{
              active: step === currentStep,
              completed: step < currentStep
            }"
          >
            {{ step }}
          </button>
        </div>

        <button
          @click="goToNextStep"
          class="nav-btn next-btn"
          :disabled="currentStep >= 5 || currentStep >= sessionStore.currentStep"
        >
          ДАЛЕЕ
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </button>
      </div>

      <!-- Step Components -->
      <div class="step-container">
        <!-- Step 1: SRS Review -->
        <Step1Component
          v-if="currentStep === 1"
          :step-data="currentStepData"
          :session="currentSession"
          @submit="handleSubmitStep1"
        />

        <!-- Step 2: New Words -->
        <Step2Component
          v-if="currentStep === 2"
          :step-data="currentStepData"
          :session="currentSession"
          @submit="handleSubmitStep2"
        />

        <!-- Step 3: Grammar -->
        <Step3Component
          v-if="currentStep === 3"
          :step-data="currentStepData"
          :session="currentSession"
          @submit="handleSubmitStep3"
        />

        <!-- Step 4: Dialogue -->
        <Step4Component
          v-if="currentStep === 4"
          :step-data="currentStepData"
          :session="currentSession"
          @submit="handleSubmitStep4"
        />

        <!-- Step 5: Word Arrangement -->
        <Step5Component
          v-if="currentStep === 5"
          :step-data="currentStepData"
          :session="currentSession"
          @submit="handleSubmitStep5"
        />
      </div>

      <!-- Scrolls Earned Badge -->
      <div v-if="currentSession.xp_earned > 0" class="scrolls-badge">
        <span class="icon">⚡</span>
        <span>{{ currentSession.xp_earned }}</span> СКРОЛЛЫ
      </div>
    </div>

    <!-- Session Complete - Show Summary -->
    <SessionSummaryView
      v-if="showSummary"
      :session="currentSession"
      :summary="sessionSummary"
      @close="goBack"
      @retry="retrySession"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import Step1Component from '@/components/steps/Step1Component.vue'
import Step2Component from '@/components/steps/Step2Component.vue'
import Step3Component from '@/components/steps/Step3Component.vue'
import Step4Component from '@/components/steps/Step4Component.vue'
import Step5Component from '@/components/steps/Step5Component.vue'
import SessionSummaryView from '@/components/steps/SessionSummaryView.vue'

const router = useRouter()
const sessionStore = useSessionStore()

const isLoading = ref(true)
const error = ref('')
const showSummary = ref(false)
const sessionSummary = ref<any>(null)
const timerInterval = ref<number | null>(null)
const userStepOverride = ref<number | null>(null) // User manually navigated to this step

const currentSession = computed(() => sessionStore.currentSession)
const currentStep = computed(() => userStepOverride.value || sessionStore.currentStep)
const currentStepData = computed(() => sessionStore.currentStepData)
const timeRemaining = computed(() => sessionStore.timeRemaining)

const formattedTime = computed(() => {
  const minutes = Math.floor(timeRemaining.value / 60)
  const seconds = timeRemaining.value % 60
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

onMounted(async () => {
  await loadSession()
  startTimer()
})

onUnmounted(() => {
  stopTimer()
})

async function loadSession() {
  isLoading.value = true
  error.value = ''

  try {
    // Check if we have session data and step data
    if (!sessionStore.currentSession) {
      error.value = 'No active session found'
      router.push('/learn')
    } else if (!sessionStore.currentStepData || !sessionStore.currentStepData.cards || sessionStore.currentStepData.cards.length === 0) {
      // If we have session but no step data (or empty data), load it
      console.log('Loading step data from server...')
      const response = await sessionStore.moveToStep(sessionStore.currentStep)
      if (response) {
        sessionStore.currentStepData = response.data
        console.log('Loaded step data:', response)
      }
    } else {
      console.log('Using existing step data:', sessionStore.currentStepData)
    }
    // If both exist, we're good - data was already loaded by startSession
  } catch (err: any) {
    console.error('Error in loadSession:', err)
    error.value = err.response?.data?.detail || 'Failed to load session'
  } finally {
    isLoading.value = false
  }
}

function startTimer() {
  timerInterval.value = window.setInterval(() => {
    if (sessionStore.timeRemaining > 0) {
      sessionStore.timeRemaining--
    } else {
      // Time's up - Auto submit or show warning
      stopTimer()
    }
  }, 1000)
}

function stopTimer() {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
}

// Step Navigation Functions
async function goToStep(stepNumber: number) {
  if (!currentSession.value || stepNumber < 1 || stepNumber > 5) return

  const actualStep = sessionStore.currentStep

  // Only allow navigating to current step or completed steps
  if (stepNumber > actualStep) {
    console.log('Cannot jump ahead to step', stepNumber, 'current step is', actualStep)
    return // Don't allow jumping ahead
  }

  // Only load if moving to a different step
  if (stepNumber !== actualStep) {
    userStepOverride.value = stepNumber
    await loadStepData(stepNumber)
  }
}

async function goToPreviousStep() {
  if (currentStep.value > 1) {
    await goToStep(currentStep.value - 1)
  }
}

async function goToNextStep() {
  if (currentStep.value < 5) {
    await goToStep(currentStep.value + 1)
  }
}

async function loadStepData(stepNumber: number) {
  try {
    console.log('=== Loading step data ===', stepNumber)
    // Fetch step data from API
    await sessionStore.moveToStep(stepNumber)
    console.log('=== Step data loaded ===')
    console.log('sessionStore.currentStepData:', sessionStore.currentStepData)
    console.log('sessionStore.currentStep:', sessionStore.currentStep)
    // Store will be updated by moveToStep
  } catch (err) {
    console.error('Error loading step data:', err)
    error.value = 'Failed to load step data'
  }
}

async function handleSubmitStep1(data: any) {
  userStepOverride.value = null // Clear override when submitting
  try {
    const response = await sessionStore.submitStep1(
      data.cardId,
      data.selectedOptionId,
      data.currentCardIndex,
      data.totalShownCards
    )

    if (response && !response.is_correct && response.explanation) {
      // Show feedback
    }

    // Auto-load step 2 data after step 1 completes
    if (response && response.next_step) {
      await loadStepData(response.next_step)
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to submit answer'
  }
}

async function handleSubmitStep2(data: any) {
  userStepOverride.value = null
  try {
    const response = await sessionStore.submitStep2(data.words)

    // Auto-load step 3 data after step 2 completes
    if (response && response.next_step) {
      await loadStepData(response.next_step)
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to submit words'
  }
}

async function handleSubmitStep3(data: any) {
  userStepOverride.value = null
  try {
    const response = await sessionStore.submitStep3(data.builtSentence)

    // Auto-load step 4 data after step 3 completes
    if (response && response.next_step) {
      await loadStepData(response.next_step)
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to submit grammar'
  }
}

async function handleSubmitStep4(data: any) {
  userStepOverride.value = null
  try {
    const response = await sessionStore.submitStep4(data.selectedOptionIndex)

    // Auto-load step 5 data after step 4 completes
    if (response && response.next_step) {
      await loadStepData(response.next_step)
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to submit dialogue'
  }
}

async function handleSubmitStep5(data: any) {
  userStepOverride.value = null
  try {
    await sessionStore.submitStep5(data.arrangedWordIds)

    // Complete session and get summary
    const summary = await sessionStore.completeSession()

    // Store summary data
    sessionSummary.value = summary

    // Show summary with data
    showSummary.value = true
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to complete session'
  }
}

function retrySession() {
  showSummary.value = false
  userStepOverride.value = 1
  router.push('/session')
}

function goBack() {
  stopTimer()
  sessionStore.resetState()
  router.push('/learn')
}

// Watch for session completion
watch(currentSession, (newSession) => {
  if (newSession?.is_completed) {
    showSummary.value = true
  }
})
</script>

<style scoped>
.session-view {
  min-height: 100vh;
  background: var(--color-bg-primary);
  position: relative;
  overflow: hidden;
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
    linear-gradient(rgba(0, 229, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 229, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridMove 20s linear infinite;
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
  background: radial-gradient(circle, rgba(0, 229, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: glowPulse 10s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  50% { transform: translate(-50%, -50%) scale(1.3); opacity: 0.8; }
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

.cyber-loader {
  width: 60px;
  height: 60px;
  border: 3px solid transparent;
  border-top-color: var(--color-accent-cyan);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  box-shadow: var(--shadow-cyan);
}

.loading-text {
  color: var(--color-accent-cyan);
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

.retry-btn,
.back-btn {
  padding: 1rem 2rem;
  background: var(--gradient-cyber);
  color: var(--color-bg-primary);
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 2px;
  cursor: pointer;
  box-shadow: var(--shadow-cyan);
  transition: all 0.3s;
}

.retry-btn:hover,
.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-cyan), 0 0 30px rgba(0, 229, 255, 0.5);
}

.back-btn {
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.session-content {
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(17, 19, 24, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: var(--radius-xl);
}

.session-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.session-type {
  font-size: 1.2rem;
  font-weight: 900;
  color: var(--color-accent-cyan);
  letter-spacing: 2px;
}

.step-indicator {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  letter-spacing: 1px;
}

.timer {
  background: rgba(17, 19, 24, 0.9);
  border: 1px solid rgba(0, 229, 255, 0.3);
  border-radius: var(--radius-md);
  padding: 0.75rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-accent-cyan);
  font-weight: 700;
  font-size: 1.1rem;
}

.timer .icon {
  font-size: 1.3rem;
}

.progress-container {
  margin-bottom: 1.5rem;
}

.progress-bar {
  display: flex;
  gap: 0.5rem;
}

.progress-segment {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-sm);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.progress-segment.active {
  background: rgba(0, 229, 255, 0.3);
  border: 1px solid var(--color-accent-cyan);
  box-shadow: 0 0 10px var(--color-accent-cyan);
  animation: pulse 2s ease-in-out infinite;
}

.progress-segment.completed {
  background: var(--gradient-success);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Step Navigation */
.step-navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding: 1rem 1.5rem;
  background: rgba(17, 19, 24, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: var(--radius-xl);
  gap: 1rem;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: var(--gradient-cyber);
  color: var(--color-bg-primary);
  border: none;
  border-radius: var(--radius-md);
  font-weight: 700;
  font-size: 0.9rem;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: var(--shadow-cyan);
}

.nav-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-cyan), 0 0 20px rgba(0, 229, 255, 0.5);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.step-indicators {
  display: flex;
  gap: 0.5rem;
}

.step-indicator-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--color-text-muted);
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-indicator-btn.active {
  background: var(--gradient-cyber);
  color: var(--color-bg-primary);
  border-color: var(--color-accent-cyan);
  box-shadow: 0 0 15px var(--color-accent-cyan);
}

.step-indicator-btn.completed {
  background: var(--gradient-success);
  color: var(--color-bg-primary);
  border-color: var(--color-success);
}

.step-indicator-btn:hover:not(.active):not(.completed) {
  background: rgba(0, 229, 255, 0.1);
  border-color: var(--color-accent-cyan);
}

.step-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.scrolls-badge {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: var(--gradient-cyber);
  padding: 1rem 1.5rem;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 900;
  font-size: 1.1rem;
  color: var(--color-bg-primary);
  box-shadow: var(--shadow-cyan);
  z-index: 100;
  animation: slideIn 0.5s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.scrolls-badge .icon {
  font-size: 1.3rem;
}
</style>
