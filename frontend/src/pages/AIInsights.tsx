import { useState } from 'react'
import { askAI, analyzeTradeAI } from '../api/client'

export default function AIInsights() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [tradeId, setTradeId] = useState('')
  const [analysis, setAnalysis] = useState('')
  const [loading, setLoading] = useState(false)
  const [analysisLoading, setAnalysisLoading] = useState(false)

  const handleAsk = async () => {
    if (!question.trim()) return
    setLoading(true)
    setAnswer('')
    try {
      const res = await askAI(question)
      setAnswer(res.answer || res.error || 'No response')
    } catch {
      setAnswer('Error connecting to AI service')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!tradeId) return
    setAnalysisLoading(true)
    setAnalysis('')
    try {
      const res = await analyzeTradeAI(Number(tradeId))
      setAnalysis(res.analysis || res.error || 'No analysis returned')
    } catch {
      setAnalysis('Error connecting to AI service')
    } finally {
      setAnalysisLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">AI Insights</h2>
        <p className="text-sm text-gray-500 mt-0.5">Powered by Llama 3.2 — running locally</p>
      </div>

      {/* Q&A */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-3">
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Ask a Trading Question</h3>
        <div className="flex gap-2">
          <input
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAsk()}
            placeholder="e.g. What is the Kelly Criterion?"
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleAsk}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white text-sm rounded-lg transition-colors"
          >
            {loading ? 'Thinking...' : 'Ask'}
          </button>
        </div>
        {answer && (
          <div className="bg-gray-800 rounded-lg p-3 text-sm text-gray-300 leading-relaxed whitespace-pre-wrap border-l-2 border-blue-500">
            {answer}
          </div>
        )}
      </div>

      {/* Trade Analysis */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-3">
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Trade Post-Mortem</h3>
        <div className="flex gap-2">
          <input
            value={tradeId}
            onChange={e => setTradeId(e.target.value)}
            placeholder="Enter trade ID (e.g. 1)"
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-blue-500"
            type="number"
          />
          <button
            onClick={handleAnalyze}
            disabled={analysisLoading}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 text-white text-sm rounded-lg transition-colors"
          >
            {analysisLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
        {analysis && (
          <div className="bg-gray-800 rounded-lg p-3 text-sm text-gray-300 leading-relaxed whitespace-pre-wrap border-l-2 border-purple-500">
            {analysis}
          </div>
        )}
      </div>
    </div>
  )
}