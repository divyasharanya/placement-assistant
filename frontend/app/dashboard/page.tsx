'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Brain, LogOut, FileText, Mic, Code2, Play, ChevronRight, BarChart3, Zap, Clock, Target, TrendingUp } from 'lucide-react'

interface UserStats {
  interviews_completed: number
  average_score: number
  problems_solved: number
  day_streak: number
}

interface Activity {
  id: string
  type: string
  title: string
  description: string
  timestamp: string
}

interface ResumeHistoryItem {
  id: string
  file_name: string
  ats_score: number
  skills_detected: string[]
  missing_skills: string[]
  strengths: string[]
  improvements: string[]
  suggestions: string[]
  uploaded_at: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [stats, setStats] = useState<UserStats>({
    interviews_completed: 0,
    average_score: 0,
    problems_solved: 0,
    day_streak: 0
  })
  const [activities, setActivities] = useState<Activity[]>([])
  const [resumeHistory, setResumeHistory] = useState<ResumeHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const resumeApiBase = process.env.NEXT_PUBLIC_RESUME_API_URL || 'http://localhost:8002'

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const userData = localStorage.getItem('user')
    
    if (!token || !userData) {
      router.push('/login')
      return
    }

    const parsedUser = JSON.parse(userData)
    setUser(parsedUser)
    
    // Fetch real data from API
    fetchProgress(parsedUser.id)
    fetchResumeHistory(parsedUser.id)
  }, [router])

  const fetchProgress = async (userId: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/progress/${userId}`)
      if (response.ok) {
        const data = await response.json()
        if (data.progress) {
          setStats({
            interviews_completed: data.progress.interviews_completed || 0,
            average_score: data.progress.average_score || 0,
            problems_solved: data.progress.problems_solved || 0,
            day_streak: data.progress.day_streak || 0
          })
        }
        if (data.recent_activities) {
          setActivities(data.recent_activities)
        }
      }
    } catch (error) {
      console.error('Failed to fetch progress:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchResumeHistory = async (userId: string) => {
    try {
      const response = await fetch(`${resumeApiBase}/api/resume-history?user_id=${userId}`)
      if (response.ok) {
        const data = await response.json()
        if (data.history) {
          setResumeHistory(data.history)
        }
      }
    } catch (error) {
      console.error('Failed to fetch resume history:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      {/* Header */}
      <header className="border-b border-[#1e1e2e] bg-[#0a0a0f]/90 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <span className="text-lg font-semibold text-white">InterviewMaster</span>
          </Link>

          <div className="flex items-center gap-4">
            <span className="text-gray-400 text-sm">Welcome, {user?.full_name || user?.email}</span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 text-gray-400 hover:text-white transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold text-white mb-8">Your Dashboard</h1>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <ActionCard
            icon={<Mic className="w-6 h-6 text-blue-400" />}
            title="Start Voice Interview"
            description="Practice with our AI interviewer using voice"
            href="/interview"
            color="blue"
          />
          <ActionCard
            icon={<FileText className="w-6 h-6 text-purple-400" />}
            title="Upload Resume"
            description="Get AI analysis and improvement tips"
            href="/resume"
            color="purple"
          />
          <ActionCard
            icon={<Code2 className="w-6 h-6 text-emerald-400" />}
            title="Practice Coding"
            description="Browse curated problems from LeetCode and CodeChef"
            href="/practice"
            color="emerald"
          />
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <StatCard value={stats.interviews_completed} label="Interviews Completed" />
          <StatCard value={stats.average_score} label="Average Score" suffix="%" />
          <StatCard value={stats.problems_solved} label="Problems Solved" />
          <StatCard value={stats.day_streak} label="Day Streak" />
        </div>

        {/* Resume Analysis History */}
        {resumeHistory && resumeHistory.length > 0 && (
          <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6 mb-12">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Resume Analysis History</h2>
              <Link href="/resume" className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1">
                Upload New <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
            
            <div className="space-y-4">
              {resumeHistory.slice(0, 5).map((resume) => (
                <div 
                  key={resume.id}
                  className="flex items-center justify-between p-4 bg-[#0a0a0f] rounded-lg border border-[#1e1e2e] hover:border-purple-500/30 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                      <FileText className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">{resume.file_name}</p>
                      <div className="flex items-center gap-3 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(resume.uploaded_at)}
                        </span>
                        {resume.skills_detected && resume.skills_detected.length > 0 && (
                          <span className="flex items-center gap-1">
                            <Target className="w-3 h-3" />
                            {resume.skills_detected.length} skills
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className={`text-2xl font-bold ${getScoreColor(resume.ats_score)}`}>
                        {resume.ats_score}%
                      </p>
                      <p className="text-gray-500 text-xs">ATS Score</p>
                    </div>
                    
                    {resume.improvements && resume.improvements.length > 0 && (
                      <div className="max-w-xs">
                        <p className="text-gray-400 text-xs mb-1">Quick improvement:</p>
                        <p className="text-gray-500 text-xs truncate">{resume.improvements[0]}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {resumeHistory.length > 5 && (
              <div className="mt-4 text-center">
                <p className="text-gray-500 text-sm">Showing 5 of {resumeHistory.length} analyses</p>
              </div>
            )}
          </div>
        )}

        {/* Recent Activity */}
        <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Recent Activity</h2>
          
          {activities && activities.length > 0 ? (
            <div className="space-y-4">
              {activities.map((activity) => (
                <ActivityItem
                  key={activity.id}
                  title={activity.title}
                  description={activity.description}
                  time={new Date(activity.timestamp).toLocaleDateString()}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <BarChart3 className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 mb-2">No activity yet</p>
              <p className="text-gray-500 text-sm">Start practicing to see your progress.</p>
            </div>
          )}

          {activities && activities.length > 0 && (
            <Link href="/history" className="mt-6 flex items-center gap-2 text-blue-400 hover:text-blue-300 text-sm">
              View all activity <ChevronRight className="w-4 h-4" />
            </Link>
          )}
        </div>
      </main>
    </div>
  )
}

function ActionCard({ icon, title, description, href, color }: {
  icon: React.ReactNode
  title: string
  description: string
  href: string
  color: string
}) {
  const colorClasses: Record<string, string> = {
    blue: 'hover:border-blue-500/50 bg-blue-500/5',
    purple: 'hover:border-purple-500/50 bg-purple-500/5',
    emerald: 'hover:border-emerald-500/50 bg-emerald-500/5',
  }

  return (
    <Link href={href}>
      <div className={`p-6 bg-[#13131a] border border-[#1e1e2e] rounded-xl transition-all hover:scale-[1.02] ${colorClasses[color]}`}>
        <div className="mb-4">{icon}</div>
        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-gray-400 text-sm">{description}</p>
      </div>
    </Link>
  )
}

function StatCard({ value, label, suffix }: { value: number; label: string; suffix?: string }) {
  return (
    <div className="p-6 bg-[#13131a] border border-[#1e1e2e] rounded-xl text-center">
      <div className="text-3xl font-bold text-white mb-1">
        {value}{suffix || ''}
      </div>
      <div className="text-gray-500 text-sm">{label}</div>
    </div>
  )
}

function ActivityItem({ title, description, time }: { title: string; description: string; time: string }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-[#1e1e2e] last:border-0">
      <div>
        <h4 className="text-white font-medium">{title}</h4>
        <p className="text-gray-400 text-sm">{description}</p>
      </div>
      <span className="text-gray-500 text-sm">{time}</span>
    </div>
  )
}
