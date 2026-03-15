import { apiClient } from './client'

// Types for Session A/B System
export interface MainScreenResponse {
  current_course_day: {
    id: number
    day_number: number
    title: string
    description: string
    estimated_minutes: number
  }
  session_a: LearningSession | null
  session_b: LearningSession | null
  due_for_review: number
  total_learning_words: number
  streak_days: number
  xp_total: number
}

export interface LearningSession {
  id: number
  course_day: any
  session_type: 'A' | 'B'
  current_step: number
  is_completed: boolean
  started_at: string
  completed_at: string | null
  words_learned: number
  problematic_words: number[]
  total_questions: number
  correct_answers: number
  xp_earned: number
  accuracy: number
  accuracy_percentage: string
  total_time_minutes: number
}

export interface StepResponse {
  step: number
  step_type: string
  data: any
  session: LearningSession
}

export interface StartSessionRequest {
  course_day_id: number
  session_type: 'A' | 'B'
}

export interface Step1SubmitRequest {
  session_id: number
  card_id: number
  selected_option_id: number
  time_spent_seconds?: number
  current_card_index?: number
  total_shown_cards?: number
}

export interface Step2WordAnswer {
  word_id: number
  selected_option_id: number
  is_correct: boolean
  time_spent_seconds: number
  pronunciation_attempts?: number
  pronunciation_ok_count?: number
}

export interface Step2SubmitRequest {
  session_id: number
  words: Step2WordAnswer[]
}

export interface Step3SubmitRequest {
  session_id: number
  built_sentence_hanzi: string
  time_spent_seconds?: number
}

export interface Step4SubmitRequest {
  session_id: number
  selected_option_index: number
  time_spent_seconds?: number
}

export interface Step5SubmitRequest {
  session_id: number
  arranged_word_ids: number[]
  time_spent_seconds?: number
}

export interface StepSubmitResponse {
  is_correct: boolean
  is_step_completed: boolean
  xp_earned: number
  next_step: number | null
  session: LearningSession
  correct_answer?: any
  explanation?: string
  next_card?: any
}

export interface SessionSummaryResponse {
  session: LearningSession
  words_learned: number
  accuracy_percentage: string
  problematic_words_count: number
  problematic_words: any[]
  time_spent_minutes: number
  xp_earned: number
  is_day_completed: boolean
}

// API functions
export const learningAPI = {
  // Main Screen
  async getMainScreen(dayNumber?: number, hskLevel?: number): Promise<MainScreenResponse> {
    const params = new URLSearchParams()
    if (dayNumber) params.append('day', dayNumber.toString())
    if (hskLevel) params.append('hsk', hskLevel.toString())
    const queryString = params.toString()
    const url = queryString ? `/learning/main-screen/?${queryString}` : '/learning/main-screen/'
    return apiClient.get(url)
  },

  // Session Management
  async startSession(data: StartSessionRequest): Promise<StepResponse> {
    return apiClient.post('/learning/start/', data)
  },

  async getStepData(sessionId: number): Promise<StepResponse> {
    return apiClient.get(`/learning/step/${sessionId}/`)
  },

  async completeSession(sessionId: number): Promise<SessionSummaryResponse> {
    return apiClient.post('/learning/complete/', { session_id: sessionId })
  },

  // Step Submissions
  async submitStep1(data: Step1SubmitRequest): Promise<StepSubmitResponse> {
    return apiClient.post('/learning/submit/step-1/', data)
  },

  async submitStep2(data: Step2SubmitRequest): Promise<StepSubmitResponse> {
    return apiClient.post('/learning/submit/step-2/', data)
  },

  async submitStep3(data: Step3SubmitRequest): Promise<StepSubmitResponse> {
    return apiClient.post('/learning/submit/step-3/', data)
  },

  async submitStep4(data: Step4SubmitRequest): Promise<StepSubmitResponse> {
    return apiClient.post('/learning/submit/step-4/', data)
  },

  async submitStep5(data: Step5SubmitRequest): Promise<StepSubmitResponse> {
    return apiClient.post('/learning/submit/step-5/', data)
  },

  // Initialize demo course with data
  async initializeDemoCourse(hskLevel?: number): Promise<{success: boolean, message: string, words_created: number}> {
    const data = hskLevel ? { hsk_level: hskLevel } : {}
    return apiClient.post('/learning/initialize-demo/', data)
  },
}
