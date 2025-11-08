/**
 * Position Service
 * API calls for position management
 */

import { API_ENDPOINTS, getApiUrl } from '../config/api';
import type { Position } from '../types';
import { get, patch, del } from './api';

export interface PositionsResponse {
  positions: Position[];
  total: number;
}

export interface UpdatePositionRequest {
  stop_loss?: number;
  take_profit?: number;
}

/**
 * Get all positions
 */
export async function getPositions(params?: {
  symbol?: string;
  limit?: number;
  offset?: number;
}): Promise<PositionsResponse> {
  const url = getApiUrl(API_ENDPOINTS.POSITIONS);
  return get<PositionsResponse>(url, { params });
}

/**
 * Get position by ID
 */
export async function getPositionById(id: string): Promise<Position> {
  const url = getApiUrl(API_ENDPOINTS.POSITION_BY_ID(id));
  return get<Position>(url);
}

/**
 * Update position (SL/TP)
 */
export async function updatePosition(
  id: string,
  data: UpdatePositionRequest
): Promise<Position> {
  const url = getApiUrl(API_ENDPOINTS.POSITION_BY_ID(id));
  return patch<Position, UpdatePositionRequest>(url, data);
}

/**
 * Close position
 */
export async function closePosition(id: string): Promise<Position> {
  const url = getApiUrl(API_ENDPOINTS.POSITION_BY_ID(id));
  return del<Position>(url);
}
