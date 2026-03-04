import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

class APIClient {
  private client: AxiosInstance
  private isRefreshing = false

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      // Disable caching to prevent stale 404 responses
      paramsSerializer: {
        indexes: null
      }
    })

    // Request interceptor - add auth token and logging
    this.client.interceptors.request.use(
      (config) => {
        const accessToken = localStorage.getItem('access_token')
        if (accessToken) {
          config.headers.Authorization = `Bearer ${accessToken}`
        }
        // Log request for debugging
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('[API] Request error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor - handle token refresh with better error handling
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[API] ${response.config.url} - Status: ${response.status}`)
        return response
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as any

        console.error('[API] Response error:', {
          url: originalRequest?.url,
          status: error.response?.status,
          message: error.message
        })

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
          originalRequest._retry = true

          // Don't try to refresh if we're already on login/register pages
          const currentPath = window.location.pathname
          if (currentPath === '/login' || currentPath === '/register') {
            console.warn('[API] Already on auth page, skipping refresh')
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('ai_access_until')
            return Promise.reject(error)
          }

          // If already refreshing, wait
          if (this.isRefreshing) {
            return new Promise((resolve, reject) => {
              setTimeout(() => {
                this.client(originalRequest)
                  .then(resolve)
                  .catch(reject)
              }, 1000)
            })
          }

          this.isRefreshing = true

          try {
            const refreshToken = localStorage.getItem('refresh_token')
            if (!refreshToken) {
              throw new Error('No refresh token available')
            }

            console.log('[API] Refreshing token...')
            const response = await axios.post(`${API_BASE_URL}/auth/jwt/refresh/`, {
              refresh: refreshToken
            })

            const { access } = response.data
            localStorage.setItem('access_token', access)

            // Djoser simplejwt doesn't return refresh token on refresh (rotate is on backend)
            // but if it does, save it
            if (response.data.refresh) {
              localStorage.setItem('refresh_token', response.data.refresh)
            }

            console.log('[API] Token refreshed successfully')

            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${access}`
            }

            this.isRefreshing = false
            return this.client(originalRequest)
          } catch (refreshError: any) {
            console.error('[API] Token refresh failed:', refreshError)
            this.isRefreshing = false

            // Check if error is due to invalid/expired token or user not found
            const errorStatus = refreshError.response?.status
            if (errorStatus === 401 || errorStatus === 404) {
              console.warn('[API] Session expired or user not found. Clearing tokens...')
              // Clear ALL auth data
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              localStorage.removeItem('ai_access_until')
              // Only redirect if not already on login page
              if (currentPath !== '/login') {
                window.location.href = '/login?session_expired=true'
              }
            } else {
              // For other errors, still clear tokens but don't show special message
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              if (currentPath !== '/login') {
                window.location.href = '/login'
              }
            }
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, params?: any) {
    const response = await this.client.get<T>(url, { params })
    return response.data
  }

  async post<T>(url: string, data?: any, config?: any) {
    const response = await this.client.post<T>(url, data, config)
    return response.data
  }

  async patch<T>(url: string, data?: any) {
    const response = await this.client.patch<T>(url, data)
    return response.data
  }

  async put<T>(url: string, data?: any) {
    const response = await this.client.put<T>(url, data)
    return response.data
  }

  async delete<T>(url: string) {
    const response = await this.client.delete<T>(url)
    return response.data
  }
}

export const apiClient = new APIClient()
