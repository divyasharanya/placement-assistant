'use client'

import { useState, useRef } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { 
  Brain, 
  Upload, 
  FileText, 
  Loader2, 
  CheckCircle, 
  XCircle,
  ArrowLeft,
  TrendingUp,
  Target,
  Lightbulb,
  AlertCircle,
  History
} from 'lucide-react'

interface ResumeAnalysis {
  ats_score: number
  skills_detected: string[]
  missing_skills: string[]
  strengths: string[]
  improvements: string[]
  suggestions: string[]
  professional_feedback?: string
  analysis: string
}

function normalizeResumeAnalysis(payload: any): ResumeAnalysis {
  const source = payload?.analysis && typeof payload.analysis === 'object' ? payload.analysis : payload
  const asArray = (value: any): string[] => Array.isArray(value) ? value.filter((x) => typeof x === 'string') : []
  const toNumber = (value: any): number => {
    const n = Number(value)
    return Number.isFinite(n) ? Math.max(0, Math.min(100, Math.round(n))) : 0
  }

  return {
    ats_score: toNumber(source?.ats_score ?? source?.atsScore ?? source?.score),
    skills_detected: asArray(source?.skills_detected ?? source?.skillsDetected ?? source?.keywords_found),
    missing_skills: asArray(source?.missing_skills ?? source?.missingSkills ?? source?.missing_keywords),
    strengths: asArray(source?.strengths),
    improvements: asArray(source?.improvements),
    suggestions: asArray(source?.suggestions),
    professional_feedback: source?.professional_feedback ?? source?.professionalFeedback ?? source?.overall_feedback ?? '',
    analysis: source?.analysis ?? source?.professional_feedback ?? source?.professionalFeedback ?? source?.overall_feedback ?? ''
  }
}

export default function ResumePage() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null)
  const [error, setError] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const resumeApiBase = process.env.NEXT_PUBLIC_RESUME_API_URL || 'http://localhost:8002'

  const user = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('user') || '{}') : {}

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      // Validate file type - Only allow PDF, DOC, DOCX
      const validTypes = ['.pdf', '.doc', '.docx']
      const extension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase()
      
      if (!validTypes.includes(extension)) {
        setError('Please upload a valid resume file (PDF, DOC, or DOCX only)')
        return
      }

      // Validate file size (max 5MB)
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB')
        return
      }

      setFile(selectedFile)
      setError('')
      setAnalysis(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setIsLoading(true)
    setError('')
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('resume', file)
      if (user.id) {
        formData.append('user_id', user.id)
      }

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + 10
        })
      }, 200)

      const response = await fetch(`${resumeApiBase}/api/upload-resume`, {
        method: 'POST',
        body: formData
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to analyze resume')
      }

      setAnalysis(normalizeResumeAnalysis(data))
    } catch (err: any) {
      const message = err?.message === 'Failed to fetch'
        ? `Cannot reach resume service at ${resumeApiBase}. Ensure backend/resume-service is running and CORS allows your frontend origin.`
        : (err.message || 'Failed to analyze resume. Please try again.')
      setError(message)
    } finally {
      setIsLoading(false)
      setTimeout(() => setUploadProgress(0), 500)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Needs Work'
    return 'Poor'
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      {/* Header */}
      <header className="border-b border-[#1e1e2e] bg-[#0a0a0f]/90 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-gray-400 hover:text-white">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Brain className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-semibold text-white">Resume Analysis</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-12">
        {!analysis ? (
          // Upload Section
          <div className="space-y-8">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-white mb-4">Upload Your Resume</h1>
              <p className="text-gray-400 max-w-md mx-auto">
                Upload your resume in PDF, DOC, or DOCX format. Our AI will analyze it and provide professional feedback.
              </p>
            </div>

            {/* Upload Area */}
            <div 
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
                file 
                  ? 'border-blue-500 bg-blue-500/10' 
                  : 'border-[#1e1e2e] hover:border-blue-500/50 hover:bg-[#13131a]'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileSelect}
                className="hidden"
              />

              {file ? (
                <div className="flex flex-col items-center">
                  <FileText className="w-16 h-16 text-blue-400 mb-4" />
                  <p className="text-white font-medium mb-2">{file.name}</p>
                  <p className="text-gray-500 text-sm">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation()
                      setFile(null)
                    }}
                    className="mt-4 text-sm text-red-400 hover:text-red-300"
                  >
                    Remove file
                  </button>
                </div>
              ) : (
                <>
                  <Upload className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                  <p className="text-white font-medium mb-2">
                    Click to upload your resume
                  </p>
                  <p className="text-gray-500 text-sm">
                    PDF, DOC, or DOCX (max 5MB)
                  </p>
                </>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <p>{error}</p>
              </div>
            )}

            {/* Progress Bar */}
            {isLoading && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-gray-400">
                  <span>Analyzing resume...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!file || isLoading}
              className="w-full py-4 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  Analyze Resume
                </>
              )}
            </button>
          </div>
        ) : (
          // Results Section
          <div className="space-y-8">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-white mb-4">Resume Analysis Complete</h1>
              <p className="text-gray-400">Here's your professional resume feedback</p>
            </div>

            {/* ATS Score */}
            <div className="bg-[#13131a] border border-[#1e1e2e] rounded-2xl p-8 text-center">
              <h2 className="text-lg text-gray-400 mb-4">ATS Score</h2>
              <div className="flex items-center justify-center gap-4">
                <div className={`text-7xl font-bold ${getScoreColor(analysis.ats_score)}`}>
                  {analysis.ats_score}%
                </div>
                <div className={`text-xl font-medium ${getScoreColor(analysis.ats_score)}`}>
                  {getScoreLabel(analysis.ats_score)}
                </div>
              </div>
              <p className="text-gray-500 text-sm mt-4">
                This score estimates how well your resume would perform in Applicant Tracking Systems
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Skills Detected */}
              <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <CheckCircle className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-lg font-semibold text-white">Skills Detected</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {analysis.skills_detected && analysis.skills_detected.map((skill, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-emerald-500/10 text-emerald-400 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                  {(!analysis.skills_detected || analysis.skills_detected.length === 0) && (
                    <p className="text-gray-500 text-sm">No skills detected</p>
                  )}
                </div>
              </div>

              {/* Missing Skills */}
              <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Target className="w-5 h-5 text-amber-400" />
                  <h3 className="text-lg font-semibold text-white">Missing Skills</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {analysis.missing_skills && analysis.missing_skills.map((skill, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-amber-500/10 text-amber-400 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                  {(!analysis.missing_skills || analysis.missing_skills.length === 0) && (
                    <p className="text-gray-500 text-sm">No missing skills identified</p>
                  )}
                </div>
              </div>
            </div>

            {/* Strengths */}
            {analysis.strengths && analysis.strengths.length > 0 && (
              <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <CheckCircle className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-lg font-semibold text-white">Resume Strengths</h3>
                </div>
                <ul className="space-y-2">
                  {analysis.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start gap-3 text-gray-300">
                      <span className="text-emerald-400 mt-1">✓</span>
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Improvements */}
            {analysis.improvements && analysis.improvements.length > 0 && (
              <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-5 h-5 text-amber-400" />
                  <h3 className="text-lg font-semibold text-white">Areas for Improvement</h3>
                </div>
                <ul className="space-y-2">
                  {analysis.improvements.map((improvement, index) => (
                    <li key={index} className="flex items-start gap-3 text-gray-300">
                      <span className="text-amber-400 mt-1">•</span>
                      <span>{improvement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Suggestions */}
            {analysis.suggestions && analysis.suggestions.length > 0 && (
              <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Lightbulb className="w-5 h-5 text-blue-400" />
                  <h3 className="text-lg font-semibold text-white">Suggestions to Improve</h3>
                </div>
                <ul className="space-y-3">
                  {analysis.suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start gap-3 text-gray-300">
                      <span className="text-blue-400 mt-1">-</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Professional Analysis */}
            <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">Professional Feedback</h3>
              </div>
              <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                {analysis.analysis}
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => {
                  setFile(null)
                  setAnalysis(null)
                }}
                className="flex-1 py-4 border border-[#1e1e2e] text-white font-semibold rounded-xl hover:bg-[#1e1e2e] transition-colors"
              >
                Upload Another Resume
              </button>
              <button
                onClick={() => router.push('/dashboard')}
                className="flex-1 py-4 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-colors"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
