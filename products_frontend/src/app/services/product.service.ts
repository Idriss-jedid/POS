import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Product,
  ProductCreate,
  ProductUpdate,
  DataResponse,
  PaginatedResponse,
  ProductStatistics,
  ImportResult,
  ProductStatus,
} from '../interfaces/product.interface';

@Injectable({
  providedIn: 'root',
})
export class ProductService {
  private http = inject(HttpClient);
  private baseUrl = 'http://localhost:8000/products';

  // Signals for state management
  products = signal<Product[]>([]);
  loading = signal<boolean>(false);
  totalRecords = signal<number>(0);

  getProducts(
    skip: number = 0,
    limit: number = 10,
    search?: string,
    status?: ProductStatus,
    companyId?: number,
    categoryId?: number
  ): Observable<PaginatedResponse<Product>> {
    let params = new HttpParams().set('skip', skip.toString()).set('limit', limit.toString());

    if (search) params = params.set('search', search);
    if (status) params = params.set('status', status);
    if (companyId) params = params.set('company_id', companyId.toString());
    if (categoryId) params = params.set('category_id', categoryId.toString());

    return this.http.get<PaginatedResponse<Product>>(this.baseUrl, { params });
  }

  getProduct(id: number): Observable<DataResponse<Product>> {
    return this.http.get<DataResponse<Product>>(`${this.baseUrl}/${id}`);
  }

  createProduct(product: ProductCreate): Observable<DataResponse<Product>> {
    return this.http.post<DataResponse<Product>>(this.baseUrl, product);
  }

  updateProduct(id: number, product: ProductUpdate): Observable<DataResponse<Product>> {
    return this.http.put<DataResponse<Product>>(`${this.baseUrl}/${id}`, product);
  }

  deleteProduct(id: number): Observable<DataResponse<null>> {
    return this.http.delete<DataResponse<null>>(`${this.baseUrl}/${id}`);
  }

  getStatistics(): Observable<DataResponse<ProductStatistics>> {
    return this.http.get<DataResponse<ProductStatistics>>(`${this.baseUrl}/statistics`);
  }

  getLowStock(threshold?: number): Observable<DataResponse<Product[]>> {
    let params = new HttpParams();
    if (threshold) params = params.set('threshold', threshold.toString());
    return this.http.get<DataResponse<Product[]>>(`${this.baseUrl}/low-stock`, { params });
  }

  importCsv(file: File, companyId: number, skipDuplicates: boolean = true): Observable<DataResponse<ImportResult>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('company_id', companyId.toString());
    formData.append('skip_duplicates', skipDuplicates.toString());
    return this.http.post<DataResponse<ImportResult>>(`${this.baseUrl}/import-csv`, formData);
  }

  updateQuantity(id: number, quantityChange: number): Observable<DataResponse<Product>> {
    return this.http.patch<DataResponse<Product>>(`${this.baseUrl}/${id}/quantity`, null, {
      params: new HttpParams().set('quantity_change', quantityChange.toString()),
    });
  }
}
