/**
 * API Configuration
 * Centralized API endpoint configuration
 */

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  API_V1_PREFIX: '/api/v1',
  TIMEOUT: 30000, // 30 seconds
} as const;

export const API_ENDPOINTS = {
  // Orders
  ORDERS: '/orders',
  ORDER_BY_ID: (id: string) => `/orders/${id}`,

  // Positions
  POSITIONS: '/positions',
  POSITION_BY_ID: (id: string) => `/positions/${id}`,

  // Portfolio
  PORTFOLIO_SUMMARY: '/portfolio/summary',
  PORTFOLIO_HISTORY: '/portfolio/history',
  PORTFOLIO_PERFORMANCE: '/portfolio/performance',

  // Market Data
  MARKET_DATA: '/market-data',
  MARKET_DATA_BY_SYMBOL: (symbol: string) => `/market-data/${symbol}`,
  KLINES: (symbol: string) => `/market-data/${symbol}/klines`,
  ORDERBOOK: (symbol: string) => `/market-data/${symbol}/orderbook`,

  // Health
  HEALTH: '/health',
  ROOT: '/',
} as const;

/**
 * Get full API URL
 */
export function getApiUrl(endpoint: string): string {
  return `${API_CONFIG.BASE_URL}${API_CONFIG.API_V1_PREFIX}${endpoint}`;
}

/**
 * Get base URL (for health/root endpoints)
 */
export function getBaseUrl(endpoint: string): string {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
}
