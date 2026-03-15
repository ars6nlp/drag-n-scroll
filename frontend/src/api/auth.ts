import { apiClient } from './client'
import type {
  User,
  AuthTokens,
  RegisterData,
  LoginData,
  UserProfile,
  UserProgress,
} from '@/types/api'

export const authAPI = {
  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<{ user: User }>('/auth/users/', data)
    return response.user
  },

  async login(data: LoginData): Promise<AuthTokens> {
    return apiClient.post('/auth/jwt/create/', data)
  },

  async logout(refreshToken: string): Promise<void> {
    return apiClient.post('/auth/logout/', { refresh: refreshToken })
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    return apiClient.post('/auth/jwt/refresh/', { refresh: refreshToken })
  },

  async getCurrentUser(): Promise<User> {
    try {
      // Try our custom endpoint first
      return await apiClient.get('/user/me/')
    } catch (error) {
      console.warn('[Auth] /user/me/ failed, trying /auth/users/me/', error)
      // Fallback to djoser endpoint
      return apiClient.get('/auth/users/me/')
    }
  },

  async getProfile(): Promise<UserProfile> {
    return apiClient.get('/user/profile/')
  },

  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    return apiClient.patch('/user/profile/', data)
  },

  async getProgress(): Promise<UserProgress> {
    const user = await apiClient.get<User>('/user/me/')
    return user.progress as UserProgress
  },

  async getUserById(userId: number): Promise<User> {
    return apiClient.get(`/user/by-id/${userId}/`)
  },
}
