import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

// PrimeNG
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { DialogModule } from 'primeng/dialog';
import { ToastModule } from 'primeng/toast';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { FileUploadModule } from 'primeng/fileupload';
import { TextareaModule } from 'primeng/textarea';
import { MessageService, ConfirmationService } from 'primeng/api';

import { ProductService } from '../../services/product.service';
import { CompanyService } from '../../services/company.service';
import { CategoryService } from '../../services/category.service';
import {
  Product,
  ProductCreate,
  Company,
  Category,
  ProductStatus,
  UnitType,
} from '../../interfaces/product.interface';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    TableModule,
    ButtonModule,
    InputTextModule,
    InputNumberModule,
    SelectModule,
    DialogModule,
    ToastModule,
    ConfirmDialogModule,
    TagModule,
    TooltipModule,
    FileUploadModule,
    TextareaModule,
  ],
  providers: [MessageService, ConfirmationService],
  templateUrl: './products.html',
  styleUrl: './products.css',
})
export class ProductsComponent implements OnInit {
  private productService = inject(ProductService);
  private companyService = inject(CompanyService);
  private categoryService = inject(CategoryService);
  private messageService = inject(MessageService);
  private confirmationService = inject(ConfirmationService);
  private fb = inject(FormBuilder);

  // Data
  products = signal<Product[]>([]);
  companies = signal<Company[]>([]);
  categories = signal<Category[]>([]);

  // State
  loading = signal<boolean>(false);
  totalRecords = signal<number>(0);
  rows = 10;
  first = 0;

  // Filters
  searchValue = '';
  selectedStatus: ProductStatus | null = null;
  selectedCompany: number | null = null;
  selectedCategory: number | null = null;

  // Dialogs
  showDialog = signal<boolean>(false);
  showImportDialog = signal<boolean>(false);
  editingProduct = signal<Product | null>(null);
  productForm!: FormGroup;

  // Import form fields
  importCompanyId: number | null = null;
  importFile: File | null = null;

  // Options
  statusOptions = [
    { label: 'All Status', value: null },
    { label: 'Active', value: 'ACTIVE' },
    { label: 'Inactive', value: 'INACTIVE' },
    { label: 'Out of Stock', value: 'OUT_OF_STOCK' },
    { label: 'Discontinued', value: 'DISCONTINUED' },
    { label: 'Pending', value: 'PENDING' },
  ];

  unitOptions: { label: string; value: UnitType }[] = [
    { label: 'Piece', value: 'PIECE' },
    { label: 'Kilogram', value: 'KG' },
    { label: 'Gram', value: 'GRAM' },
    { label: 'Liter', value: 'LITER' },
    { label: 'Milliliter', value: 'ML' },
    { label: 'Meter', value: 'METER' },
    { label: 'Centimeter', value: 'CM' },
    { label: 'Box', value: 'BOX' },
    { label: 'Pack', value: 'PACK' },
    { label: 'Dozen', value: 'DOZEN' },
  ];

  statusFormOptions = [
    { label: 'Active', value: 'ACTIVE' },
    { label: 'Inactive', value: 'INACTIVE' },
    { label: 'Out of Stock', value: 'OUT_OF_STOCK' },
    { label: 'Discontinued', value: 'DISCONTINUED' },
    { label: 'Pending', value: 'PENDING' },
  ];

  ngOnInit(): void {
    this.initForm();
    this.loadProducts();
    this.loadCompanies();
    this.loadCategories();
  }

  initForm(): void {
    this.productForm = this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(255)]],
      sku: ['', [Validators.required, Validators.maxLength(100)]],
      barcode: [''],
      description: [''],
      cost_price: [0, [Validators.required, Validators.min(0)]],
      selling_price: [0, [Validators.required, Validators.min(0)]],
      quantity: [0, [Validators.required, Validators.min(0)]],
      min_stock_level: [10, [Validators.required, Validators.min(0)]],
      max_stock_level: [null],
      unit: ['PIECE', Validators.required],
      status: ['ACTIVE', Validators.required],
      company_id: [null, Validators.required],
      category_id: [null, Validators.required],
      brand: [''],
      notes: [''],
    });
  }

  loadProducts(): void {
    this.loading.set(true);

    this.productService
      .getProducts(
        this.first,
        this.rows,
        this.searchValue || undefined,
        this.selectedStatus || undefined,
        this.selectedCompany || undefined,
        this.selectedCategory || undefined
      )
      .subscribe({
        next: (response) => {
          this.products.set(response.data);
          this.totalRecords.set(response.total);
          this.loading.set(false);
        },
        error: () => {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load products',
          });
          this.loading.set(false);
        },
      });
  }

  loadCompanies(): void {
    this.companyService.getAllCompanies().subscribe({
      next: (response) => {
        this.companies.set(response.data);
      },
    });
  }

  loadCategories(): void {
    this.categoryService.getAllCategories().subscribe({
      next: (response) => {
        this.categories.set(response.data);
      },
    });
  }

  onPageChange(event: any): void {
    this.first = event.first;
    this.rows = event.rows;
    this.loadProducts();
  }

  onFilter(): void {
    this.first = 0;
    this.loadProducts();
  }

  clearFilters(): void {
    this.searchValue = '';
    this.selectedStatus = null;
    this.selectedCompany = null;
    this.selectedCategory = null;
    this.first = 0;
    this.loadProducts();
  }

  openAddDialog(): void {
    this.editingProduct.set(null);
    this.productForm.reset({
      cost_price: 0,
      selling_price: 0,
      quantity: 0,
      min_stock_level: 10,
      unit: 'PIECE',
      status: 'ACTIVE',
    });
    this.showDialog.set(true);
  }

  openEditDialog(product: Product): void {
    this.editingProduct.set(product);
    this.productForm.patchValue({
      name: product.name,
      sku: product.sku,
      barcode: product.barcode,
      description: product.description,
      cost_price: product.cost_price,
      selling_price: product.selling_price,
      quantity: product.quantity,
      min_stock_level: product.min_stock_level,
      max_stock_level: product.max_stock_level,
      unit: product.unit,
      status: product.status,
      company_id: product.company_id,
      category_id: product.category_id,
      brand: product.brand,
      notes: product.notes,
    });
    this.showDialog.set(true);
  }

  saveProduct(): void {
    if (this.productForm.invalid) {
      this.productForm.markAllAsTouched();
      return;
    }

    const formData = { ...this.productForm.value };

    // Clean up empty values
    Object.keys(formData).forEach((key) => {
      if (formData[key] === '' || formData[key] === null) {
        delete formData[key];
      }
    });

    if (this.editingProduct()) {
      this.productService.updateProduct(this.editingProduct()!.id, formData).subscribe({
        next: () => {
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Product updated successfully',
          });
          this.showDialog.set(false);
          this.loadProducts();
        },
        error: () => {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to update product',
          });
        },
      });
    } else {
      this.productService.createProduct(formData as ProductCreate).subscribe({
        next: () => {
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Product created successfully',
          });
          this.showDialog.set(false);
          this.loadProducts();
        },
        error: () => {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to create product',
          });
        },
      });
    }
  }

  confirmDelete(product: Product): void {
    this.confirmationService.confirm({
      message: `Are you sure you want to delete "${product.name}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: () => {
        this.deleteProduct(product.id);
      },
    });
  }

  deleteProduct(id: number): void {
    this.productService.deleteProduct(id).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: 'Deleted',
          detail: 'Product deleted successfully',
        });
        this.loadProducts();
      },
      error: () => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete product',
        });
      },
    });
  }

  // Import CSV
  onFileSelect(event: any): void {
    const file = event.files[0];
    if (file) {
      this.importFile = file;
    }
  }

  uploadImport(): void {
    if (!this.importFile) {
      this.messageService.add({
        severity: 'warn',
        summary: 'No File',
        detail: 'Please select a CSV file to upload',
      });
      return;
    }

    if (!this.importCompanyId) {
      this.messageService.add({
        severity: 'warn',
        summary: 'No Company',
        detail: 'Please select a company',
      });
      return;
    }

    this.productService.importCsv(this.importFile, this.importCompanyId).subscribe({
      next: (response) => {
        const result = response.data;
        const severity = result.failed > 0 ? 'warn' : 'success';
        this.messageService.add({
          severity: severity,
          summary: result.failed > 0 ? 'Import Completed with Errors' : 'Import Complete',
          detail: `Imported ${result.successful} products. Skipped: ${result.skipped}. Failed: ${result.failed}.`,
          life: 5000
        });

        // Show errors if any
        if (result.errors && result.errors.length > 0) {
          console.log('Import errors:', result.errors);
          // Show first few errors in toast
          const errorSummary = result.errors.slice(0, 3).join('; ');
          if (result.errors.length > 3) {
            this.messageService.add({
              severity: 'error',
              summary: 'Import Errors',
              detail: `${errorSummary}... and ${result.errors.length - 3} more errors. Check console for details.`,
              life: 10000
            });
          } else if (result.errors.length > 0) {
            this.messageService.add({
              severity: 'error',
              summary: 'Import Errors',
              detail: errorSummary,
              life: 10000
            });
          }
        }

        this.showImportDialog.set(false);
        this.resetImportForm();
        this.loadProducts();
      },
      error: (err) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Import Failed',
          detail: err.error?.detail || 'Failed to import file',
        });
      },
    });
  }

  resetImportForm(): void {
    this.importFile = null;
    this.importCompanyId = null;
  }

  closeImportDialog(): void {
    this.showImportDialog.set(false);
    this.resetImportForm();
  }

  downloadTemplate(): void {
    const headers = ['name', 'sku', 'category_id', 'description', 'selling_price', 'quantity'];
    const example = ['Sample Product', 'SKU001', '1', 'Product description', '15.00', '100'];

    const csv = [headers.join(','), example.join(',')].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'products_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  }

  getStatusSeverity(status: ProductStatus): 'success' | 'info' | 'warn' | 'danger' | 'secondary' {
    switch (status) {
      case 'ACTIVE': return 'success';
      case 'INACTIVE': return 'secondary';
      case 'OUT_OF_STOCK': return 'danger';
      case 'DISCONTINUED': return 'warn';
      case 'PENDING': return 'info';
      default: return 'info';
    }
  }

  getCompanyName(companyId: number): string {
    return this.companies().find((c) => c.id === companyId)?.name || 'N/A';
  }

  getCategoryName(categoryId: number): string {
    return this.categories().find((c) => c.id === categoryId)?.name || 'N/A';
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
  }

  hasError(field: string, error: string): boolean {
    const control = this.productForm.get(field);
    return !!(control?.touched && control?.hasError(error));
  }
}
