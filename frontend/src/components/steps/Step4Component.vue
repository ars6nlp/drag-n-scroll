<template>
  <div class="step-4-component">
    <div class="step-header">
      <h2 class="step-title">
        <span class="icon">🎧</span>
        АУДИРОВАНИЕ
      </h2>
      <p class="step-subtitle">Слушайте и выбирайте правильный ответ</p>
    </div>

    <!-- No Data State -->
    <div v-if="!stepData || !stepData.lines || stepData.lines.length === 0" class="no-data">
      <p>Нет упражнения на диалог для этого шага.</p>
      <p class="hint">Пожалуйста, вернитесь позже или свяжитесь с поддержкой.</p>
    </div>

    <div v-else class="dialogue-container">
      <!-- Dialogue Display -->
      <div class="dialogue-card">
        <div class="dialogue-lines">
          <div
            v-for="(line, index) in stepData.lines"
            :key="index"
            class="dialogue-line"
          >
            <span class="speaker">{{ line.speaker }}:</span>
            <div class="line-content">
              <span class="hanzi clickable-word" @click="speakHanzi(line.hanzi)" title="Нажмите для озвучки">{{ line.hanzi }}</span>
              <span class="pinyin clickable-word" @click="speakHanzi(line.hanzi)" title="Нажмите для озвучки">{{ line.pinyin }}</span>
              <span class="translation">{{ getTranslation(line) }}</span>
            </div>
          </div>
        </div>

        <div class="question-section">
          <h4>Вопрос:</h4>
          <div class="question">
            <span class="question-hanzi clickable-word" @click="speakHanzi(stepData.question_hanzi)" title="Нажмите для озвучки">{{ stepData.question_hanzi }}</span>
            <span class="question-pinyin clickable-word" @click="speakHanzi(stepData.question_hanzi)" title="Нажмите для озвучки">{{ stepData.question_pinyin }}</span>
          </div>

          <button @click="playAudio" class="play-audio-btn">
            <span class="icon">🔊</span> ВОСПРОИЗВЕСТИ ДИАЛОГ
          </button>
        </div>
      </div>

      <!-- Response Options -->
      <div class="options-section">
        <h4>Как бы вы ответили?</h4>
        <div class="options-grid">
          <button
            v-for="(option, index) in stepData.options"
            :key="index"
            @click="selectOption(index)"
            class="option-card"
            :class="{
              selected: selectedOption === index,
              correct: showResult && option.is_correct,
              incorrect: showResult && selectedOption === index && !option.is_correct
            }"
            :disabled="showResult"
          >
            <span class="option-hanzi clickable-word" @click="speakHanzi(option.hanzi)" title="Нажмите для озвучки">{{ option.hanzi }}</span>
            <span class="option-pinyin clickable-word" @click="speakHanzi(option.hanzi)" title="Нажмите для озвучки">{{ option.pinyin }}</span>
            <span class="option-translation">{{ getTranslation(option) }}</span>
          </button>
        </div>
      </div>

      <!-- Feedback -->
      <div v-if="showResult" class="feedback-container">
        <div class="feedback" :class="{ correct: isCorrect, incorrect: !isCorrect }">
          <div class="feedback-icon">{{ isCorrect ? '✓' : '✗' }}</div>
          <div class="feedback-text">
            {{ isCorrect ? 'ПРАВИЛЬНО!' : 'НЕ СОВСЕМ' }}
          </div>
          <div v-if="explanation" class="explanation">{{ explanation }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { speakChinese } from '@/utils/speech'

const props = defineProps<{
  stepData: any
  session: any
}>()

const emit = defineEmits(['submit'])

const authStore = useAuthStore()
const selectedOption = ref<number | null>(null)
const showResult = ref(false)
const isCorrect = ref(false)
const explanation = ref('')

const userLanguage = computed(() => {
  return authStore.user?.profile?.learning_language || 'RU'
})

function getTranslation(item: any) {
  return userLanguage.value === 'KZ' ? item.translation_kz : item.translation_ru
}

function selectOption(index: number) {
  if (showResult.value) return

  selectedOption.value = index
  const option = props.stepData?.options[index]

  isCorrect.value = option.is_correct
  showResult.value = true

  // Set explanation
  explanation.value = option?.explanation || ''

  // Auto-submit and move to next step after showing feedback
  setTimeout(() => {
    completeStep()
  }, 2000)
}

function completeStep() {
  emit('submit', {
    selectedOptionIndex: selectedOption.value
  })
}

function playAudio() {
  if (props.stepData?.question_hanzi) {
    speakChinese(props.stepData.question_hanzi)
  }
}

function speakHanzi(text: string) {
  if (text) {
    speakChinese(text)
  }
}
</script>

<style scoped>
.step-4-component {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.step-header {
  text-align: center;
}

.step-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
}

.step-title .icon {
  font-size: 2rem;
}

.step-subtitle {
  color: var(--color-text-muted);
  font-size: 1rem;
  margin: 0;
}

.dialogue-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dialogue-card {
  background: rgba(17, 19, 24, 0.95);
  border: 2px solid rgba(0, 229, 255, 0.3);
  border-radius: var(--radius-xl);
  padding: 2rem;
  box-shadow: var(--shadow-card);
}

.dialogue-lines {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.dialogue-line {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
}

.speaker {
  font-weight: 700;
  color: var(--color-accent-cyan);
  min-width: 80px;
}

.line-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.hanzi {
  font-size: 1.2rem;
  color: var(--color-text-primary);
  font-weight: 600;
}

.pinyin {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.clickable-word {
  cursor: pointer;
  transition: all 0.3s;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  display: inline-block;
}

.clickable-word:hover {
  transform: scale(1.03);
  color: var(--color-accent-cyan);
}

.translation {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.question-section {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.question-section h4 {
  color: var(--color-text-primary);
  margin: 0;
  font-size: 1.1rem;
}

.question {
  text-align: center;
}

.question-hanzi {
  font-size: 1.5rem;
  color: var(--color-text-primary);
  font-weight: 700;
  display: block;
  margin-bottom: 0.5rem;
}

.question-pinyin {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
}

.play-audio-btn {
  padding: 0.75rem 1.5rem;
  background: var(--gradient-cyber);
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-bg-primary);
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: var(--shadow-cyan);
  transition: all 0.3s;
}

.play-audio-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-cyan), 0 0 20px rgba(0, 229, 255, 0.5);
}

.play-audio-btn .icon {
  font-size: 1.2rem;
}

.options-section {
  background: rgba(17, 19, 24, 0.9);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: var(--radius-xl);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.options-section h4 {
  color: var(--color-text-primary);
  margin: 0;
  font-size: 1.2rem;
  text-align: center;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.option-card {
  background: rgba(255, 255, 255, 0.03);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: center;
}

.option-card:hover:not(:disabled) {
  background: rgba(0, 229, 255, 0.1);
  border-color: var(--color-accent-cyan);
  transform: translateY(-2px);
}

.option-card.selected {
  border-color: var(--color-accent-cyan);
  background: rgba(0, 229, 255, 0.15);
}

.option-card.correct {
  background: rgba(0, 255, 100, 0.2);
  border-color: var(--color-success);
}

.option-card.incorrect {
  background: rgba(255, 46, 46, 0.2);
  border-color: var(--color-accent-red);
}

.option-hanzi {
  font-size: 1.3rem;
  color: var(--color-text-primary);
  font-weight: 700;
}

.option-pinyin {
  font-size: 1rem;
  color: var(--color-text-secondary);
}

.option-translation {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.feedback-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
}

.feedback {
  width: 100%;
  padding: 1.5rem;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feedback.correct {
  background: rgba(0, 255, 100, 0.2);
  border: 1px solid var(--color-success);
}

.feedback.incorrect {
  background: rgba(255, 46, 46, 0.2);
  border: 1px solid var(--color-accent-red);
}

.feedback-icon {
  font-size: 3rem;
  font-weight: 900;
}

.feedback.correct .feedback-icon {
  color: var(--color-success);
}

.feedback.incorrect .feedback-icon {
  color: var(--color-accent-red);
}

.feedback-text {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: 1px;
}

.explanation {
  color: var(--color-text-muted);
  font-size: 1rem;
  text-align: center;
  line-height: 1.5;
}

.next-btn {
  padding: 1rem 2rem;
  background: var(--gradient-cyber);
  color: var(--color-bg-primary);
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  box-shadow: var(--shadow-cyan);
  transition: all 0.3s;
}

.next-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-cyan), 0 0 20px rgba(0, 229, 255, 0.5);
}

.no-data {
  background: rgba(17, 19, 24, 0.9);
  border: 1px solid rgba(255, 46, 46, 0.3);
  border-radius: var(--radius-xl);
  padding: 3rem 2rem;
  text-align: center;
  color: var(--color-text-primary);
}

.no-data p {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.no-data .hint {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}
</style>
