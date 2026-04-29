import axios from 'axios'
import Cookies from 'js-cookie'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = Cookies.get('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token, refresh_token } = response.data
          Cookies.set('access_token', access_token)
          Cookies.set('refresh_token', refresh_token)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/api/login', { email, password }),
  
  register: (email: string, password: string, full_name: string) =>
    api.post('/api/register', { email, password, full_name }),
  
  logout: () => api.post('/v1/auth/logout'),
  
  me: () => api.get('/v1/auth/me'),
  
  updateProfile: (data: any) => api.put('/v1/auth/me', data),
  
  resetPassword: (email: string) =>
    api.post('/v1/auth/password-reset', { email }),
  
  confirmResetPassword: (token: string, newPassword: string) =>
    api.post('/v1/auth/password-reset/confirm', { token, new_password: newPassword }),
}

// Resume API
export const resumeApi = {
  list: () => api.get('/v1/resumes'),
  
  get: (id: string) => api.get(`/v1/resumes/${id}`),
  
  create: (data: { source_type: string; source_url?: string }) =>
    api.post('/v1/resumes', data),
  
  parse: (id: string, raw_content: string) =>
    api.post(`/v1/resumes/${id}/parse`, { raw_content }),
  
  analyze: (id: string, target_role?: string) =>
    api.post(`/v1/resumes/${id}/analyze`, { target_role }),
  
  getImprovements: (id: string) => api.get(`/v1/resumes/${id}/improvements`),
  
  updateSection: (id: string, sectionType: string, content: any) =>
    api.put(`/v1/resumes/${id}/sections/${sectionType}`, content),
  
  delete: (id: string) => api.delete(`/v1/resumes/${id}`),
}

// Interview API
export const interviewApi = {
  list: () => api.get('/v1/interviews'),
  
  get: (id: string) => api.get(`/v1/interviews/${id}`),
  
  create: (data: {
    target_role: string
    difficulty: string
    mode: string
    focus_areas?: string[]
    resume_id?: string
  }) => api.post('/v1/interviews', data),
  
  start: (id: string) => api.post(`/v1/interviews/${id}/start`),
  
  answer: (id: string, data: {
    question_id: string
    content?: string
    code?: string
    language?: string
  }) => api.post(`/v1/interviews/${id}/answer`, data),
  
  getHint: (id: string, questionId: string) =>
    api.post(`/v1/interviews/${id}/hint`, { question_id: questionId }),
  
  getFeedback: (id: string) => api.post(`/v1/interviews/${id}/feedback`),
  
  cancel: (id: string) => api.delete(`/v1/interviews/${id}`),
}

// DSA API
export const dsaApi = {
  listProblems: (params?: { difficulty?: string; topic?: string; limit?: number }) =>
    api.get('/v1/dsa/problems', { params }),
  
  getProblem: (slug: string) => api.get(`/v1/dsa/problems/${slug}`),
  
  createProblem: (data: any) => api.post('/v1/dsa/problems', data),
  
  submitSolution: (slug: string, data: { code: string; language: string }) =>
    api.post(`/v1/dsa/problems/${slug}/submit`, data),
  
  getSubmission: (id: string) => api.get(`/v1/dsa/submissions/${id}`),
  
  getUserSubmissions: (slug: string) => api.get(`/v1/dsa/problems/${slug}/submissions`),
  
  getHint: (slug: string, currentHintLevel: number) =>
    api.post(`/v1/dsa/problems/${slug}/hint`, { current_hint_level: currentHintLevel }),
  
  analyzeCode: (id: string) => api.get(`/v1/dsa/analyze/${id}`),
}

// Problem Library API (New)
export const problemsApi = {
  // Get all problems with filters
  getProblems: (params?: { 
    difficulty?: string; 
    topic?: string; 
    search?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/api/problems', { params }),
  
  // Get single problem details
  getProblem: (slug: string) => api.get(`/api/problems/${slug}`),
  
  // Get daily problem
  getDailyProblem: () => api.get('/api/daily-problem'),
  
  // Get all topics
  getTopics: () => api.get('/api/topics'),
  
  // Get all difficulties
  getDifficulties: () => api.get('/api/difficulties'),
}

// AI API
export const aiApi = {
  generateInterviewPlan: (data: {
    target_role: string
    experience_level: string
    difficulty: string
    focus_areas: string[]
    duration_minutes: number
    resume_data?: any
  }) => api.post('/v1/ai/interview-plan', data),
  
  generateQuestion: (data: {
    topic: string
    difficulty: number
    question_number: number
  }) => api.post('/v1/ai/question', data),
  
  analyzeResponse: (data: {
    question: string
    question_type: string
    expected_points: string[]
    answer: string
  }) => api.post('/v1/ai/analyze', data),
  
  generateFeedback: (data: {
    session_responses: any[]
    user_profile?: any
  }) => api.post('/v1/ai/feedback', data),
}

// WebSocket connection
export const createWebSocket = (sessionId: string, token: string) => {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
  return new WebSocket(`${wsUrl}/v1/interviews/${sessionId}/stream?token=${token}`)
}
