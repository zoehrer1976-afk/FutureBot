/**
 * Market Data Service
 * API calls for market data
 */

import { API_ENDPOINTS, getApiUrl } from '../config/api';
import type { MarketData, Kline, OrderBook } from '../types';
import { get } from './api';

export interface MarketDataParams {
  symbols?: string[];
}

export interface KlineParams {
  interval?: '1m' | '5m' | '15m' | '1h' | '4h' | '1d';
  limit?: number;
  start_time?: number;
  end_time?: number;
}

/**
 * Get market data for all or specific symbols
 */
export async function getMarketData(params?: MarketDataParams): Promise<MarketData[]> {
  const url = getApiUrl(API_ENDPOINTS.MARKET_DATA);
  return get<MarketData[]>(url, { params });
}

/**
 * Get market data for specific symbol
 */
export async function getMarketDataBySymbol(symbol: string): Promise<MarketData> {
  const url = getApiUrl(API_ENDPOINTS.MARKET_DATA_BY_SYMBOL(symbol));
  return get<MarketData>(url);
}

/**
 * Get kline/candlestick data
 */
export async function getKlines(symbol: string, params?: KlineParams): Promise<Kline[]> {
  const url = getApiUrl(API_ENDPOINTS.KLINES(symbol));
  return get<Kline[]>(url, { params });
}

/**
 * Get order book data
 */
export async function getOrderBook(symbol: string, depth: number = 20): Promise<OrderBook> {
  const url = getApiUrl(API_ENDPOINTS.ORDERBOOK(symbol));
  return get<OrderBook>(url, { params: { depth } });
}
