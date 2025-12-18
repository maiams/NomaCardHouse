/**
 * API response types matching Django backend
 */

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Product types
export interface Product {
  id: string;
  name: string;
  slug: string;
  description?: string;
  brand: string;
  set_name: string;
  tcg_number?: string;
  rarity: string;
  is_active: boolean;
  min_price_brl: number | null;
  is_in_stock: boolean;
  created_at: string;
  image_url?: string | null;
}

export interface ProductSummary {
  id: string;
  name: string;
  slug: string;
  brand: string;
  set_name: string;
  rarity: string;
}

export interface SKU {
  id: string;
  sku_code: string;
  condition: string;
  language: string;
  is_foil: boolean;
  price_cents: number;
  sale_price_cents: number | null;
  price_brl: number;
  effective_price_brl: number;
  currency: string;
  is_active: boolean;
  is_in_stock: boolean;
  quantity_available: number;
  product?: ProductSummary;
}

export interface ProductDetail extends Product {
  skus: SKU[];
}

// Cart types
export interface CartItem {
  id: string;
  sku: SKU;
  quantity: number;
  unit_price_cents: number;
  unit_price_brl: number;
  line_total_cents: number;
  line_total_brl: number;
  reserved_until: string;
  is_reservation_expired: boolean;
}

export interface Cart {
  id: string;
  session_id: string;
  expires_at: string;
  is_expired: boolean;
  items: CartItem[];
  total_items: number;
  subtotal_cents: number;
  subtotal_brl: number;
}

// Order types
export interface OrderItem {
  id: string;
  sku: string;
  quantity: number;
  unit_price_cents: number;
  unit_price_brl: number;
  line_total_cents: number;
  line_total_brl: number;
  product_snapshot: Record<string, any>;
}

export interface Order {
  id: string;
  order_number: string;
  status: string;
  customer_email: string;
  customer_name: string;
  customer_cpf: string;
  customer_phone: string;
  shipping_street: string;
  shipping_number: string;
  shipping_complement?: string;
  shipping_neighborhood: string;
  shipping_city: string;
  shipping_state: string;
  shipping_cep: string;
  full_address: string;
  subtotal_cents: number;
  subtotal_brl: number;
  shipping_cents: number;
  discount_cents: number;
  total_cents: number;
  total_brl: number;
  currency: string;
  items: OrderItem[];
  total_items: number;
  notes?: string;
  tracking_code?: string;
  created_at: string;
}

// Checkout types
export interface CheckoutRequest {
  customer_email: string;
  customer_name: string;
  customer_cpf: string;
  customer_phone: string;
  shipping_street: string;
  shipping_number: string;
  shipping_complement?: string;
  shipping_neighborhood: string;
  shipping_city: string;
  shipping_state: string;
  shipping_cep: string;
  payment_method: 'PIX' | 'BOLETO' | 'CREDIT_CARD' | 'DEBIT_CARD';
  notes?: string;
}

export interface PaymentInfo {
  transaction_id: string;
  method: string;
  status: string;
  amount_brl: number;
  pix_qr_code?: string;
  pix_copy_paste?: string;
  boleto_url?: string;
  boleto_barcode?: string;
  expires_at?: string;
}

export interface CheckoutResponse {
  order: Order;
  payment: PaymentInfo;
}

// Error type
export interface APIError {
  success: false;
  error: {
    message: string;
    code: number;
    details?: Record<string, any>;
  };
}
