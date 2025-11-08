/**
 * Type definitions for FutureBot
 */

export type OrderStatus = 'pending' | 'open' | 'filled' | 'partially_filled' | 'cancelled' | 'expired';
export type OrderSide = 'buy' | 'sell';
export type OrderType = 'market' | 'limit' | 'stop' | 'stop_limit';
export type PositionSide = 'long' | 'short';

export interface Order {
  id: string;
  symbol: string;
  side: OrderSide;
  type: OrderType;
  quantity: number;
  price: number | null;
  stop_price: number | null;
  status: OrderStatus;
  filled_quantity: number;
  average_price: number | null;
  created_at: string;
  updated_at: string;
  exchange_order_id: string | null;
}

export interface Position {
  id: string;
  symbol: string;
  side: PositionSide;
  quantity: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  unrealized_pnl_percentage: number;
  stop_loss: number | null;
  take_profit: number | null;
  leverage: number;
  liquidation_price: number | null;
  opened_at: string;
  updated_at: string;
}

export interface PortfolioSummary {
  total_balance: number;
  available_balance: number;
  used_margin: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_pnl: number;
  pnl_percentage: number;
  open_positions_count: number;
  active_orders_count: number;
}

export interface PortfolioPerformance {
  daily_return: number;
  weekly_return: number;
  monthly_return: number;
  total_return: number;
  sharpe_ratio: number | null;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
}

export interface MarketData {
  symbol: string;
  last_price: number;
  bid_price: number;
  ask_price: number;
  volume_24h: number;
  price_change_24h: number;
  price_change_percentage_24h: number;
  high_24h: number;
  low_24h: number;
  timestamp: string;
}

export interface Kline {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OrderBookEntry {
  price: number;
  quantity: number;
}

export interface OrderBook {
  symbol: string;
  bids: OrderBookEntry[];
  asks: OrderBookEntry[];
  timestamp: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  detail: string;
  status_code: number;
}
