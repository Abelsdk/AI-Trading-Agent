// src/api/client.ts
// Central API client — all backend calls go through here.
// Never use fetch/axios directly in components.

import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// — Types —
export interface Trade {
  id: number
  symbol: string
  direction: 'LONG' | 'SHORT'
  entry_price: number
  exit_price: number | null
  stop_loss: number | null
  take_profit: number | null
  quantity: number
  risk_percent: number | null
  strategy: string | null
  reasoning: string | null
  emotion: string | null
  notes: string | null
  status: 'OPEN' | 'CLOSED'
  entry_time: string
  exit_time: string | null
  created_at: string
  updated_at: string
}

export interface AnalyticsSummary {
  total_trades: number
  win_rate: number
  total_pnl: number
  avg_win: number
  avg_loss: number
  expectancy: number
  r_expectancy: number | null
  profit_factor: number
  max_drawdown: number
  sharpe_ratio: number
  max_win_streak: number
  max_loss_streak: number
  wins: number
  losses: number
}

export interface AIResponse {
  analysis?: string
  answer?: string
  error?: string
  model?: string
}

// — API calls —
export const getTrades = () =>
  api.get<Trade[]>('/trades/').then(r => r.data)

export const createTrade = (data: Partial<Trade>) =>
  api.post<Trade>('/trades/', data).then(r => r.data)

export const updateTrade = (id: number, data: Partial<Trade>) =>
  api.patch<Trade>(`/trades/${id}`, data).then(r => r.data)

export const getAnalytics = () =>
  api.get<AnalyticsSummary>('/analytics/summary').then(r => r.data)

export const getStrategyBreakdown = () =>
  api.get('/analytics/strategies').then(r => r.data)

export const analyzeTradeAI = (id: number) =>
  api.get<AIResponse>(`/ai/analyze-trade/${id}`).then(r => r.data)

export const askAI = (question: string) =>
  api.get<AIResponse>('/ai/ask', { params: { question } }).then(r => r.data)

export const fetchMarketData = (symbol: string, period = '2y', interval = '1d') =>
  api.post('/market-data/fetch', null, {
    params: { symbol, period, interval }
  }).then(r => r.data)

export default api