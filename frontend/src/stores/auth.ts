import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'
import type { User, UserProfile, UserProgress, RegisterData, LoginData } from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const profile = ref<UserProfile | null>(null)
  const progress = ref<UserProgress | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const isInitialized = ref(false)
  const isAuthenticated = computed(() => !!user.value && !!accessToken.value)

  // AI Access State
  const aiAccessUntil = ref<string | null>(localStorage.getItem('ai_access_until'))
  const hasAIAccess = computed(() => {
    if (!aiAccessUntil.value) return false
    const accessDate = new Date(aiAccessUntil.value)
    return accessDate > new Date()
  })
  const aiAccessDaysLeft = computed(() => {
    if (!aiAccessUntil.value) return 0
    const accessDate = new Date(aiAccessUntil.value)
    const now = new Date()
    const diffTime = accessDate.getTime() - now.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return Math.max(0, diffDays)
  })

  // Actions
  async function register(data: RegisterData) {
    try {
      await authAPI.register(data)
      // Registration succeeded - user is created but not authenticated yet
      // The djoser /auth/users/ endpoint only returns user data, not tokens
      // User needs to login separately to get authenticated
      return true
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    }
  }

  async function login(data: LoginData) {
    try {
      const response = await authAPI.login(data)
      accessToken.value = response.access
      refreshToken.value = response.refresh

      localStorage.setItem('access_token', response.access)
      localStorage.setItem('refresh_token', response.refresh)

      await loadUser()
      return true
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  async function logout() {
    try {
      if (refreshToken.value) {
        await authAPI.logout(refreshToken.value)
      }
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      // Clear local state regardless of API call success
      user.value = null
      profile.value = null
      progress.value = null
      accessToken.value = null
      refreshToken.value = null

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  async function loadUser() {
    try {
      const userData = await authAPI.getCurrentUser()
      user.value = userData
      profile.value = userData.profile || null
      progress.value = userData.progress || null
    } catch (error) {
      console.error('Failed to load user:', error)
      throw error
    }
  }

  async function loadProfile() {
    try {
      const [profileData, progressData] = await Promise.all([
        authAPI.getProfile(),
        authAPI.getProgress(),
      ])
      profile.value = profileData
      progress.value = progressData
    } catch (error) {
      console.error('Failed to load profile:', error)
    }
  }

  async function updateProfile(data: Partial<UserProfile>) {
    try {
      const updated = await authAPI.updateProfile(data)
      profile.value = updated
      if (user.value) {
        user.value.profile = updated
      }
    } catch (error) {
      console.error('Failed to update profile:', error)
      throw error
    }
  }

  async function initializeAuth() {
    const access = localStorage.getItem('access_token')
    const refresh = localStorage.getItem('refresh_token')

    if (access && refresh) {
      accessToken.value = access
      refreshToken.value = refresh
      isLoading.value = true
      try {
        await loadUser()
      } catch (error: any) {
        // Token might be expired, clear auth but only if NOT on login page
        const currentPath = window.location.pathname
        if (currentPath !== '/login' && currentPath !== '/register') {
          // Clear local state only (don't call logout API)
          user.value = null
          profile.value = null
          progress.value = null
          accessToken.value = null
          refreshToken.value = null
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      } finally {
        isLoading.value = false
        isInitialized.value = true
      }
    } else {
      isInitialized.value = true
    }
  }

  // AI Access Functions
  function purchaseAIAccess(days: number) {
    const now = new Date()
    const currentAccess = aiAccessUntil.value ? new Date(aiAccessUntil.value) : now

    // If current access is expired, start from now, otherwise extend from current end date
    const startDate = currentAccess > now ? currentAccess : now
    const endDate = new Date(startDate)
    endDate.setDate(endDate.getDate() + days)

    aiAccessUntil.value = endDate.toISOString()
    localStorage.setItem('ai_access_until', aiAccessUntil.value)
  }

  function clearAIAccess() {
    aiAccessUntil.value = null
    localStorage.removeItem('ai_access_until')
  }

  return {
    user,
    profile,
    progress,
    accessToken,
    refreshToken,
    isLoading,
    isInitialized,
    isAuthenticated,
    aiAccessUntil,
    hasAIAccess,
    aiAccessDaysLeft,
    register,
    login,
    logout,
    loadUser,
    loadProfile,
    updateProfile,
    initializeAuth,
    purchaseAIAccess,
    clearAIAccess,
  }
})
