'use client'

import Link from 'next/link'
import { 
  Mic, 
  FileText, 
  Code2, 
  TrendingUp, 
  MessageSquare, 
  Target,
  Zap,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Play,
  Star,
  Users,
  Calendar,
  BarChart3,
  Brain,
  Shield,
  Lightbulb,
  Zap as Lightning
} from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-[#1e1e2e] bg-[#0a0a0f]/90 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <span className="text-lg font-semibold text-white">InterviewMaster</span>
          </div>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-sm text-gray-400 hover:text-white transition-colors">How it Works</a>
            <a href="#pricing" className="text-sm text-gray-400 hover:text-white transition-colors">Pricing</a>
          </div>
          
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-gray-400 hover:text-white transition-colors">Log in</Link>
            <Link href="/register">
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors">
                Start Free
              </button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-blue-600/20 rounded-full blur-[120px]" />
          <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/15 rounded-full blur-[100px]" />
        </div>

        <div className="relative max-w-4xl mx-auto px-6 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600/10 border border-blue-600/30 rounded-full mb-8">
            <Zap className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-300">Now with GPT-4 powered interviews</span>
          </div>
          
          {/* Main Heading */}
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Master technical interviews
            <span className="block mt-2 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              with AI-powered practice
            </span>
          </h1>
          
          {/* Subtitle */}
          <p className="text-lg text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Practice realistic interviews with our AI interviewer. Get instant feedback on your answers, 
            track your progress, and land your dream job at top tech companies.
          </p>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <Link href="/register">
              <button className="px-8 py-3.5 bg-white text-black font-semibold rounded-lg hover:bg-gray-100 transition-colors inline-flex items-center gap-2">
                Start practicing free
                <ArrowRight className="w-4 h-4" />
              </button>
            </Link>
            <Link href="/demo">
              <button className="px-8 py-3.5 border border-gray-700 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors inline-flex items-center gap-2">
                <Play className="w-4 h-4" />
                Watch demo
              </button>
            </Link>
          </div>
          
          {/* Trust Indicators */}
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Free forever plan</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>5 minute setup</span>
            </div>
          </div>
        </div>
      </section>

      {/* Trusted By */}
      <section className="py-12 border-y border-[#1e1e2e]">
        <div className="max-w-6xl mx-auto px-6">
          <p className="text-center text-sm text-gray-500 mb-8">Trusted by engineers from</p>
          <div className="flex flex-wrap items-center justify-center gap-12 opacity-50 grayscale">
            {['Google', 'Meta', 'Amazon', 'Microsoft', 'Netflix', 'Stripe'].map((company) => (
              <span key={company} className="text-xl font-semibold text-gray-400">{company}</span>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-[#0d0d12]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Everything you need to ace your interview
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Our platform combines cutting-edge AI with proven interview preparation methods to help you succeed.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<Mic className="w-6 h-6 text-blue-400" />}
              iconBg="bg-blue-500/10"
              title="Voice Interviews"
              description="Practice with realistic voice conversations. Our AI adapts to your responses and asks follow-up questions."
            />
            <FeatureCard
              icon={<FileText className="w-6 h-6 text-purple-400" />}
              iconBg="bg-purple-500/10"
              title="Resume Analysis"
              description="Get ATS scoring and AI-powered suggestions to make your resume stand out to recruiters."
            />
            <FeatureCard
              icon={<Code2 className="w-6 h-6 text-emerald-400" />}
              iconBg="bg-emerald-500/10"
              title="Live Coding"
              description="Practice DSA problems in our built-in code editor with real-time feedback and test cases."
            />
            <FeatureCard
              icon={<TrendingUp className="w-6 h-6 text-amber-400" />}
              iconBg="bg-amber-500/10"
              title="Progress Tracking"
              description="Visualize your improvement over time with detailed analytics and skill assessments."
            />
            <FeatureCard
              icon={<MessageSquare className="w-6 h-6 text-pink-400" />}
              iconBg="bg-pink-500/10"
              title="Behavioral Prep"
              description="Master the STAR method with AI-guided practice for behavioral questions."
            />
            <FeatureCard
              icon={<Target className="w-6 h-6 text-cyan-400" />}
              iconBg="bg-cyan-500/10"
              title="Company-Specific"
              description="Prepare for specific companies with questions based on real interview data."
            />
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 border-y border-[#1e1e2e]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <StatCard value="50,000+" label="Interviews practiced" icon={<Calendar className="w-5 h-5 text-blue-400" />} />
            <StatCard value="94%" label="Success rate" icon={<Star className="w-5 h-5 text-purple-400" />} />
            <StatCard value="4.9/5" label="User rating" icon={<Users className="w-5 h-5 text-emerald-400" />} />
            <StatCard value="500+" label="Coding problems" icon={<BarChart3 className="w-5 h-5 text-amber-400" />} />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 bg-[#0d0d12]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Get started in minutes
            </h2>
            <p className="text-gray-400">
              Three simple steps to improve your interview skills
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <StepCard
              step="01"
              title="Upload your resume"
              description="Connect your LinkedIn or upload your resume. Our AI analyzes your background and target role."
            />
            <StepCard
              step="02"
              title="Start practicing"
              description="Choose your focus areas and difficulty. Practice with voice or text-based AI interviews."
            />
            <StepCard
              step="03"
              title="Get instant feedback"
              description="Receive detailed feedback on technical skills, communication, and problem-solving."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900/30 via-purple-900/30 to-pink-900/30" />
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-[400px] h-[400px] bg-blue-600/20 rounded-full blur-[100px]" />
          <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-purple-600/20 rounded-full blur-[100px]" />
        </div>
        
        <div className="relative max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to land your dream job?
          </h2>
          <p className="text-gray-400 mb-8 text-lg">
            Join thousands of engineers who have improved their interview skills and landed offers from top companies.
          </p>
          <Link href="/register">
            <button className="px-10 py-4 bg-white text-black font-semibold text-lg rounded-lg hover:bg-gray-100 transition-colors inline-flex items-center gap-2">
              Start practicing for free
              <ArrowRight className="w-5 h-5" />
            </button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#1e1e2e] py-12 bg-[#0a0a0f]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Brain className="w-3 h-3 text-white" />
              </div>
              <span className="text-sm font-medium text-white">InterviewMaster</span>
            </div>
            
            <div className="flex items-center gap-8 text-sm text-gray-500">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
              <a href="#" className="hover:text-white transition-colors">Twitter</a>
              <a href="#" className="hover:text-white transition-colors">GitHub</a>
            </div>
          </div>
          
          <div className="mt-8 text-center text-sm text-gray-600">
            © 2024 InterviewMaster. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}

// Feature Card Component
function FeatureCard({ icon, iconBg, title, description }: { 
  icon: React.ReactNode; 
  iconBg: string; 
  title: string; 
  description: string; 
}) {
  return (
    <div className="p-6 bg-[#13131a] border border-[#1e1e2e] rounded-xl hover:border-blue-600/50 hover:bg-[#18181f] transition-all duration-300">
      <div className={`w-12 h-12 ${iconBg} rounded-lg flex items-center justify-center mb-4`}>
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
    </div>
  )
}

// Step Card Component
function StepCard({ step, title, description }: { step: string; title: string; description: string }) {
  return (
    <div className="relative p-6 bg-[#13131a] border border-[#1e1e2e] rounded-xl">
      <div className="text-6xl font-bold text-[#1e1e2e] mb-4">{step}</div>
      <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  )
}

// Stat Card Component
function StatCard({ value, label, icon }: { value: string; label: string; icon: React.ReactNode }) {
  return (
    <div className="text-center p-6">
      <div className="flex items-center justify-center gap-2 mb-3">
        {icon}
      </div>
      <div className="text-3xl md:text-4xl font-bold text-white mb-1">{value}</div>
      <div className="text-gray-500 text-sm">{label}</div>
    </div>
  )
}
