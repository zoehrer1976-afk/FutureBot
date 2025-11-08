/**
 * API Client
 * Base axios configuration and interceptors
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import { API_CONFIG, getApiUrl, getBaseUrl } from '../config/api';
import type { ApiError } from '../types';

/**
 * Create axios instance with default config
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor
 * Add authentication tokens, etc.
 */
apiClient.interceptors.request.use(
  (config) => {
    // TODO: Add auth token when implemented
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor
 * Handle errors globally
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response) {
      // Server responded with error
      const apiError: ApiError = {
        detail: error.response.data?.detail || 'An error occurred',
        status_code: error.response.status,
      };
      console.error('API Error:', apiError);
      return Promise.reject(apiError);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
      return Promise.reject({
        detail: 'Network error. Please check your connection.',
        status_code: 0,
      });
    } else {
      // Something else happened
      console.error('Error:', error.message);
      return Promise.reject({
        detail: error.message,
        status_code: 0,
      });
    }
  }
);

/**
 * Generic GET request
 */
export async function get<T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.get<T>(endpoint, config);
  return response.data;
}

/**
 * Generic POST request
 */
export async function post<T, D = unknown>(
  endpoint: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.post<T>(endpoint, data, config);
  return response.data;
}

/**
 * Generic PUT request
 */
export async function put<T, D = unknown>(
  endpoint: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.put<T>(endpoint, data, config);
  return response.data;
}

/**
 * Generic DELETE request
 */
export async function del<T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.delete<T>(endpoint, config);
  return response.data;
}

/**
 * Generic PATCH request
 */
export async function patch<T, D = unknown>(
  endpoint: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.patch<T>(endpoint, data, config);
  return response.data;
}

export { apiClient, getApiUrl, getBaseUrl };
