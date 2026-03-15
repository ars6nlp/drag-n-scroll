<template>
  <div class="step-5-component">
    <div class="step-header">
      <h2 class="step-title">
        <span class="icon">🧩</span>
        ПОРЯДОК СЛОВ
      </h2>
      <p class="step-subtitle">Расположите слова, чтобы составить предложение</p>
    </div>

    <!-- No Data State -->
    <div v-if="!stepData || !stepData.data || !stepData.data.scrambled_words || stepData.data.scrambled_words.length === 0" class="no-data">
      <div class="no-data-icon">📝</div>
      <p>Нет упражнения на порядок слов для этого шага.</p>
      <p class="hint">Вернитесь позже или попробуйте другую сессию!</p>
      <button @click="skipStep" class="skip-btn">ПРОПУСТИТЬ ШАГ</button>
    </div>

    <div v-else class="arrangement-container">
      <!-- Target Sentence Display -->
      <div class="target-card">
        <div class="target-info">
          <span class="label">СЛУШАЙТЕ И СОСТАВЛЯЙТЕ:</span>
          <span class="target-hanzi clickable-word" @click="speakHanzi(stepData.data.target_hanzi)" title="Нажмите для озвучки">{{ stepData.data.target_hanzi }}</span>
          <span class="target-pinyin clickable-word" @click="speakHanzi(stepData.data.target_hanzi)" title="Нажмите для озвучки">{{ stepData.data.target_pinyin }}</span>
          <span class="target-translation">{{ getTranslation(stepData) }}</span>
        </div>

        <button @click="playAudio" class="audio-btn">
          <span class="icon">🔊</span> ВОСПРОИЗВЕСТИ АУДИО
        </button>

        <div v-if="stepData.data.hint" class="hint">
          💡 {{ getHint(stepData) }}
        </div>
      </div>

      <!-- Word Bank -->
      <div class="word-bank-section">
        <div class="section-header">
          <h4>Доступные слова</h4>
          <span class="word-count">{{ availableWords.length }} слов</span>
        </div>
        <div class="word-bank">
          <div
            v-for="word in availableWords"
            :key="word.id"
            @click="addToArrangement(word)"
            class="word-chip"
          >
            <span class="word-hanzi clickable-word" @click.stop="speakHanzi(word.hanzi)" title="Нажмите для озвучки">{{ word.hanzi }}</span>
            <span class="word-pinyin clickable-word" @click.stop="speakHanzi(word.hanzi)" title="Нажмите для озвучки">{{ word.pinyin }}</span>
          </div>
        </div>
      </div>

      <!-- Arrangement Area -->
      <div class="arrangement-area">
        <div class="section-header">
          <h4>Ваше предложение</h4>
          <span class="progress-text">{{ arrangementSlots.filter(s => s.word).length }} / {{ arrangementSlots.length }}</span>
        </div>
        <div class="arrangement-slots">
          <div
            v-for="(slot, index) in arrangementSlots"
            :key="index"
            @click="removeFromArrangement(index)"
            class="arrangement-slot"
            :class="{ filled: slot.word }"
          >
            <span v-if="slot.word" class="word-hanzi clickable-word" @click.stop="speakHanzi(slot.word.hanzi)" title="Нажмите для озвучки">{{ slot.word.hanzi }}</span>
            <span v-else class="empty-slot">
              <span class="slot-number">{{ index + 1 }}</span>
              <span class="slot-label">пусто</span>
            </span>
            <button v-if="slot.word" class="remove-btn">×</button>
          </div>
        </div>

        <!-- Current Sentence Preview -->
        <div v-if="arrangementSlots.some(s => s.word)" class="sentence-preview">
          <span class="preview-label">Текущее:</span>
          <span class="preview-text">{{ currentSentence }}</span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-section">
        <button @click="resetArrangement" class="reset-btn" v-if="arrangementSlots.some(s => s.word)">
          <span class="icon">↺</span> СБРОСИТЬ
        </button>

        <button @click="checkArrangement" class="check-btn" :disabled="!isComplete">
          <span class="icon">✓</span> ПРОВЕРИТЬ ОТВЕТ
        </button>

        <!-- Feedback -->
        <div v-if="showResult" class="feedback" :class="{ correct: isCorrect, incorrect: !isCorrect }">
          <div class="feedback-content">
            <div class="feedback-icon">{{ isCorrect ? '🎉' : '💪' }}</div>
            <div class="feedback-text">
              {{ isCorrect ? 'ИДЕАЛЬНО!' : 'ПРОДОЛЖАЙТЕ СТАРАТЬСЯ!' }}
            </div>
            <div v-if="!isCorrect" class="feedback-hint">
              Попробуйте снова или сбросьте для начала заново
            </div>
          </div>
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
const arrangementSlots = ref<any[]>([])
const showResult = ref(false)
const isCorrect = ref(false)

const userLanguage = computed(() => {
  return authStore.user?.profile?.learning_language || 'RU'
})

const availableWords = computed(() => {
  if (!props.stepData?.data?.scrambled_words) return []

  const arrangedIds = arrangementSlots.value
    .filter(s => s.word)
    .map(s => s.word.id)

  return props.stepData.data.scrambled_words.filter(
    (w: any) => !arrangedIds.includes(w.id)
  )
})

const isComplete = computed(() => {
  return arrangementSlots.value.every(slot => slot.word)
})

const currentSentence = computed(() => {
  return arrangementSlots.value
    .filter(slot => slot.word)
    .map(slot => slot.word.hanzi)
    .join('')
})

function getTranslation(item: any) {
  return userLanguage.value === 'KZ' ? item.target_translation_kz : item.target_translation_ru
}

function getHint(item: any) {
  return userLanguage.value === 'KZ' ? item.hint_kz : item.hint_ru
}

function addToArrangement(word: any) {
  const emptySlot = arrangementSlots.value.find(s => !s.word)
  if (emptySlot) {
    emptySlot.word = word
  } else {
    arrangementSlots.value.push({ word })
  }
}

function removeFromArrangement(index: number) {
  arrangementSlots.value[index].word = null
}

function resetArrangement() {
  arrangementSlots.value = arrangementSlots.value.map(() => ({ word: null }))
  showResult.value = false
  isCorrect.value = false
}

function checkArrangement() {
  if (!isComplete.value) return

  // Build sentence from arrangement
  const sentence = arrangementSlots.value
    .map(slot => slot.word.hanzi)
    .join('')

  const correctSentence = props.stepData.target_hanzi

  // Check correctness
  isCorrect.value = sentence === correctSentence
  showResult.value = true

  // Auto-submit and complete session after showing feedback
  setTimeout(() => {
    completeStep()
  }, 2000)
}

function completeStep() {
  const wordIds = arrangementSlots.value
    .filter(slot => slot.word)
    .map(slot => slot.word.id)

  emit('submit', {
    arrangedWordIds: wordIds
  })
}

function playAudio() {
  if (props.stepData?.target_hanzi) {
    speakChinese(props.stepData.target_hanzi)
  }
}

function speakHanzi(text: string) {
  if (text) {
    speakChinese(text)
  }
}

function skipStep() {
  emit('submit', {
    arrangedWordIds: props.stepData?.scrambled_words?.map((w: any) => w.id) || []
  })
}

// Initialize slots
if (props.stepData?.scrambled_words) {
  arrangementSlots.value = props.stepData.scrambled_words.map(() => ({ word: null }))
}
</script>

<style scoped>
.step-5-component {
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
  font-size: 1.8rem;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
  font-weight: 900;
  letter-spacing: 1px;
}

.step-title .icon {
  font-size: 2.2rem;
}

.step-subtitle {
  color: var(--color-text-muted);
  font-size: 1rem;
  margin: 0;
}

.arrangement-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.target-card {
  background: rgba(37, 29, 45, 0.95);
  border: 2px solid rgba(255, 107, 53, 0.3);
  border-radius: var(--radius-xl);
  padding: 2rem;
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.target-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-primary);
}

.target-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  text-align: center;
}

.label {
  color: var(--color-accent-primary);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.target-hanzi {
  font-size: 2.2rem;
  color: var(--color-text-primary);
  font-weight: 900;
  letter-spacing: 2px;
}

.target-pinyin {
  font-size: 1.3rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.target-translation {
  font-size: 1rem;
  color: var(--color-text-muted);
}

.audio-btn {
  padding: 0.9rem 2rem;
  background: var(--gradient-primary);
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 700;
  font-size: 0.95rem;
  letter-spacing: 1px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  box-shadow: var(--shadow-primary);
  transition: all 0.3s;
}

.audio-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-primary), 0 0 25px rgba(255, 107, 53, 0.5);
}

.audio-btn:active {
  transform: scale(0.98);
}

.audio-btn .icon {
  font-size: 1.3rem;
}

.hint {
  background: rgba(255, 230, 109, 0.1);
  border: 1px solid var(--color-accent-tertiary);
  border-radius: var(--radius-md);
  padding: 0.75rem 1.25rem;
  color: var(--color-accent-tertiary);
  font-size: 0.9rem;
  text-align: center;
  width: 100%;
}

.word-bank-section {
  background: rgba(37, 29, 45, 0.9);
  border: 1px solid rgba(255, 107, 53, 0.15);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.section-header h4 {
  color: var(--color-text-primary);
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.word-count {
  color: var(--color-accent-primary);
  font-size: 0.85rem;
  font-weight: 600;
  background: rgba(255, 107, 53, 0.1);
  padding: 0.3rem 0.75rem;
  border-radius: var(--radius-sm);
}

.word-bank {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  justify-content: center;
}

.word-chip {
  background: var(--gradient-primary);
  color: var(--color-text-primary);
  padding: 0.8rem 1.4rem;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: var(--shadow-primary);
  min-width: 80px;
}

.word-chip:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: var(--shadow-primary), 0 0 20px rgba(255, 107, 53, 0.5);
}

.word-chip .word-hanzi {
  font-size: 1.4rem;
  font-weight: 700;
}

.word-chip .word-pinyin {
  font-size: 0.75rem;
  opacity: 0.8;
}

.arrangement-area {
  background: rgba(37, 29, 45, 0.9);
  border: 1px solid rgba(255, 107, 53, 0.15);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
}

.arrangement-slots {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.arrangement-slot {
  width: 100px;
  height: 100px;
  background: rgba(0, 0, 0, 0.3);
  border: 2px dashed rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.arrangement-slot:hover {
  border-color: var(--color-accent-primary);
  background: rgba(255, 107, 53, 0.05);
}

.arrangement-slot.filled {
  background: var(--gradient-primary);
  border-style: solid;
  border-color: var(--color-accent-primary);
  box-shadow: var(--shadow-primary);
}

.arrangement-slot.filled:hover {
  transform: scale(1.05);
}

.word-hanzi {
  font-size: 1.6rem;
  font-weight: 900;
  color: var(--color-text-primary);
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

.empty-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  color: var(--color-text-muted);
}

.slot-number {
  font-size: 1.5rem;
  font-weight: 700;
}

.slot-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--color-accent-pink);
  border: 2px solid var(--color-bg-primary);
  color: white;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  opacity: 0;
  transform: scale(0.8);
}

.arrangement-slot.filled:hover .remove-btn {
  opacity: 1;
  transform: scale(1);
}

.remove-btn:hover {
  background: var(--color-accent-pink-dark);
  transform: scale(1.2) !important;
}

.sentence-preview {
  background: rgba(255, 107, 53, 0.1);
  border: 1px solid rgba(255, 107, 53, 0.2);
  border-radius: var(--radius-md);
  padding: 1rem;
  text-align: center;
}

.preview-label {
  display: block;
  color: var(--color-accent-primary);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
}

.preview-text {
  color: var(--color-text-primary);
  font-size: 1.2rem;
  font-weight: 600;
  letter-spacing: 2px;
}

.progress-text {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  font-weight: 600;
}

.action-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
}

.reset-btn {
  padding: 0.8rem 1.5rem;
  background: transparent;
  border: 2px solid var(--color-accent-pink);
  color: var(--color-accent-pink);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.reset-btn:hover {
  background: var(--color-accent-pink);
  color: var(--color-text-primary);
}

.check-btn,
.next-btn {
  padding: 1rem 2.5rem;
  background: var(--gradient-primary);
  color: var(--color-text-primary);
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  box-shadow: var(--shadow-primary);
  transition: all 0.3s;
}

.check-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.check-btn:hover:not(:disabled),
.next-btn:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-primary), 0 0 25px rgba(255, 107, 53, 0.5);
}

.next-btn {
  padding: 1.2rem 3rem;
  font-size: 1.1rem;
  background: var(--gradient-sunset);
}

.feedback {
  width: 100%;
  padding: 1.5rem;
  border-radius: var(--radius-md);
  animation: slideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.feedback.correct {
  background: rgba(6, 214, 160, 0.15);
  border: 2px solid var(--color-success);
  box-shadow: 0 0 30px rgba(6, 214, 160, 0.3);
}

.feedback.incorrect {
  background: rgba(255, 117, 143, 0.15);
  border: 2px solid var(--color-accent-pink);
  box-shadow: 0 0 30px rgba(255, 117, 143, 0.3);
}

.feedback-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.feedback-icon {
  font-size: 3rem;
}

.feedback-text {
  font-size: 1.4rem;
  font-weight: 900;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.feedback.correct .feedback-text {
  color: var(--color-success);
}

.feedback.incorrect .feedback-text {
  color: var(--color-accent-pink);
}

.feedback-hint {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  text-align: center;
}

.no-data {
  background: rgba(37, 29, 45, 0.9);
  border: 1px solid rgba(255, 117, 143, 0.3);
  border-radius: var(--radius-xl);
  padding: 3rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.no-data-icon {
  font-size: 4rem;
  opacity: 0.7;
}

.no-data p {
  margin: 0;
  font-size: 1.1rem;
  color: var(--color-text-primary);
}

.no-data .hint {
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.skip-btn {
  margin-top: 1rem;
  padding: 0.8rem 2rem;
  background: var(--gradient-purple);
  color: var(--color-text-primary);
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  box-shadow: var(--shadow-purple);
  transition: all 0.3s;
}

.skip-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-purple), 0 0 20px rgba(157, 78, 221, 0.5);
}
</style>
