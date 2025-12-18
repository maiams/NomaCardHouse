/**
 * Typed API client for Noma Card House backend
 * Automatically injects X-Session-ID header for cart operations
 */

import { getSessionId, refreshSession } from './session';
import type {
  APIResponse,
  PaginatedResponse,
  Product,
  ProductDetail,
  Cart,
  CheckoutRequest,
  CheckoutResponse,
  APIError,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Custom API error class
 */
export class APIClientError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'APIClientError';
  }
}

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
  includeSessionId = false
): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Inject X-Session-ID for cart operations
  if (includeSessionId && typeof window !== 'undefined') {
    const sessionId = getSessionId();
    if (sessionId) {
      headers['X-Session-ID'] = sessionId;
      refreshSession(); // Extend session on each request
    }
  }

  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle HTTP errors
    if (!response.ok) {
      let errorData: APIError | null = null;

      try {
        errorData = await response.json();
      } catch {
        // Response is not JSON
      }

      throw new APIClientError(
        errorData?.error?.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData?.error?.details
      );
    }

    // Parse successful response
    const data = await response.json();
    return data as T;
  } catch (error) {
    if (error instanceof APIClientError) {
      throw error;
    }

    // Network or parsing error
    throw new APIClientError(
      error instanceof Error ? error.message : 'Network error',
      0
    );
  }
}

/**
 * API Client
 */
export const api = {
  // Products
  products: {
    list: async (params?: {
      search?: string;
      brand?: string;
      set_name?: string;
      rarity?: string;
      page?: number;
    }) => {
      const query = new URLSearchParams();
      if (params?.search) query.append('search', params.search);
      if (params?.brand) query.append('brand', params.brand);
      if (params?.set_name) query.append('set_name', params.set_name);
      if (params?.rarity) query.append('rarity', params.rarity);
      if (params?.page) query.append('page', params.page.toString());

      const queryString = query.toString();
      const endpoint = `/products/${queryString ? `?${queryString}` : ''}`;

      return apiFetch<PaginatedResponse<Product>>(endpoint);
    },

    get: async (slug: string) => {
      return apiFetch<APIResponse<ProductDetail>>(`/products/${slug}/`);
    },
  },

  // Cart
  cart: {
    get: async () => {
      return apiFetch<APIResponse<Cart>>('/cart/', {}, true);
    },

    addItem: async (skuId: string, quantity: number) => {
      return apiFetch<APIResponse<Cart>>(
        '/cart/add_item/',
        {
          method: 'POST',
          body: JSON.stringify({ sku_id: skuId, quantity }),
        },
        true
      );
    },

    updateItem: async (itemId: string, quantity: number) => {
      return apiFetch<APIResponse<Cart>>(
        `/cart/items/${itemId}/`,
        {
          method: 'PATCH',
          body: JSON.stringify({ quantity }),
        },
        true
      );
    },

    removeItem: async (itemId: string) => {
      return apiFetch<APIResponse<Cart>>(
        `/cart/items/${itemId}/`,
        {
          method: 'DELETE',
        },
        true
      );
    },

    clear: async () => {
      return apiFetch<APIResponse<Cart>>(
        '/cart/clear/',
        {
          method: 'POST',
        },
        true
      );
    },
  },

  // Orders
  orders: {
    checkout: async (data: CheckoutRequest) => {
      return apiFetch<APIResponse<CheckoutResponse>>(
        '/orders/checkout/',
        {
          method: 'POST',
          body: JSON.stringify(data),
        },
        true
      );
    },

    get: async (orderNumber: string) => {
      return apiFetch<APIResponse<any>>(`/orders/${orderNumber}/`);
    },

    list: async () => {
      return apiFetch<PaginatedResponse<any>>('/orders/');
    },
  },
};

export default api;
