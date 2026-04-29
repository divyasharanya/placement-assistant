'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'

// ─── Types ───────────────────────────────────────────────────
interface Problem {
  id: string; title: string; slug: string
  difficulty: string; category: string; tags: string[]
  platformLink: string; companies_asked: string[]
  frequency_score: number; acceptance_rate: number
  time_complexity: string; space_complexity: string
}
interface DailyProblem {
  id: string; title: string; slug: string; difficulty: string
  category: string; tags: string[]; platformLink: string
  acceptance_rate: number; time_complexity: string; date: string
}
interface Stats { total: number; easy: number; medium: number; hard: number; topics: number; companies: number }
interface Difficulty { value: string; label: string; count: number }

const API = 'http://localhost:8004'

// ─── Difficulty config ────────────────────────────────────────
const DIFF_CONFIG: Record<string, { color: string; bg: string; border: string; dot: string }> = {
  easy:   { color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/30', dot: 'bg-emerald-400' },
  medium: { color: 'text-amber-400',   bg: 'bg-amber-400/10',   border: 'border-amber-400/30',   dot: 'bg-amber-400' },
  hard:   { color: 'text-rose-400',    bg: 'bg-rose-400/10',    border: 'border-rose-400/30',    dot: 'bg-rose-400' },
}
const dc = (d: string) => DIFF_CONFIG[d?.toLowerCase()] ?? DIFF_CONFIG.easy

const SORT_OPTIONS = [
  { value: 'frequency',      label: 'Most Popular' },
  { value: 'acceptance',     label: 'Easiest First' },
  { value: 'difficulty_asc', label: 'Easy → Hard' },
  { value: 'difficulty_desc',label: 'Hard → Easy' },
]

// ─── Main component ───────────────────────────────────────────
export default function PracticePage() {
  const router        = useRouter()
  const searchParams  = useSearchParams()

  // Data
  const [problems,    setProblems]    = useState<Problem[]>([])
  const [daily,       setDaily]       = useState<DailyProblem | null>(null)
  const [stats,       setStats]       = useState<Stats | null>(null)
  const [topics,      setTopics]      = useState<string[]>([])
  const [difficulties,setDifficulties]= useState<Difficulty[]>([])
  const [companies,   setCompanies]   = useState<string[]>([])
  const [total,       setTotal]       = useState(0)

  // Filters
  const [search,      setSearch]      = useState(searchParams.get('q') ?? '')
  const [difficulty,  setDifficulty]  = useState(searchParams.get('d') ?? '')
  const [topic,       setTopic]       = useState(searchParams.get('t') ?? '')
  const [company,     setCompany]     = useState(searchParams.get('c') ?? '')
  const [sortBy,      setSortBy]      = useState('frequency')
  const [offset,      setOffset]      = useState(0)
  const limit = 15

  // UI
  const [loading,     setLoading]     = useState(true)
  const [loadingInit, setLoadingInit] = useState(true)
  const [showFilters, setShowFilters] = useState(false)
  const searchRef = useRef<HTMLInputElement>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout>>()

  // ── Init fetch ───────────────────────────────────────────────
  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/daily-problem`).then(r => r.json()),
      fetch(`${API}/api/stats`).then(r => r.json()),
      fetch(`${API}/api/topics`).then(r => r.json()),
      fetch(`${API}/api/difficulties`).then(r => r.json()),
      fetch(`${API}/api/companies`).then(r => r.json()),
    ]).then(([d, s, t, diff, comp]) => {
      setDaily(d)
      setStats(s)
      setTopics(t.topics ?? [])
      setDifficulties(diff.difficulties ?? [])
      setCompanies(comp.companies ?? [])
    }).catch(console.error).finally(() => setLoadingInit(false))
  }, [])

  // ── Fetch problems ───────────────────────────────────────────
  const fetchProblems = useCallback(() => {
    setLoading(true)
    const params = new URLSearchParams()
    params.set('limit', String(limit))
    params.set('offset', String(offset))
    params.set('sort_by', sortBy)
    if (search)    params.set('search', search)
    if (difficulty)params.set('difficulty', difficulty)
    if (topic)     params.set('topic', topic)
    if (company)   params.set('company', company)

    fetch(`${API}/api/problems?${params}`)
      .then(r => r.json())
      .then(d => { setProblems(d.problems ?? []); setTotal(d.total ?? 0) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [search, difficulty, topic, company, sortBy, offset])

  useEffect(() => {
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(fetchProblems, search ? 300 : 0)
    return () => clearTimeout(debounceRef.current)
  }, [fetchProblems])

  // reset offset on filter change
  useEffect(() => { setOffset(0) }, [search, difficulty, topic, company, sortBy])

  const clearFilters = () => {
    setSearch(''); setDifficulty(''); setTopic(''); setCompany(''); setSortBy('frequency')
    searchRef.current?.focus()
  }
  const hasFilters = search || difficulty || topic || company

  const totalPages = Math.ceil(total / limit)
  const currentPage = Math.floor(offset / limit) + 1

  // ── Render ───────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-[#080810] text-[#e0e0f0]" style={{ fontFamily: "'IBM Plex Mono', 'Courier New', monospace" }}>

      {/* Subtle grid background */}
      <div className="fixed inset-0 pointer-events-none" style={{
        backgroundImage: 'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)',
        backgroundSize: '40px 40px'
      }} />

      {/* ── Header ──────────────────────────────────────────── */}
      <div className="relative border-b border-white/5 bg-[#080810]/80 backdrop-blur-xl sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="text-[#5a5a8a] hover:text-[#9090c0] transition-colors text-sm">
              ← back
            </Link>
            <span className="text-[#5a5a8a]">/</span>
            <span className="text-sm text-[#9090c0]">practice</span>
          </div>
          <div className="flex items-center gap-4">
            {stats && (
              <div className="hidden sm:flex items-center gap-4 text-xs text-[#5a5a8a]">
                <span><span className="text-emerald-400 font-medium">{stats.easy}</span> easy</span>
                <span><span className="text-amber-400 font-medium">{stats.medium}</span> medium</span>
                <span><span className="text-rose-400 font-medium">{stats.hard}</span> hard</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        {/* ── Page title ──────────────────────────────────── */}
        <div>
          <div className="text-xs text-[#5a5a8a] mb-1 tracking-widest uppercase">// coding practice</div>
          <h1 className="text-2xl sm:text-3xl font-light text-white tracking-tight">
            Problem <span style={{ color: '#7b7bff' }}>Library</span>
          </h1>
        </div>

        {/* ── Daily problem ────────────────────────────────── */}
        {daily && (
          <div className="relative rounded-xl border border-[#7b7bff]/20 bg-[#0e0e1c] overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-[#7b7bff]/5 via-transparent to-[#ff7bdb]/5 pointer-events-none" />
            <div className="relative p-5 sm:p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-[10px] tracking-widest uppercase text-[#7b7bff] border border-[#7b7bff]/30 px-2 py-0.5 rounded">
                      ★ daily
                    </span>
                    <span className="text-xs text-[#5a5a8a]">{daily.date}</span>
                  </div>
                  <h2 className="text-lg sm:text-xl font-light text-white mb-2 truncate">{daily.title}</h2>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded border font-medium ${dc(daily.difficulty).color} ${dc(daily.difficulty).bg} ${dc(daily.difficulty).border}`}>
                      {daily.difficulty}
                    </span>
                    <span className="text-xs text-[#5a5a8a]">{daily.category}</span>
                    {daily.acceptance_rate > 0 && (
                      <span className="text-xs text-[#5a5a8a]">{daily.acceptance_rate.toFixed(1)}% acceptance</span>
                    )}
                    {daily.time_complexity && (
                      <span className="text-xs font-mono text-[#7b7bff]/70 border border-[#7b7bff]/20 px-2 py-0.5 rounded">{daily.time_complexity}</span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <Link href={`/practice/${daily.slug}`}
                    className="text-sm px-4 py-2 rounded-lg border border-[#7b7bff]/40 text-[#9090ff] hover:border-[#7b7bff] hover:text-white transition-all">
                    Details
                  </Link>
                  <a href={daily.platformLink} target="_blank" rel="noopener noreferrer"
                    className="text-sm px-4 py-2 rounded-lg bg-[#7b7bff] text-white hover:bg-[#9090ff] transition-colors">
                    Solve →
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Stats row ─────────────────────────────────────── */}
        {stats && (
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
            {[
              { label: 'Total',     val: stats.total,     color: 'text-[#9090c0]' },
              { label: 'Easy',      val: stats.easy,      color: 'text-emerald-400' },
              { label: 'Medium',    val: stats.medium,    color: 'text-amber-400' },
              { label: 'Hard',      val: stats.hard,      color: 'text-rose-400' },
              { label: 'Topics',    val: stats.topics,    color: 'text-[#7b7bff]' },
              { label: 'Companies', val: stats.companies, color: 'text-[#ff7bdb]' },
            ].map(s => (
              <div key={s.label} className="bg-[#0e0e1c] border border-white/5 rounded-lg p-3 text-center">
                <div className={`text-xl font-light ${s.color}`}>{s.val}</div>
                <div className="text-[10px] tracking-wider uppercase text-[#5a5a8a] mt-0.5">{s.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* ── Search + Sort + Filter toggle ────────────────── */}
        <div className="space-y-3">
          <div className="flex gap-2">
            {/* Search */}
            <div className="flex-1 relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5a5a8a] text-xs font-mono select-none">$</span>
              <input
                ref={searchRef}
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="search problems, topics, algorithms..."
                className="w-full bg-[#0e0e1c] border border-white/8 rounded-lg pl-7 pr-4 py-2.5 text-sm text-[#e0e0f0] placeholder-[#3a3a5a] focus:outline-none focus:border-[#7b7bff]/50 transition-colors"
              />
              {search && (
                <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#5a5a8a] hover:text-[#9090c0] text-xs">✕</button>
              )}
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value)}
              className="bg-[#0e0e1c] border border-white/8 rounded-lg px-3 py-2.5 text-xs text-[#9090c0] focus:outline-none focus:border-[#7b7bff]/50 cursor-pointer"
            >
              {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>

            {/* Filter toggle */}
            <button
              onClick={() => setShowFilters(f => !f)}
              className={`px-3 py-2.5 rounded-lg border text-xs transition-all ${
                showFilters || hasFilters
                  ? 'border-[#7b7bff]/50 bg-[#7b7bff]/10 text-[#9090ff]'
                  : 'border-white/8 text-[#5a5a8a] hover:text-[#9090c0]'
              }`}
            >
              ⚙ filters{hasFilters ? ` (${[difficulty,topic,company].filter(Boolean).length})` : ''}
            </button>
          </div>

          {/* Expandable filters */}
          {showFilters && (
            <div className="bg-[#0e0e1c] border border-white/5 rounded-xl p-4 space-y-4">

              {/* Difficulty */}
              <div>
                <div className="text-[10px] tracking-widest uppercase text-[#5a5a8a] mb-2">Difficulty</div>
                <div className="flex flex-wrap gap-2">
                  {['', 'easy', 'medium', 'hard'].map(d => (
                    <button key={d} onClick={() => setDifficulty(d)}
                      className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
                        difficulty === d
                          ? d ? `${dc(d).color} ${dc(d).bg} ${dc(d).border}` : 'border-[#7b7bff]/40 text-[#9090ff] bg-[#7b7bff]/10'
                          : 'border-white/5 text-[#5a5a8a] hover:text-[#9090c0] hover:border-white/10'
                      }`}>
                      {d || 'all'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Topics */}
              <div>
                <div className="text-[10px] tracking-widest uppercase text-[#5a5a8a] mb-2">Topic</div>
                <div className="flex flex-wrap gap-1.5">
                  {['', ...topics].map(t => (
                    <button key={t} onClick={() => setTopic(t)}
                      className={`text-xs px-2.5 py-1 rounded-lg border transition-all ${
                        topic === t
                          ? 'border-[#7b7bff]/40 text-[#9090ff] bg-[#7b7bff]/10'
                          : 'border-white/5 text-[#5a5a8a] hover:text-[#9090c0] hover:border-white/10'
                      }`}>
                      {t || 'all topics'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Companies */}
              <div>
                <div className="text-[10px] tracking-widest uppercase text-[#5a5a8a] mb-2">Company</div>
                <div className="flex flex-wrap gap-1.5">
                  {['', ...companies].map(c => (
                    <button key={c} onClick={() => setCompany(c)}
                      className={`text-xs px-2.5 py-1 rounded-lg border transition-all ${
                        company === c
                          ? 'border-[#ff7bdb]/40 text-[#ff9be8] bg-[#ff7bdb]/10'
                          : 'border-white/5 text-[#5a5a8a] hover:text-[#9090c0] hover:border-white/10'
                      }`}>
                      {c || 'all companies'}
                    </button>
                  ))}
                </div>
              </div>

              {hasFilters && (
                <button onClick={clearFilters} className="text-xs text-rose-400/70 hover:text-rose-400 transition-colors">
                  ✕ clear all filters
                </button>
              )}
            </div>
          )}

          {/* Active filter pills */}
          {hasFilters && !showFilters && (
            <div className="flex flex-wrap gap-2 items-center">
              <span className="text-xs text-[#5a5a8a]">filters:</span>
              {difficulty && (
                <span className={`text-xs px-2.5 py-1 rounded-full border flex items-center gap-1.5 ${dc(difficulty).color} ${dc(difficulty).bg} ${dc(difficulty).border}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${dc(difficulty).dot}`} />
                  {difficulty}
                  <button onClick={() => setDifficulty('')} className="opacity-60 hover:opacity-100">✕</button>
                </span>
              )}
              {topic && (
                <span className="text-xs px-2.5 py-1 rounded-full border border-[#7b7bff]/30 text-[#9090ff] bg-[#7b7bff]/10 flex items-center gap-1.5">
                  {topic}
                  <button onClick={() => setTopic('')} className="opacity-60 hover:opacity-100">✕</button>
                </span>
              )}
              {company && (
                <span className="text-xs px-2.5 py-1 rounded-full border border-[#ff7bdb]/30 text-[#ff9be8] bg-[#ff7bdb]/10 flex items-center gap-1.5">
                  {company}
                  <button onClick={() => setCompany('')} className="opacity-60 hover:opacity-100">✕</button>
                </span>
              )}
              <button onClick={clearFilters} className="text-xs text-[#5a5a8a] hover:text-rose-400 transition-colors">clear all</button>
            </div>
          )}
        </div>

        {/* ── Problems table ───────────────────────────────── */}
        <div className="rounded-xl border border-white/5 bg-[#0e0e1c] overflow-hidden">

          {/* Table header */}
          <div className="hidden sm:grid grid-cols-[2fr_1fr_1fr_1fr_auto] gap-4 px-5 py-3 border-b border-white/5 text-[10px] tracking-widest uppercase text-[#3a3a5a]">
            <span>Problem</span>
            <span>Difficulty</span>
            <span>Category</span>
            <span>Complexity</span>
            <span>Action</span>
          </div>

          {loading ? (
            <div className="py-16 text-center">
              <div className="inline-flex items-center gap-2 text-xs text-[#5a5a8a]">
                <div className="w-4 h-4 border border-[#7b7bff]/40 border-t-[#7b7bff] rounded-full animate-spin" />
                loading problems...
              </div>
            </div>
          ) : problems.length === 0 ? (
            <div className="py-16 text-center space-y-2">
              <div className="text-[#5a5a8a] text-sm">no problems found</div>
              {hasFilters && (
                <button onClick={clearFilters} className="text-xs text-[#7b7bff] hover:underline">clear filters</button>
              )}
            </div>
          ) : (
            <div className="divide-y divide-white/[0.03]">
              {problems.map((p, i) => (
                <div key={p.id}
                  className="group grid grid-cols-1 sm:grid-cols-[2fr_1fr_1fr_1fr_auto] gap-x-4 gap-y-2 px-5 py-4 hover:bg-white/[0.02] transition-colors items-center">

                  {/* Title + tags */}
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-mono text-[#3a3a5a] flex-shrink-0">
                        {String(offset + i + 1).padStart(2, '0')}
                      </span>
                      <Link href={`/practice/${p.slug}`}
                        className="text-sm text-[#c0c0e0] hover:text-white font-light transition-colors truncate group-hover:text-white">
                        {p.title}
                      </Link>
                    </div>
                    <div className="flex flex-wrap gap-1 pl-6">
                      {p.tags.slice(0, 3).map(t => (
                        <button key={t} onClick={() => { setTopic(t); setShowFilters(false) }}
                          className="text-[10px] px-1.5 py-0.5 rounded border border-white/5 text-[#5a5a8a] hover:text-[#9090c0] hover:border-white/10 transition-colors">
                          {t}
                        </button>
                      ))}
                      {p.companies_asked.length > 0 && (
                        <span className="text-[10px] text-[#3a3a5a] px-1.5 py-0.5">
                          {p.companies_asked.slice(0, 2).join(', ')}{p.companies_asked.length > 2 ? ` +${p.companies_asked.length - 2}` : ''}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Difficulty */}
                  <div className="sm:block">
                    <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${dc(p.difficulty).color} ${dc(p.difficulty).bg} ${dc(p.difficulty).border}`}>
                      <span className={`w-1 h-1 rounded-full flex-shrink-0 ${dc(p.difficulty).dot}`} />
                      {p.difficulty}
                    </span>
                    {p.acceptance_rate > 0 && (
                      <div className="text-[10px] text-[#3a3a5a] mt-1 pl-0.5">{p.acceptance_rate.toFixed(0)}% accepted</div>
                    )}
                  </div>

                  {/* Category */}
                  <div className="hidden sm:block text-xs text-[#5a5a8a]">{p.category}</div>

                  {/* Complexity */}
                  <div className="hidden sm:block">
                    {p.time_complexity && (
                      <span className="text-[10px] font-mono text-[#7b7bff]/60 border border-[#7b7bff]/15 px-1.5 py-0.5 rounded">
                        {p.time_complexity}
                      </span>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 pl-6 sm:pl-0">
                    <Link href={`/practice/${p.slug}`}
                      className="text-xs text-[#5a5a8a] hover:text-[#9090c0] transition-colors">
                      details
                    </Link>
                    <a href={p.platformLink} target="_blank" rel="noopener noreferrer"
                      className="text-xs px-3 py-1.5 rounded-lg border border-[#7b7bff]/20 text-[#7b7bff] hover:bg-[#7b7bff]/10 hover:border-[#7b7bff]/40 transition-all whitespace-nowrap">
                      solve →
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Footer: count + pagination */}
          {!loading && problems.length > 0 && (
            <div className="border-t border-white/5 px-5 py-3 flex items-center justify-between gap-4">
              <span className="text-xs text-[#3a3a5a]">
                {offset + 1}–{Math.min(offset + limit, total)} of <span className="text-[#5a5a8a]">{total}</span> problems
                {hasFilters && <span className="ml-1 text-[#7b7bff]">(filtered)</span>}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setOffset(Math.max(0, offset - limit))}
                  disabled={offset === 0}
                  className="text-xs px-3 py-1.5 rounded border border-white/5 text-[#5a5a8a] disabled:opacity-30 hover:not-disabled:text-[#9090c0] hover:not-disabled:border-white/10 transition-colors"
                >
                  ← prev
                </button>
                <div className="flex gap-1">
                  {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                    let page = i + 1
                    if (totalPages > 7) {
                      if (currentPage <= 4) page = i + 1
                      else if (currentPage >= totalPages - 3) page = totalPages - 6 + i
                      else page = currentPage - 3 + i
                    }
                    return (
                      <button key={page} onClick={() => setOffset((page - 1) * limit)}
                        className={`w-7 h-7 rounded text-xs transition-colors ${
                          currentPage === page
                            ? 'bg-[#7b7bff]/20 text-[#9090ff] border border-[#7b7bff]/30'
                            : 'text-[#5a5a8a] hover:text-[#9090c0] border border-transparent hover:border-white/5'
                        }`}>
                        {page}
                      </button>
                    )
                  })}
                </div>
                <button
                  onClick={() => setOffset(offset + limit)}
                  disabled={offset + limit >= total}
                  className="text-xs px-3 py-1.5 rounded border border-white/5 text-[#5a5a8a] disabled:opacity-30 hover:not-disabled:text-[#9090c0] hover:not-disabled:border-white/10 transition-colors"
                >
                  next →
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ── Bottom padding ─────────────────────────────── */}
        <div className="h-8" />
      </div>
    </div>
  )
}