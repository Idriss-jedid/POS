import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Category,
  CategoryCreate,
  CategoryUpdate,
  CategoryType,
  DataResponse,
  PaginatedResponse,
} from '../interfaces/product.interface';

@Injectable({
  providedIn: 'root',
})
export class CategoryService {
  private http = inject(HttpClient);
  private baseUrl = 'http://localhost:8000/categories/';

  getCategories(
    skip: number = 0,
    limit: number = 100,
    categoryType?: CategoryType,
    isActive?: boolean
  ): Observable<PaginatedResponse<Category>> {
    let params = new HttpParams().set('skip', skip.toString()).set('limit', limit.toString());

    if (categoryType) params = params.set('category_type', categoryType);
    if (isActive !== undefined) params = params.set('is_active', isActive.toString());

    return this.http.get<PaginatedResponse<Category>>(this.baseUrl, { params });
  }

  getCategory(id: number): Observable<DataResponse<Category>> {
    return this.http.get<DataResponse<Category>>(`${this.baseUrl}/${id}`);
  }

  createCategory(category: CategoryCreate): Observable<DataResponse<Category>> {
    return this.http.post<DataResponse<Category>>(this.baseUrl, category);
  }

  updateCategory(id: number, category: CategoryUpdate): Observable<DataResponse<Category>> {
    return this.http.put<DataResponse<Category>>(`${this.baseUrl}/${id}`, category);
  }

  deleteCategory(id: number): Observable<DataResponse<null>> {
    return this.http.delete<DataResponse<null>>(`${this.baseUrl}/${id}`);
  }

  toggleActive(id: number): Observable<DataResponse<Category>> {
    return this.http.patch<DataResponse<Category>>(`${this.baseUrl}/${id}/toggle-active`, {});
  }

  getAllCategories(): Observable<PaginatedResponse<Category>> {
    return this.getCategories(0, 500);
  }
}
