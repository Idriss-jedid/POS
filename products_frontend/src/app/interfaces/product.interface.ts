// Product Interfaces
export interface Product {
  id: number;
  name: string;
  sku: string;
  barcode?: string;
  description?: string;
  cost_price: number;
  selling_price: number;
  quantity: number;
  min_stock_level: number;
  max_stock_level?: number;
  unit: UnitType;
  status: ProductStatus;
  company_id: number;
  category_id: number;
  brand?: string;
  weight?: number;
  dimensions?: string;
  image_url?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  company?: Company;
  category?: Category;
}

export interface ProductCreate {
  name: string;
  sku: string;
  barcode?: string;
  description?: string;
  cost_price: number;
  selling_price: number;
  quantity: number;
  min_stock_level: number;
  max_stock_level?: number;
  unit: UnitType;
  status?: ProductStatus;
  company_id: number;
  category_id: number;
  brand?: string;
  weight?: number;
  dimensions?: string;
  image_url?: string;
  notes?: string;
}

export interface ProductUpdate {
  name?: string;
  sku?: string;
  barcode?: string;
  description?: string;
  cost_price?: number;
  selling_price?: number;
  quantity?: number;
  min_stock_level?: number;
  max_stock_level?: number;
  unit?: UnitType;
  status?: ProductStatus;
  company_id?: number;
  category_id?: number;
  brand?: string;
  weight?: number;
  dimensions?: string;
  image_url?: string;
  notes?: string;
}

// Company Interfaces
export interface Company {
  id: number;
  name: string;
  code: string;
  email?: string;
  phone?: string;
  address?: string;
  website?: string;
  contact_person?: string;
  is_active: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
  product_count?: number;
}

export interface CompanyCreate {
  name: string;
  code: string;
  email?: string;
  phone?: string;
  address?: string;
  website?: string;
  contact_person?: string;
  is_active?: boolean;
  description?: string;
}

export interface CompanyUpdate {
  name?: string;
  code?: string;
  email?: string;
  phone?: string;
  address?: string;
  website?: string;
  contact_person?: string;
  is_active?: boolean;
  description?: string;
}

// Category Interfaces
export interface Category {
  id: number;
  name: string;
  code: string;
  category_type: CategoryType;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  product_count?: number;
}

export interface CategoryCreate {
  name: string;
  code: string;
  category_type: CategoryType;
  description?: string;
  is_active?: boolean;
}

export interface CategoryUpdate {
  name?: string;
  code?: string;
  category_type?: CategoryType;
  description?: string;
  is_active?: boolean;
}

// Enums
export type ProductStatus = 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED' | 'OUT_OF_STOCK' | 'PENDING';

export type UnitType = 'PIECE' | 'KG' | 'GRAM' | 'LITER' | 'ML' | 'METER' | 'CM' | 'BOX' | 'PACK' | 'DOZEN';

export type CategoryType =
  | 'ELECTRONICS'
  | 'CLOTHING'
  | 'FOOD_BEVERAGE'
  | 'HOME_GARDEN'
  | 'HEALTH_BEAUTY'
  | 'SPORTS_OUTDOORS'
  | 'TOYS_GAMES'
  | 'BOOKS_MEDIA'
  | 'AUTOMOTIVE'
  | 'OFFICE_SUPPLIES'
  | 'OTHER';

// API Response
export interface DataResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  success: boolean;
  message: string;
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Statistics
export interface ProductStatistics {
  total_products: number;
  active_products: number;
  out_of_stock: number;
  low_stock: number;
  total_value: number;
  total_cost: number;
  by_status: Record<string, number>;
  by_category: Record<number, number>;
  by_company: Record<number, number>;
}

// CSV Import
export interface ImportResult {
  total_rows: number;
  successful: number;
  failed: number;
  skipped: number;
  errors: string[];
  created_product_ids: number[];
}
