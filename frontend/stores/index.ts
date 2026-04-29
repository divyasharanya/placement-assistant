import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import Cookies from 'js-cookie'

// User Types
interface User {
  id: string
  email: string
  full_name: string
  avatar_url?: string
  role: string
  subscription_tier: string
  email_verified: boolean
}

interface UserProfile {
  target_role?: string
  experience_level?: string
  preferred_languages?: string[]
  timezone?: string
  interview_frequency?: number
}

// Auth Store
interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      setUser: (user) => set({ user, isAuthenticated: !!user, isLoading: false }),
      setLoading: (isLoading) => set({ isLoading }),
      logout: () => {
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        set({ user: null, isAuthenticated: false })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)

// Interview Session Store
interface Question {
  id: string
  type: string
  content: string
  sequence: number
  time_limit?: number
  hints?: string[]
}

interface InterviewState {
  sessionId: string | null
  status: 'idle' | 'connecting' | 'active' | 'paused' | 'completed'
  currentQuestion: Question | null
  questionIndex: number
  totalQuestions: number
  responses: any[]
  isRecording: boolean
  transcript: string
  
  setSessionId: (id: string | null) => void
  setStatus: (status: InterviewState['status']) => void
  setCurrentQuestion: (question: Question | null) => void
  setQuestionIndex: (index: number) => void
  setTotalQuestions: (total: number) => void
  addResponse: (response: any) => void
  setIsRecording: (recording: boolean) => void
  setTranscript: (transcript: string) => void
  reset: () => void
}

export const useInterviewStore = create<InterviewState>()((set) => ({
  sessionId: null,
  status: 'idle',
  currentQuestion: null,
  questionIndex: 0,
  totalQuestions: 0,
  responses: [],
  isRecording: false,
  transcript: '',
  
  setSessionId: (sessionId) => set({ sessionId }),
  setStatus: (status) => set({ status }),
  setCurrentQuestion: (currentQuestion) => set({ currentQuestion }),
  setQuestionIndex: (questionIndex) => set({ questionIndex }),
  setTotalQuestions: (totalQuestions) => set({ totalQuestions }),
  addResponse: (response) => set((state) => ({ responses: [...state.responses, response] })),
  setIsRecording: (isRecording) => set({ isRecording }),
  setTranscript: (transcript) => set({ transcript }),
  reset: () => set({
    sessionId: null,
    status: 'idle',
    currentQuestion: null,
    questionIndex: 0,
    responses: [],
    isRecording: false,
    transcript: '',
  }),
}))

// Resume Store
interface Resume {
  id: string
  parsed_data?: any
  ats_score?: number
  improvement_suggestions?: any[]
}

interface ResumeState {
  resumes: Resume[]
  currentResume: Resume | null
  isLoading: boolean
  
  setResumes: (resumes: Resume[]) => void
  setCurrentResume: (resume: Resume | null) => void
  setLoading: (loading: boolean) => void
  addResume: (resume: Resume) => void
}

export const useResumeStore = create<ResumeState>()((set) => ({
  resumes: [],
  currentResume: null,
  isLoading: false,
  
  setResumes: (resumes) => set({ resumes }),
  setCurrentResume: (currentResume) => set({ currentResume }),
  setLoading: (isLoading) => set({ isLoading }),
  addResume: (resume) => set((state) => ({ resumes: [...state.resumes, resume] })),
}))

// DSA Problem Store
interface Problem {
  id: string
  title: string
  slug: string
  difficulty: string
  topics: string[]
}

interface DSAState {
  problems: Problem[]
  currentProblem: Problem | null
  isLoading: boolean
  
  setProblems: (problems: Problem[]) => void
  setCurrentProblem: (problem: Problem | null) => void
  setLoading: (loading: boolean) => void
}

export const useDSAStore = create<DSAState>()((set) => ({
  problems: [],
  currentProblem: null,
  isLoading: false,
  
  setProblems: (problems) => set({ problems }),
  setCurrentProblem: (currentProblem) => set({ currentProblem }),
  setLoading: (isLoading) => set({ isLoading }),
}))

// Analytics Store
interface SkillAssessment {
  skill: string
  score: number
  trend: 'up' | 'down' | 'stable'
}

interface AnalyticsState {
  overallScore: number
  technicalScore: number
  communicationScore: number
  problemSolvingScore: number
  skills: SkillAssessment[]
  recentInterviews: number
  weakAreas: string[]
  
  setAnalytics: (data: Partial<AnalyticsState>) => void
}

export const useAnalyticsStore = create<AnalyticsState>()((set) => ({
  overallScore: 0,
  technicalScore: 0,
  communicationScore: 0,
  problemSolvingScore: 0,
  skills: [],
  recentInterviews: 0,
  weakAreas: [],
  
  setAnalytics: (data) => set(data),
}))
