/**
 * Portfolio Service
 * API calls for portfolio data
 */

import { API_ENDPOINTS, getApiUrl } from '../config/api';
import type { PortfolioSummary, PortfolioPerformance } from '../types';
import { get } from './api';

export interface PortfolioHistory {
  timestamp: string;
  balance: number;
  pnl: number;
}

/**
 * Get portfolio summary
 */
export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  const url = getApiUrl(API_ENDPOINTS.PORTFOLIO_SUMMARY);
  return get<PortfolioSummary>(url);
}

/**
 * Get portfolio performance metrics
 */
export async function getPortfolioPerformance(): Promise<PortfolioPerformance> {
  const url = getApiUrl(API_ENDPOINTS.PORTFOLIO_PERFORMANCE);
  return get<PortfolioPerformance>(url);
}

/**
 * Get portfolio history
 */
export async function getPortfolioHistory(params?: {
  period?: '1d' | '1w' | '1m' | '3m' | '1y';
  interval?: '1m' | '5m' | '15m' | '1h' | '1d';
}): Promise<PortfolioHistory[]> {
  const url = getApiUrl(API_ENDPOINTS.PORTFOLIO_HISTORY);
  return get<PortfolioHistory[]>(url, { params });
}
