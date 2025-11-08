/**
 * Order Service
 * API calls for order management
 */

import { API_ENDPOINTS, getApiUrl } from '../config/api';
import type { Order, OrderSide, OrderType } from '../types';
import { get, post, del } from './api';

export interface CreateOrderRequest {
  symbol: string;
  side: OrderSide;
  type: OrderType;
  quantity: number;
  price?: number;
  stop_price?: number;
  time_in_force?: string;
}

export interface OrdersResponse {
  orders: Order[];
  total: number;
}

/**
 * Get all orders
 */
export async function getOrders(params?: {
  symbol?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<OrdersResponse> {
  const url = getApiUrl(API_ENDPOINTS.ORDERS);
  return get<OrdersResponse>(url, { params });
}

/**
 * Get order by ID
 */
export async function getOrderById(id: string): Promise<Order> {
  const url = getApiUrl(API_ENDPOINTS.ORDER_BY_ID(id));
  return get<Order>(url);
}

/**
 * Create new order
 */
export async function createOrder(data: CreateOrderRequest): Promise<Order> {
  const url = getApiUrl(API_ENDPOINTS.ORDERS);
  return post<Order, CreateOrderRequest>(url, data);
}

/**
 * Cancel order
 */
export async function cancelOrder(id: string): Promise<Order> {
  const url = getApiUrl(API_ENDPOINTS.ORDER_BY_ID(id));
  return del<Order>(url);
}
