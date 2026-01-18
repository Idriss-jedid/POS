import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'products',
    pathMatch: 'full',
  },
  {
    path: 'products',
    loadComponent: () => import('./components/products/products').then((m) => m.ProductsComponent),
  },
  {
    path: 'companies',
    loadComponent: () => import('./components/companies/companies').then((m) => m.CompaniesComponent),
  },
  {
    path: 'categories',
    loadComponent: () => import('./components/categories/categories').then((m) => m.CategoriesComponent),
  },
  {
    path: '**',
    redirectTo: 'products',
  },
];
