import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Company,
  CompanyCreate,
  CompanyUpdate,
  DataResponse,
  PaginatedResponse,
} from '../interfaces/product.interface';

@Injectable({
  providedIn: 'root',
})
export class CompanyService {
  private http = inject(HttpClient);
  private baseUrl = 'http://localhost:8000/companies/';

  getCompanies(
    skip: number = 0,
    limit: number = 100,
    search?: string,
    isActive?: boolean
  ): Observable<PaginatedResponse<Company>> {
    let params = new HttpParams().set('skip', skip.toString()).set('limit', limit.toString());

    if (search) params = params.set('search', search);
    if (isActive !== undefined) params = params.set('is_active', isActive.toString());

    return this.http.get<PaginatedResponse<Company>>(this.baseUrl, { params });
  }

  getCompany(id: number): Observable<DataResponse<Company>> {
    return this.http.get<DataResponse<Company>>(`${this.baseUrl}/${id}`);
  }

  createCompany(company: CompanyCreate): Observable<DataResponse<Company>> {
    return this.http.post<DataResponse<Company>>(this.baseUrl, company);
  }

  updateCompany(id: number, company: CompanyUpdate): Observable<DataResponse<Company>> {
    return this.http.put<DataResponse<Company>>(`${this.baseUrl}/${id}`, company);
  }

  deleteCompany(id: number): Observable<DataResponse<null>> {
    return this.http.delete<DataResponse<null>>(`${this.baseUrl}/${id}`);
  }

  toggleActive(id: number): Observable<DataResponse<Company>> {
    return this.http.patch<DataResponse<Company>>(`${this.baseUrl}/${id}/toggle-active`, {});
  }

  getAllCompanies(): Observable<PaginatedResponse<Company>> {
    return this.getCompanies(0, 500);
  }
}
