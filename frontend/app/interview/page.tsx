// 'use client'

// import { useEffect, useState, useRef } from 'react'
// import Link from 'next/link'
// import { useRouter } from 'next/navigation'
// import { 
//   Brain, 
//   Mic, 
//   MicOff, 
//   Volume2, 
//   VolumeX, 
//   Loader2, 
//   ArrowLeft,
//   MessageSquare,
//   CheckCircle
// } from 'lucide-react'

// // Type declarations for Web Speech API
// interface SpeechRecognitionEvent extends Event {
//   results: SpeechRecognitionResultList
//   resultIndex: number
// }

// interface SpeechRecognitionErrorEvent extends Event {
//   error: string
// }

// declare global {
//   interface Window {
//     SpeechRecognition: new () => SpeechRecognition
//     webkitSpeechRecognition: new () => SpeechRecognition
//   }
//   interface SpeechRecognition extends EventTarget {
//     continuous: boolean
//     interimResults: boolean
//     lang: string
//     onresult: ((event: SpeechRecognitionEvent) => void) | null
//     onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
//     onend: (() => void) | null
//     onstart: (() => void) | null
//     start: () => void
//     stop: () => void
//     abort: () => void
//   }
// }

// interface Message {
//   id: number
//   role: 'user' | 'ai'
//   content: string
//   timestamp: Date
//   score?: number
//   strengths?: string[]
//   improvements?: string[]
//   stage?: string
// }

// interface Evaluation {
//   overall_score: number
//   communication_score: number
//   technical_score: number
//   total_questions: number
//   strengths: string[]
//   improvements: string[]
//   category_scores: Record<string, number>
//   suggestions: string[]
// }

// export default function InterviewPage() {
//   const router = useRouter()
//   const [isRecording, setIsRecording] = useState(false)
//   const [isSpeaking, setIsSpeaking] = useState(false)
//   const [isLoading, setIsLoading] = useState(false)
//   const [sessionId, setSessionId] = useState<string | null>(null)
//   const [messages, setMessages] = useState<Message[]>([])
//   const [currentAnswer, setCurrentAnswer] = useState('')
//   const [transcript, setTranscript] = useState('')
//   const [questionNumber, setQuestionNumber] = useState(1)
//   const [isInterviewComplete, setIsInterviewComplete] = useState(false)
//   const [finalScore, setFinalScore] = useState<number | null>(null)
//   const [currentStage, setCurrentStage] = useState<string>('introduction')
//   const [stageLabel, setStageLabel] = useState<string>('Introduction')
//   const [evaluation, setEvaluation] = useState<Evaluation | null>(null)
//   const [hasSpokenCurrentQuestion, setHasSpokenCurrentQuestion] = useState(false)
//   const [askedQuestions, setAskedQuestions] = useState<string[]>([])
//   const [conversationHistory, setConversationHistory] = useState<{role: string, content: string}[]>([])
//   const [error, setError] = useState<string | null>(null)

//   const recognitionRef = useRef<SpeechRecognition | null>(null)
//   const synthesisRef = useRef<SpeechSynthesisUtterance | null>(null)
//   const messagesEndRef = useRef<HTMLDivElement>(null)
//   const isProcessingRef = useRef(false)

//   const user = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('user') || '{}') : {}

//   // API base URL - use correct port
//   const API_URL = 'http://localhost:8000'

//   // Initialize speech recognition
//   useEffect(() => {
//     if (typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
//       const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
//       recognitionRef.current = new SpeechRecognition()
//       recognitionRef.current.lang = 'en-US'
//       recognitionRef.current.continuous = false
//       recognitionRef.current.interimResults = true

//       recognitionRef.current.onresult = (event) => {
//         let finalTranscript = ''
//         let interimTranscript = ''
        
//         for (let i = event.resultIndex; i < event.results.length; i++) {
//           const result = event.results[i]
//           if (result.isFinal) {
//             finalTranscript += result[0].transcript
//           } else {
//             interimTranscript += result[0].transcript
//           }
//         }
        
//         if (finalTranscript && finalTranscript.trim().length > 0) {
//           setIsRecording(false)
//           setCurrentAnswer(finalTranscript)
//           setTranscript(finalTranscript)
//           if (!isProcessingRef.current) {
//             submitAnswer(finalTranscript)
//           }
//         } else if (interimTranscript) {
//           setTranscript(interimTranscript)
//         }
//       }

//       recognitionRef.current.onerror = (event) => {
//         console.error('Speech recognition error:', event.error)
//         setIsRecording(false)
//         setError(`Speech error: ${event.error}`)
//         setTimeout(() => setError(null), 3000)
//       }

//       recognitionRef.current.onend = () => {
//         setIsRecording(false)
//       }
//     }

//     return () => {
//       if (recognitionRef.current) {
//         recognitionRef.current.stop()
//       }
//       if (typeof window !== 'undefined' && window.speechSynthesis) {
//         window.speechSynthesis.cancel()
//       }
//     }
//   }, [])

//   // Scroll to bottom of messages
//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
//   }, [messages])

//   // Start interview
//   const startInterview = async () => {
//     setIsLoading(true)
//     setError(null)
//     try {
//       const response = await fetch(`${API_URL}/api/start-interview`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ 
//           user_id: user.id,
//           focus_areas: ['dsa', 'oop', 'system_design', 'behavioral']
//         })
//       })

//       if (!response.ok) {
//         throw new Error('Failed to start interview')
//       }

//       const data = await response.json()
//       setSessionId(data.session_id)
//       setQuestionNumber(data.question_number || 1)
//       if (data.stage) setCurrentStage(data.stage)
//       if (data.stage_label) setStageLabel(data.stage_label)
      
//       // Initialize conversation state
//       const question = data.question || data.next_question
//       setAskedQuestions([question])
//       setConversationHistory([{ role: 'ai', content: question }])
//       setHasSpokenCurrentQuestion(false)

//       const aiMessage: Message = {
//         id: 1,
//         role: 'ai',
//         content: question,
//         timestamp: new Date()
//       }
//       setMessages([aiMessage])

//       // Speak the question
//       speakText(question)
//     } catch (error) {
//       console.error('Failed to start interview:', error)
//       setError('Failed to start interview. Please try again.')
//       setTimeout(() => setError(null), 3000)
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   // Toggle recording
//   const toggleRecording = () => {
//     if (isRecording) {
//       recognitionRef.current?.stop()
//     } else {
//       setTranscript('')
//       recognitionRef.current?.start()
//       setIsRecording(true)
//     }
//   }

//   // Speak text using TTS
//   const speakText = (text: string) => {
//     if ('speechSynthesis' in window) {
//       window.speechSynthesis.cancel()

//       const utterance = new SpeechSynthesisUtterance(text)
//       utterance.rate = 0.9
//       utterance.pitch = 1
//       utterance.volume = 1

//       const voices = window.speechSynthesis.getVoices()
//       const englishVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google')) 
//         || voices.find(v => v.lang.startsWith('en'))
      
//       if (englishVoice) {
//         utterance.voice = englishVoice
//       }

//       utterance.onstart = () => {
//         setIsSpeaking(true)
//         setHasSpokenCurrentQuestion(true)
//       }
//       utterance.onend = () => setIsSpeaking(false)
//       utterance.onerror = () => setIsSpeaking(false)

//       window.speechSynthesis.speak(utterance)
//       synthesisRef.current = utterance
//     }
//   }

//   // Stop speaking
//   const stopSpeaking = () => {
//     if ('speechSynthesis' in window) {
//       window.speechSynthesis.cancel()
//       setIsSpeaking(false)
//     }
//   }

//   // Submit answer
//   const submitAnswer = async (answerText?: string) => {
//     if (isProcessingRef.current) return
    
//     const textToSubmit = answerText || currentAnswer
//     if (!textToSubmit.trim() || !sessionId || isLoading) return

//     isProcessingRef.current = true
//     setIsLoading(true)
    
//     // Add user's answer to messages
//     const userMessage: Message = {
//       id: messages.length + 1,
//       role: 'user',
//       content: textToSubmit,
//       timestamp: new Date()
//     }
//     setMessages(prev => [...prev, userMessage])
//     setConversationHistory(prev => [...prev, { role: 'user', content: textToSubmit }])

//     try {
//       const response = await fetch(`${API_URL}/api/answer`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           session_id: sessionId,
//           user_answer: textToSubmit,
//           question_id: questionNumber
//         })
//       })

//       if (!response.ok) {
//         throw new Error('Failed to submit answer')
//       }

//       const data = await response.json()

//       if (data.interview_completed) {
//         setIsInterviewComplete(true)
//         setFinalScore(data.final_score)

//         const completeMessage: Message = {
//           id: messages.length + 2,
//           role: 'ai',
//           content: `Interview completed! Your final score is ${data.final_score}%. Great job! Keep practicing to improve your skills.`,
//           timestamp: new Date(),
//           score: data.final_score
//         }
//         setMessages(prev => [...prev, completeMessage])
//       } else {
//         // Add AI analysis
//         const analysisContent = data.analysis?.strengths?.length > 0 
//           ? `Great answer! Score: ${data.analysis.score}%\n\nStrengths: ${data.analysis.strengths?.join(', ')}\n\nAreas to improve: ${data.analysis.improvements?.join(', ')}`
//           : 'Thank you for your answer. Let me ask you another question.'

//         const analysisMessage: Message = {
//           id: messages.length + 2,
//           role: 'ai',
//           content: analysisContent,
//           timestamp: new Date(),
//           score: data.analysis?.score,
//           strengths: data.analysis?.strengths,
//           improvements: data.analysis?.improvements
//         }
//         setMessages(prev => [...prev, analysisMessage])

//         // Add next question
//         if (data.next_question) {
//           const nextQuestionMessage: Message = {
//             id: messages.length + 3,
//             role: 'ai',
//             content: data.next_question,
//             timestamp: new Date()
//           }
//           setMessages(prev => [...prev, nextQuestionMessage])
//           setQuestionNumber(data.question_number)
//           if (data.current_stage) setCurrentStage(data.current_stage)
//           if (data.stage_label) setStageLabel(data.stage_label)
//           setHasSpokenCurrentQuestion(false)
          
//           // Update conversation state
//           setAskedQuestions(prev => [...prev, data.next_question])
//           setConversationHistory(prev => [...prev, { role: 'ai', content: data.next_question }])
          
//           // Speak next question
//           setTimeout(() => speakText(data.next_question), 1000)
//         }
//       }

//       setCurrentAnswer('')
//       setTranscript('')
//     } catch (error) {
//       console.error('Failed to submit answer:', error)
//       setError('Failed to submit answer. Please try again.')
//       setTimeout(() => setError(null), 3000)
//     } finally {
//       setIsLoading(false)
//       isProcessingRef.current = false
//     }
//   }

//   // End interview and get evaluation
//   const endInterview = async () => {
//     stopSpeaking()
//     if (!sessionId) {
//       router.push('/dashboard')
//       return
//     }
    
//     setIsLoading(true)
//     try {
//       const response = await fetch(`${API_URL}/api/end-interview`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ session_id: sessionId })
//       })
      
//       const data = await response.json()
      
//       if (data.evaluation) {
//         setEvaluation(data.evaluation)
//         setFinalScore(data.evaluation.overall_score)
//       }
//       setIsInterviewComplete(true)
//     } catch (error) {
//       console.error('Failed to end interview:', error)
//       router.push('/dashboard')
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   return (
//     <div className="min-h-screen bg-[#0a0a0f]">
//       {/* Header */}
//       <header className="border-b border-[#1e1e2e] bg-[#0a0a0f]/90 backdrop-blur-xl">
//         <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
//           <div className="flex items-center gap-4">
//             <Link href="/dashboard" className="text-gray-400 hover:text-white">
//               <ArrowLeft className="w-5 h-5" />
//             </Link>
//             <div className="flex items-center gap-2">
//               <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
//                 <Brain className="w-4 h-4 text-white" />
//               </div>
//               <span className="text-lg font-semibold text-white">AI Interview</span>
//             </div>
//           </div>

//           <div className="flex items-center gap-4">
//             {!isInterviewComplete && sessionId && (
//               <>
//                 <span className="text-blue-400 text-sm font-medium">{stageLabel}</span>
//                 <span className="text-gray-500">•</span>
//                 <span className="text-gray-400 text-sm">Question {questionNumber}</span>
//               </>
//             )}
//             {isSpeaking && (
//               <span className="flex items-center gap-2 text-blue-400 text-sm">
//                 <Volume2 className="w-4 h-4 animate-pulse" /> AI Speaking...
//               </span>
//             )}
//             {sessionId && !isInterviewComplete && (
//               <button
//                 onClick={endInterview}
//                 className="px-3 py-1 text-sm bg-red-600/20 text-red-400 hover:bg-red-600/30 rounded-lg transition-colors"
//               >
//                 End Interview
//               </button>
//             )}
//           </div>
//         </div>
//       </header>

//       {/* Main Content */}
//       <main className="max-w-4xl mx-auto px-6 py-8">
//         {/* Error message */}
//         {error && (
//           <div className="mb-4 p-4 bg-red-600/20 border border-red-600/50 rounded-lg text-red-400 text-sm">
//             {error}
//           </div>
//         )}

//         {!sessionId ? (
//           // Start Interview Screen
//           <div className="text-center py-20">
//             <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mx-auto mb-6">
//               <Mic className="w-10 h-10 text-white" />
//             </div>
//             <h1 className="text-3xl font-bold text-white mb-4">Voice Mock Interview</h1>
//             <p className="text-gray-400 mb-8 max-w-md mx-auto">
//               Practice technical interviews with our AI interviewer. 
//               You'll answer questions about DSA, OOP, System Design, and Behavioral topics.
//             </p>
            
//             <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6 mb-8 text-left max-w-md mx-auto">
//               <h3 className="text-white font-medium mb-3">How it works:</h3>
//               <ul className="space-y-2 text-gray-400 text-sm">
//                 <li className="flex items-center gap-2">
//                   <Mic className="w-4 h-4 text-blue-400" /> Click to start speaking
//                 </li>
//                 <li className="flex items-center gap-2">
//                   <Volume2 className="w-4 h-4 text-blue-400" /> AI will ask questions aloud
//                 </li>
//                 <li className="flex items-center gap-2">
//                   <MessageSquare className="w-4 h-4 text-blue-400" /> Get instant feedback
//                 </li>
//               </ul>
//             </div>

//             <button
//               onClick={startInterview}
//               disabled={isLoading}
//               className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 inline-flex items-center gap-2"
//             >
//               {isLoading ? (
//                 <>
//                   <Loader2 className="w-5 h-5 animate-spin" />
//                   Starting...
//                 </>
//               ) : (
//                 <>
//                   <Mic className="w-5 h-5" />
//                   Start Interview
//                 </>
//               )}
//             </button>
//           </div>
//         ) : isInterviewComplete ? (
//           // Interview Complete Screen with Evaluation Report
//           <div className="max-w-2xl mx-auto">
//             <div className="text-center mb-8">
//               <div className="w-24 h-24 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center mx-auto mb-6">
//                 <CheckCircle className="w-12 h-12 text-white" />
//               </div>
//               <h1 className="text-3xl font-bold text-white mb-2">Interview Complete!</h1>
//               <p className="text-gray-400">Here's your detailed performance report</p>
//             </div>

//             {evaluation ? (
//               <div className="space-y-6">
//                 {/* Overall Score */}
//                 <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
//                   <div className="text-center mb-4">
//                     <div className="text-5xl font-bold text-gradient bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-2">
//                       {evaluation.overall_score}%
//                     </div>
//                     <div className="text-gray-400 text-sm">Overall Score</div>
//                   </div>
//                   <div className="grid grid-cols-2 gap-4">
//                     <div className="bg-[#0a0a0f] rounded-lg p-4 text-center">
//                       <div className="text-2xl font-bold text-white">{evaluation.communication_score}%</div>
//                       <div className="text-gray-500 text-xs">Communication</div>
//                     </div>
//                     <div className="bg-[#0a0a0f] rounded-lg p-4 text-center">
//                       <div className="text-2xl font-bold text-white">{evaluation.technical_score}%</div>
//                       <div className="text-gray-500 text-xs">Technical</div>
//                     </div>
//                   </div>
//                 </div>

//                 {/* Strengths */}
//                 <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
//                   <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
//                     <CheckCircle className="w-5 h-5 text-green-400" /> Your Strengths
//                   </h3>
//                   <ul className="space-y-2">
//                     {evaluation.strengths?.map((strength, i) => (
//                       <li key={i} className="text-gray-300 text-sm flex items-center gap-2">
//                         <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
//                         {strength}
//                       </li>
//                     ))}
//                   </ul>
//                 </div>

//                 {/* Areas for Improvement */}
//                 <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
//                   <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
//                     <Brain className="w-5 h-5 text-yellow-400" /> Areas to Improve
//                   </h3>
//                   <ul className="space-y-2">
//                     {evaluation.improvements?.map((imp, i) => (
//                       <li key={i} className="text-gray-300 text-sm flex items-center gap-2">
//                         <span className="w-1.5 h-1.5 rounded-full bg-yellow-400"></span>
//                         {imp}
//                       </li>
//                     ))}
//                   </ul>
//                 </div>

//                 {/* Suggestions */}
//                 <div className="bg-[#13131a] border border-[#1e1e2e] rounded-xl p-6">
//                   <h3 className="text-white font-semibold mb-3">Suggestions</h3>
//                   <ul className="space-y-2">
//                     {evaluation.suggestions?.map((suggestion, i) => (
//                       <li key={i} className="text-gray-300 text-sm flex items-center gap-2">
//                         <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
//                         {suggestion}
//                       </li>
//                     ))}
//                   </ul>
//                 </div>

//                 <div className="flex gap-4">
//                   <Link href="/dashboard" className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg text-center transition-colors">
//                     Back to Dashboard
//                   </Link>
//                   <button onClick={startInterview} className="flex-1 py-3 bg-[#1e1e2e] hover:bg-[#2a2a3e] text-white font-semibold rounded-lg transition-colors">
//                     Start New Interview
//                   </button>
//                 </div>
//               </div>
//             ) : finalScore !== null ? (
//               <div className="text-center">
//                 <div className="text-5xl font-bold text-white mb-4">{finalScore}%</div>
//                 <p className="text-gray-400 mb-8">Final Score</p>
//                 <div className="flex gap-4">
//                   <Link href="/dashboard" className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg text-center transition-colors">
//                     Back to Dashboard
//                   </Link>
//                   <button onClick={startInterview} className="flex-1 py-3 bg-[#1e1e2e] hover:bg-[#2a2a3e] text-white font-semibold rounded-lg transition-colors">
//                     Start New Interview
//                   </button>
//                 </div>
//               </div>
//             ) : (
//               <div className="flex gap-4">
//                 <Link href="/dashboard" className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg text-center transition-colors">
//                   Back to Dashboard
//                 </Link>
//               </div>
//             )}
//           </div>
//         ) : (
//           // Active Interview Screen
//           <div className="space-y-6">
//             {/* Messages */}
//             <div className="space-y-4">
//               {messages.map((message) => (
//                 <div
//                   key={message.id}
//                   className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
//                 >
//                   <div
//                     className={`max-w-[80%] rounded-xl p-4 ${
//                       message.role === 'user'
//                         ? 'bg-blue-600 text-white'
//                         : 'bg-[#13131a] border border-[#1e1e2e] text-gray-100'
//                     }`}
//                   >
//                     <p className="whitespace-pre-wrap">{message.content}</p>
//                     {message.score !== undefined && (
//                       <div className="mt-2 pt-2 border-t border-white/20 text-sm">
//                         <span className="font-medium">Score: {message.score}%</span>
//                       </div>
//                     )}
//                   </div>
//                 </div>
//               ))}
//               <div ref={messagesEndRef} />
//             </div>

//             {/* Recording Controls */}
//             <div className="fixed bottom-0 left-0 right-0 bg-[#0a0a0f] border-t border-[#1e1e2e] p-4">
//               <div className="max-w-4xl mx-auto flex items-center justify-center gap-4">
//                 {/* Transcript Display */}
//                 <div className="flex-1 bg-[#13131a] border border-[#1e1e2e] rounded-lg px-4 py-2 text-gray-400 text-sm min-h-[44px]">
//                   {transcript || (isRecording ? 'Listening...' : 'Click the microphone and speak your answer')}
//                 </div>

//                 {/* Mic Button */}
//                 <button
//                   onClick={toggleRecording}
//                   disabled={isLoading}
//                   className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${
//                     isRecording 
//                       ? 'bg-red-600 hover:bg-red-500 animate-pulse' 
//                       : 'bg-blue-600 hover:bg-blue-500'
//                   } disabled:opacity-50`}
//                 >
//                   {isLoading ? (
//                     <Loader2 className="w-6 h-6 text-white animate-spin" />
//                   ) : isRecording ? (
//                     <MicOff className="w-6 h-6 text-white" />
//                   ) : (
//                     <Mic className="w-6 h-6 text-white" />
//                   )}
//                 </button>

//                 {/* Stop Speaking Button */}
//                 {isSpeaking && (
//                   <button
//                     onClick={stopSpeaking}
//                     className="w-12 h-12 rounded-full bg-[#1e1e2e] hover:bg-[#2a2a3e] flex items-center justify-center"
//                   >
//                     <VolumeX className="w-5 h-5 text-white" />
//                   </button>
//                 )}
//               </div>
//             </div>
//           </div>
//         )}
//       </main>
//     </div>
//   )
// }
'use client'

import { useEffect, useState, useRef, useCallback } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  Brain, Mic, MicOff, Volume2, VolumeX,
  Loader2, ArrowLeft, MessageSquare, CheckCircle,
  ChevronRight, Clock, BarChart2, Star, AlertCircle,
} from 'lucide-react'

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList
  resultIndex: number
}
interface SpeechRecognitionErrorEvent extends Event {
  error: string
}
declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition
    webkitSpeechRecognition: new () => SpeechRecognition
  }
  interface SpeechRecognition extends EventTarget {
    continuous: boolean
    interimResults: boolean
    lang: string
    onresult: ((event: SpeechRecognitionEvent) => void) | null
    onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
    onend: (() => void) | null
    onstart: (() => void) | null
    start: () => void
    stop: () => void
    abort: () => void
  }
}

interface Domain { id: string; label: string; icon: string }
interface Message {
  id: number; role: 'user' | 'ai'; content: string; timestamp: Date
  score?: number; strengths?: string[]; improvements?: string[]; type?: string
}
interface Analysis {
  score: number; strengths: string[]; improvements: string[]; ai_feedback: string
  technical_accuracy: number; communication: number; problem_solving: number
}
interface PerQuestion {
  question_number: number; question: string; type: string; score: number
  feedback: string; strengths: string[]; improvements: string[]
  points_covered: string[]; points_missed: string[]
}
interface Evaluation {
  overall_score: number; communication_score: number; technical_score: number
  problem_solving: number; total_questions: number
  strengths: string[]; improvements: string[]; suggestions: string[]
  category_scores: Record<string, number>
  per_question: PerQuestion[]; grade: string
}

const DOMAINS: Domain[] = [
  { id: 'backend',       label: 'Backend Engineering',          icon: '⚙️' },
  { id: 'frontend',      label: 'Frontend Development',         icon: '🎨' },
  { id: 'fullstack',     label: 'Full Stack Development',       icon: '🔗' },
  { id: 'data_science',  label: 'Data Science & ML',            icon: '📊' },
  { id: 'devops',        label: 'DevOps & Cloud',               icon: '☁️' },
  { id: 'system_design', label: 'System Design',                icon: '🏗️' },
  { id: 'mobile',        label: 'Mobile Development',           icon: '📱' },
  { id: 'security',      label: 'Cybersecurity',                icon: '🔒' },
  { id: 'database',      label: 'Database Engineering',         icon: '🗄️' },
  { id: 'general_swe',   label: 'General Software Engineering', icon: '💻' },
  { id: 'product',       label: 'Product Management',           icon: '📋' },
  { id: 'behavioral',    label: 'Behavioral / HR Round',        icon: '🤝' },
  { id: 'dsa',           label: 'DSA & Algorithms',             icon: '🧮' },
]

const DIFFICULTIES = ['easy', 'medium', 'hard'] as const
type Difficulty = typeof DIFFICULTIES[number]
const API_URL = 'http://localhost:8000'

function scoreBg(score: number) {
  if (score >= 75) return 'bg-emerald-500/10 text-emerald-400'
  if (score >= 50) return 'bg-amber-500/10 text-amber-400'
  return 'bg-red-500/10 text-red-400'
}

export default function InterviewPage() {
  const router = useRouter()

  const [screen, setScreen]         = useState<'setup' | 'interview' | 'results'>('setup')
  const [selectedDomain, setDomain] = useState<Domain | null>(null)
  const [difficulty, setDifficulty] = useState<Difficulty>('medium')
  const [numQuestions, setNum]      = useState(5)
  const [resumeText, setResumeText] = useState('')

  const [sessionId, setSessionId]   = useState<string | null>(null)
  const [messages, setMessages]     = useState<Message[]>([])
  const [questionNumber, setQNum]   = useState(1)
  const [totalQuestions, setTotal]  = useState(5)
  const [stageLabel, setStageLabel] = useState('Introduction')
  const [timeLeft, setTimeLeft]     = useState(120)
  const [analyses, setAnalyses]     = useState<Analysis[]>([])

  const [isRecording, setIsRecording]   = useState(false)
  const [isSpeaking, setIsSpeaking]     = useState(false)
  const [transcript, setTranscript]     = useState('')
  const [voiceSupported, setVoiceSupported] = useState(true)

  const [isLoading, setIsLoading]   = useState(false)
  const [error, setError]           = useState<string | null>(null)
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null)
  const [expandedQ, setExpandedQ]   = useState<number | null>(null)

  const recognitionRef  = useRef<SpeechRecognition | null>(null)
  const isProcessingRef = useRef(false)
  const messagesEndRef  = useRef<HTMLDivElement>(null)
  const timerRef        = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return
    if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
      setVoiceSupported(false); return
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    recognitionRef.current = new SR()
    recognitionRef.current.lang = 'en-US'
    recognitionRef.current.continuous = false
    recognitionRef.current.interimResults = true
    recognitionRef.current.onresult = (event) => {
      let final = '', interim = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) final   += event.results[i][0].transcript
        else                          interim += event.results[i][0].transcript
      }
      if (final.trim()) {
        setIsRecording(false)
        setTranscript(final.trim())
        if (!isProcessingRef.current) submitAnswer(final.trim())
      } else if (interim) setTranscript(interim)
    }
    recognitionRef.current.onerror = (e) => {
      setIsRecording(false)
      showError(`Mic error: ${e.error}. Please type your answer.`)
    }
    recognitionRef.current.onend = () => setIsRecording(false)
    return () => { recognitionRef.current?.stop(); window.speechSynthesis?.cancel() }
  }, [])

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const startTimer = useCallback((seconds: number) => {
    if (timerRef.current) clearInterval(timerRef.current)
    setTimeLeft(seconds)
    timerRef.current = setInterval(() => {
      setTimeLeft(prev => { if (prev <= 1) { clearInterval(timerRef.current!); return 0 } return prev - 1 })
    }, 1000)
  }, [])

  const stopTimer = useCallback(() => { if (timerRef.current) clearInterval(timerRef.current) }, [])

  const showError = (msg: string) => { setError(msg); setTimeout(() => setError(null), 4000) }

  const addMessage = (msg: Omit<Message, 'id' | 'timestamp'>) => {
    setMessages(prev => [...prev, { ...msg, id: prev.length + 1, timestamp: new Date() }])
  }

  const speakText = useCallback((text: string) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.9; utterance.pitch = 1; utterance.volume = 1
    const voices = window.speechSynthesis.getVoices()
    const voice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google'))
               || voices.find(v => v.lang.startsWith('en'))
    if (voice) utterance.voice = voice
    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend   = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)
    window.speechSynthesis.speak(utterance)
  }, [])

  const stopSpeaking = () => { window.speechSynthesis?.cancel(); setIsSpeaking(false) }

  const toggleRecording = () => {
    if (!voiceSupported) { showError('Voice not supported. Please type your answer.'); return }
    if (isRecording) { recognitionRef.current?.stop(); setIsRecording(false) }
    else {
      setTranscript('')
      try { recognitionRef.current?.start(); setIsRecording(true) }
      catch { showError('Could not start microphone. Please type your answer.') }
    }
  }

  const startInterview = async () => {
    if (!selectedDomain) { showError('Please select a domain first.'); return }
    setIsLoading(true); setError(null)
    try {
      const res = await fetch(`${API_URL}/api/start-interview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          domain: selectedDomain.label, difficulty,
          num_questions: numQuestions,
          resume_text: resumeText.trim() || null,
        }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setSessionId(data.session_id)
      setQNum(data.question_number ?? 1)
      setTotal(data.total_questions ?? numQuestions)
      setStageLabel(data.stage_label ?? 'Introduction')
      const question = data.question || data.next_question || 'Tell me about yourself.'
      setMessages([])
      addMessage({ role: 'ai', content: question, type: data.question_type })
      startTimer(data.time_limit_seconds ?? 120)
      speakText(question)
      setScreen('interview')
    } catch (e: any) {
      showError(e.message || 'Failed to start. Is the backend running on port 8000?')
    } finally { setIsLoading(false) }
  }

  const submitAnswer = async (answerText?: string) => {
    if (isProcessingRef.current) return
    const text = (answerText || transcript).trim()
    if (!text || !sessionId) return
    if (isRecording) { recognitionRef.current?.stop(); setIsRecording(false) }
    isProcessingRef.current = true
    stopTimer(); setIsLoading(true); setTranscript('')
    addMessage({ role: 'user', content: text })
    try {
      const res = await fetch(`${API_URL}/api/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, user_answer: text, question_id: questionNumber }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      const anal: Analysis = data.analysis
      setAnalyses(prev => [...prev, anal])
      if (data.interview_completed) {
        addMessage({
          role: 'ai',
          content: `Great effort! Score for this question: ${Math.round(anal.score)}%. Generating your full report...`,
          score: anal.score, strengths: anal.strengths, improvements: anal.improvements,
        })
        await fetchReport(sessionId)
      } else {
        if (anal.ai_feedback) {
          addMessage({
            role: 'ai',
            content: `Score: ${Math.round(anal.score)}% — ${anal.ai_feedback}`,
            score: anal.score, strengths: anal.strengths, improvements: anal.improvements,
          })
        }
        const nextQ = data.next_question
        if (nextQ) {
          setTimeout(() => {
            addMessage({ role: 'ai', content: nextQ, type: data.question_type })
            setQNum(data.question_number)
            setStageLabel(data.stage_label ?? stageLabel)
            const tl = data.time_limit_seconds ?? 120
            startTimer(tl)
            speakText(nextQ)
          }, 800)
        }
      }
    } catch (e: any) {
      showError(e.message || 'Failed to submit answer.')
    } finally { setIsLoading(false); isProcessingRef.current = false }
  }

  const fetchReport = async (sid: string) => {
    try {
      const res = await fetch(`${API_URL}/api/end-interview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sid }),
      })
      if (!res.ok) throw new Error(`Report error: ${res.status}`)
      const data = await res.json()
      if (data.evaluation) setEvaluation(data.evaluation)
    } catch (e: any) {
      showError(e.message || 'Failed to load report.')
    } finally { stopTimer(); setScreen('results') }
  }

  const endInterview = async () => {
    stopSpeaking(); stopTimer()
    if (!sessionId) { router.push('/dashboard'); return }
    setIsLoading(true)
    await fetchReport(sessionId)
    setIsLoading(false)
  }

  const restart = () => {
    stopSpeaking(); stopTimer()
    setScreen('setup'); setSessionId(null); setMessages([])
    setAnalyses([]); setEvaluation(null); setTranscript('')
    setQNum(1); setStageLabel('Introduction')
  }

  // ── SETUP SCREEN ─────────────────────────────────────────
  if (screen === 'setup') return (
    <div className="min-h-screen bg-[#0a0a0f] overflow-y-auto">
      <header className="border-b border-white/5 bg-[#0a0a0f]/90 backdrop-blur-xl sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-6 h-14 flex items-center gap-3">
          <Link href="/dashboard" className="text-gray-500 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <Brain className="w-5 h-5 text-violet-400" />
          <span className="text-white font-medium">AI Mock Interview</span>
        </div>
      </header>
      <main className="max-w-3xl mx-auto px-6 py-12">
        <div className="mb-10 text-center">
          <h1 className="text-3xl font-semibold text-white mb-2">Set up your interview</h1>
          <p className="text-gray-400 text-sm">Voice-based one-on-one with instant AI feedback and scoring</p>
        </div>
        {error && (
          <div className="mb-6 flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
          </div>
        )}
        <p className="text-xs uppercase tracking-widest text-gray-500 mb-3">Choose your domain</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 mb-8">
          {DOMAINS.map(d => (
            <button key={d.id} onClick={() => setDomain(d)}
              className={`p-3 rounded-xl border text-left transition-all ${
                selectedDomain?.id === d.id
                  ? 'border-violet-500 bg-violet-500/10 text-white'
                  : 'border-white/5 bg-white/[0.02] text-gray-400 hover:border-white/10 hover:text-gray-200'
              }`}>
              <span className="text-xl block mb-1">{d.icon}</span>
              <span className="text-xs leading-tight">{d.label}</span>
            </button>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-6 mb-8">
          <div>
            <p className="text-xs uppercase tracking-widest text-gray-500 mb-3">Difficulty</p>
            <div className="flex gap-2">
              {DIFFICULTIES.map(d => (
                <button key={d} onClick={() => setDifficulty(d)}
                  className={`flex-1 py-2 rounded-lg border text-sm capitalize transition-all ${
                    difficulty === d
                      ? 'border-violet-500 bg-violet-500/10 text-white'
                      : 'border-white/5 bg-white/[0.02] text-gray-400 hover:text-gray-200'
                  }`}>{d}</button>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-gray-500 mb-3">Questions</p>
            <div className="flex items-center gap-3">
              <button onClick={() => setNum(n => Math.max(2, n - 1))}
                className="w-9 h-9 rounded-lg border border-white/5 bg-white/[0.02] text-gray-300 text-lg hover:border-white/10">−</button>
              <span className="text-2xl font-light text-violet-400 w-6 text-center">{numQuestions}</span>
              <button onClick={() => setNum(n => Math.min(10, n + 1))}
                className="w-9 h-9 rounded-lg border border-white/5 bg-white/[0.02] text-gray-300 text-lg hover:border-white/10">+</button>
            </div>
          </div>
        </div>
        <p className="text-xs uppercase tracking-widest text-gray-500 mb-3">
          Resume <span className="normal-case tracking-normal text-gray-600">(optional)</span>
        </p>
        <textarea value={resumeText} onChange={e => setResumeText(e.target.value)}
          placeholder="Paste your resume text here (optional)..."
          rows={4}
          className="w-full bg-white/[0.02] border border-white/5 rounded-xl p-4 text-sm text-gray-200 placeholder-gray-600 resize-none focus:outline-none focus:border-violet-500/50 mb-8 transition-colors" />
        <button onClick={startInterview} disabled={isLoading || !selectedDomain}
          className="w-full py-4 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2">
          {isLoading ? <><Loader2 className="w-5 h-5 animate-spin" /> Generating questions...</>
                     : <><Mic className="w-5 h-5" /> Begin Interview</>}
        </button>
      </main>
    </div>
  )

  // ── INTERVIEW SCREEN ──────────────────────────────────────
  if (screen === 'interview') return (
    <div className="min-h-screen bg-[#0a0a0f] flex flex-col">
      <header className="flex-shrink-0 border-b border-white/5 bg-[#0a0a0f]/90 backdrop-blur-xl z-10">
        <div className="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Brain className="w-5 h-5 text-violet-400" />
            <span className="text-white font-medium text-sm hidden sm:block">{selectedDomain?.label}</span>
            <span className="text-xs text-violet-400 px-2 py-0.5 rounded-full border border-violet-500/30 bg-violet-500/10">{stageLabel}</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2">
              <div className="w-24 h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-violet-500 rounded-full transition-all duration-500"
                  style={{ width: `${((questionNumber - 1) / totalQuestions) * 100}%` }} />
              </div>
              <span className="text-xs text-gray-400">{questionNumber}/{totalQuestions}</span>
            </div>
            <div className={`flex items-center gap-1 text-xs font-mono ${timeLeft <= 30 ? 'text-red-400' : 'text-gray-400'}`}>
              <Clock className="w-3.5 h-3.5" />
              {String(Math.floor(timeLeft / 60)).padStart(2,'0')}:{String(timeLeft % 60).padStart(2,'0')}
            </div>
            {isSpeaking && (
              <button onClick={stopSpeaking} className="flex items-center gap-1.5 text-xs text-sky-400">
                <Volume2 className="w-3.5 h-3.5 animate-pulse" /> Stop
              </button>
            )}
            <button onClick={endInterview} disabled={isLoading}
              className="text-xs px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 transition-colors">
              End
            </button>
          </div>
        </div>
      </header>
      {error && (
        <div className="bg-red-500/10 border-b border-red-500/20 px-6 py-2 text-red-400 text-xs text-center">{error}</div>
      )}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl w-full mx-auto space-y-4">
        {messages.map(msg => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'ai' && (
              <div className="w-7 h-7 rounded-full bg-violet-500/20 border border-violet-500/30 flex items-center justify-center flex-shrink-0 mr-3 mt-0.5">
                <Brain className="w-3.5 h-3.5 text-violet-400" />
              </div>
            )}
            <div className={`max-w-[78%] ${msg.role === 'user' ? 'order-first' : ''}`}>
              <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-violet-600 text-white rounded-br-sm'
                  : 'bg-white/[0.04] border border-white/5 text-gray-100 rounded-bl-sm'
              }`}>{msg.content}</div>
              {msg.score !== undefined && (
                <div className="mt-2 space-y-1">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${scoreBg(msg.score)}`}>
                    {Math.round(msg.score)}/100
                  </span>
                  {(msg.strengths?.length ?? 0) > 0 && (
                    <p className="text-xs text-gray-500">✓ {msg.strengths!.slice(0,2).join(' · ')}</p>
                  )}
                  {(msg.improvements?.length ?? 0) > 0 && (
                    <p className="text-xs text-gray-500">△ {msg.improvements!.slice(0,1).join('')}</p>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="w-7 h-7 rounded-full bg-violet-500/20 border border-violet-500/30 flex items-center justify-center mr-3">
              <Brain className="w-3.5 h-3.5 text-violet-400" />
            </div>
            <div className="bg-white/[0.04] border border-white/5 rounded-2xl rounded-bl-sm px-4 py-3">
              <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="flex-shrink-0 border-t border-white/5 bg-[#0a0a0f] px-4 py-4">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="flex-1 relative">
            <textarea value={transcript} onChange={e => setTranscript(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitAnswer() } }}
              placeholder={isRecording ? 'Listening...' : voiceSupported ? 'Speak or type your answer (Enter to submit)' : 'Type your answer here...'}
              rows={2}
              className="w-full bg-white/[0.03] border border-white/8 rounded-xl px-4 py-3 text-sm text-gray-200 placeholder-gray-600 resize-none focus:outline-none focus:border-violet-500/40 transition-colors pr-24" />
            <button onClick={() => submitAnswer()} disabled={isLoading || !transcript.trim()}
              className="absolute right-2 bottom-2 px-3 py-1.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-30 disabled:cursor-not-allowed text-white text-xs rounded-lg transition-colors flex items-center gap-1">
              Send <ChevronRight className="w-3 h-3" />
            </button>
          </div>
          <button onClick={toggleRecording} disabled={isLoading}
            className={`w-12 h-12 rounded-full flex-shrink-0 flex items-center justify-center transition-all ${
              isRecording ? 'bg-red-500 shadow-[0_0_20px_rgba(239,68,68,0.4)] animate-pulse' : 'bg-violet-600 hover:bg-violet-500'
            } disabled:opacity-40 disabled:cursor-not-allowed`}>
            {isLoading ? <Loader2 className="w-5 h-5 text-white animate-spin" />
              : isRecording ? <MicOff className="w-5 h-5 text-white" />
              : <Mic className="w-5 h-5 text-white" />}
          </button>
        </div>
        <p className="text-center text-xs text-gray-600 mt-2">
          {isRecording ? '● Recording — click mic to stop' : 'Click mic to speak · Enter to submit typed answer'}
        </p>
      </div>
    </div>
  )

  // ── RESULTS SCREEN ────────────────────────────────────────
  return (
    <div className="min-h-screen bg-[#0a0a0f] overflow-y-auto">
      <header className="border-b border-white/5 sticky top-0 bg-[#0a0a0f]/90 backdrop-blur-xl z-10">
        <div className="max-w-3xl mx-auto px-6 h-14 flex items-center gap-3">
          <Brain className="w-5 h-5 text-violet-400" />
          <span className="text-white font-medium">Interview Complete</span>
        </div>
      </header>
      <main className="max-w-3xl mx-auto px-6 py-10 space-y-8">
        <div className="text-center">
          <div className="w-24 h-24 rounded-full border-2 border-violet-500 flex items-center justify-center mx-auto mb-4">
            <span className="text-4xl font-light text-violet-400">{evaluation?.grade ?? '—'}</span>
          </div>
          <div className="text-5xl font-light text-white mb-1">
            {evaluation ? `${Math.round(evaluation.overall_score)}` : '—'}
            <span className="text-2xl text-gray-500">/100</span>
          </div>
          <p className="text-gray-400 text-sm">{selectedDomain?.label} · {difficulty} · {totalQuestions} questions</p>
        </div>

        {evaluation && (
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Technical',       val: evaluation.technical_score,     color: 'text-violet-400' },
              { label: 'Communication',   val: evaluation.communication_score, color: 'text-sky-400' },
              { label: 'Problem Solving', val: evaluation.problem_solving,     color: 'text-emerald-400' },
            ].map(({ label, val, color }) => (
              <div key={label} className="bg-white/[0.03] border border-white/5 rounded-xl p-4 text-center">
                <p className="text-xs text-gray-500 mb-2">{label}</p>
                <p className={`text-2xl font-light ${color}`}>{Math.round(val ?? 0)}</p>
                <div className="mt-2 h-1 bg-white/5 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${color.replace('text-', 'bg-')}`} style={{ width: `${val ?? 0}%` }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {evaluation && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-5">
              <h3 className="text-sm font-medium text-emerald-400 mb-3 flex items-center gap-2">
                <CheckCircle className="w-4 h-4" /> Strengths
              </h3>
              <ul className="space-y-2">
                {((evaluation.strengths?.length ?? 0) > 0 ? evaluation.strengths : ['No specific strengths noted']).map((s, i) => (
                  <li key={i} className="text-xs text-gray-300 flex gap-2">
                    <span className="text-emerald-500 mt-0.5">✓</span>{s}
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-5">
              <h3 className="text-sm font-medium text-amber-400 mb-3 flex items-center gap-2">
                <Star className="w-4 h-4" /> Areas to Improve
              </h3>
              <ul className="space-y-2">
                {((evaluation.improvements?.length ?? 0) > 0 ? evaluation.improvements : ['Keep practising!']).map((s, i) => (
                  <li key={i} className="text-xs text-gray-300 flex gap-2">
                    <span className="text-amber-500 mt-0.5">△</span>{s}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {evaluation && (evaluation.suggestions?.length ?? 0) > 0 && (
          <div className="bg-white/[0.02] border border-white/5 rounded-xl p-5">
            <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-violet-400" /> Recommendations
            </h3>
            <div className="space-y-3">
              {evaluation.suggestions.map((s, i) => (
                <div key={i} className="flex gap-3 text-xs text-gray-300">
                  <span className="font-mono text-violet-400 bg-violet-500/10 px-2 py-0.5 rounded flex-shrink-0">0{i+1}</span>
                  {s}
                </div>
              ))}
            </div>
          </div>
        )}

        {evaluation && (evaluation.per_question?.length ?? 0) > 0 && (
          <div>
            <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-violet-400" /> Question Breakdown
            </h3>
            <div className="space-y-2">
              {(evaluation.per_question ?? []).map((pq, i) => (
                <div key={i} className="bg-white/[0.02] border border-white/5 rounded-xl overflow-hidden">
                  <button onClick={() => setExpandedQ(expandedQ === i ? null : i)}
                    className="w-full flex items-center justify-between p-4 text-left hover:bg-white/[0.02] transition-colors">
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="text-xs font-mono text-gray-500 flex-shrink-0">Q{pq.question_number}</span>
                      <span className="text-sm text-gray-200 truncate">{pq.question}</span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${scoreBg(pq.score ?? 0)}`}>
                        {Math.round(pq.score ?? 0)}/100
                      </span>
                      <ChevronRight className={`w-4 h-4 text-gray-500 transition-transform ${expandedQ === i ? 'rotate-90' : ''}`} />
                    </div>
                  </button>
                  {expandedQ === i && (
                    <div className="px-4 pb-4 border-t border-white/5 pt-3 space-y-2">
                      <p className="text-xs text-gray-300 leading-relaxed bg-white/[0.03] rounded-lg p-3">{pq.feedback}</p>
                      {(pq.points_covered?.length ?? 0) > 0 && (
                        <p className="text-xs text-emerald-400">✓ Covered: {pq.points_covered.join(', ')}</p>
                      )}
                      {(pq.points_missed?.length ?? 0) > 0 && (
                        <p className="text-xs text-amber-400">△ Missed: {pq.points_missed.join(', ')}</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-3 pt-2">
          <Link href="/dashboard"
            className="flex-1 py-3 text-center text-sm font-medium bg-violet-600 hover:bg-violet-500 text-white rounded-xl transition-colors">
            Dashboard
          </Link>
          <button onClick={restart}
            className="flex-1 py-3 text-sm font-medium bg-white/[0.03] border border-white/5 hover:border-white/10 text-gray-300 rounded-xl transition-colors">
            New Interview
          </button>
        </div>
      </main>
    </div>
  )
}