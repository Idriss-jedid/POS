import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

// PrimeNG
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { DialogModule } from 'primeng/dialog';
import { ToastModule } from 'primeng/toast';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { TextareaModule } from 'primeng/textarea';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { MessageService, ConfirmationService } from 'primeng/api';

import { CategoryService } from '../../services/category.service';
import { Category, CategoryCreate, CategoryType } from '../../interfaces/product.interface';

@Component({
  selector: 'app-categories',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    TableModule,
    ButtonModule,
    InputTextModule,
    SelectModule,
    DialogModule,
    ToastModule,
    ConfirmDialogModule,
    TagModule,
    TooltipModule,
    TextareaModule,
    ToggleSwitchModule,
  ],
  providers: [MessageService, ConfirmationService],
  templateUrl: './categories.html',
  styleUrl: './categories.css',
})
export class CategoriesComponent implements OnInit {
  private categoryService = inject(CategoryService);
  private messageService = inject(MessageService);
  private confirmationService = inject(ConfirmationService);
  private fb = inject(FormBuilder);

  categories = signal<Category[]>([]);
  loading = signal<boolean>(false);
  totalRecords = signal<number>(0);
  rows = 10;
  first = 0;

  selectedType: CategoryType | null = null;
  showDialog = signal<boolean>(false);
  editingCategory = signal<Category | null>(null);
  categoryForm!: FormGroup;

  categoryTypeOptions: { label: string; value: CategoryType }[] = [
    { label: 'Electronics', value: 'ELECTRONICS' },
    { label: 'Clothing', value: 'CLOTHING' },
    { label: 'Food & Beverage', value: 'FOOD_BEVERAGE' },
    { label: 'Home & Garden', value: 'HOME_GARDEN' },
    { label: 'Health & Beauty', value: 'HEALTH_BEAUTY' },
    { label: 'Sports & Outdoors', value: 'SPORTS_OUTDOORS' },
    { label: 'Toys & Games', value: 'TOYS_GAMES' },
    { label: 'Books & Media', value: 'BOOKS_MEDIA' },
    { label: 'Automotive', value: 'AUTOMOTIVE' },
    { label: 'Office Supplies', value: 'OFFICE_SUPPLIES' },
    { label: 'Other', value: 'OTHER' },
  ];

  filterOptions = [{ label: 'All Types', value: null }, ...this.categoryTypeOptions];

  ngOnInit(): void {
    this.initForm();
    this.loadCategories();
  }

  initForm(): void {
    this.categoryForm = this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(255)]],
      code: ['', [Validators.required, Validators.maxLength(50)]],
      category_type: ['OTHER', Validators.required],
      description: [''],
      is_active: [true],
    });
  }

  loadCategories(): void {
    this.loading.set(true);
    this.categoryService.getCategories(this.first, this.rows, this.selectedType || undefined).subscribe({
      next: (response) => {
        this.categories.set(response.data);
        this.totalRecords.set(response.total);
        this.loading.set(false);
      },
      error: () => {
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to load categories' });
        this.loading.set(false);
      },
    });
  }

  onPageChange(event: any): void {
    this.first = event.first;
    this.rows = event.rows;
    this.loadCategories();
  }

  onFilter(): void {
    this.first = 0;
    this.loadCategories();
  }

  openAddDialog(): void {
    this.editingCategory.set(null);
    this.categoryForm.reset({ category_type: 'OTHER', is_active: true });
    this.showDialog.set(true);
  }

  openEditDialog(category: Category): void {
    this.editingCategory.set(category);
    this.categoryForm.patchValue({
      name: category.name,
      code: category.code,
      category_type: category.category_type,
      description: category.description,
      is_active: category.is_active,
    });
    this.showDialog.set(true);
  }

  saveCategory(): void {
    if (this.categoryForm.invalid) {
      this.categoryForm.markAllAsTouched();
      return;
    }

    const formData = { ...this.categoryForm.value };
    Object.keys(formData).forEach((key) => {
      if (formData[key] === '' || formData[key] === null) delete formData[key];
    });

    if (this.editingCategory()) {
      this.categoryService.updateCategory(this.editingCategory()!.id, formData).subscribe({
        next: () => {
          this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Category updated' });
          this.showDialog.set(false);
          this.loadCategories();
        },
        error: () => {
          this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to update category' });
        },
      });
    } else {
      this.categoryService.createCategory(formData as CategoryCreate).subscribe({
        next: () => {
          this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Category created' });
          this.showDialog.set(false);
          this.loadCategories();
        },
        error: () => {
          this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to create category' });
        },
      });
    }
  }

  confirmDelete(category: Category): void {
    this.confirmationService.confirm({
      message: `Are you sure you want to delete "${category.name}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: () => this.deleteCategory(category.id),
    });
  }

  deleteCategory(id: number): void {
    this.categoryService.deleteCategory(id).subscribe({
      next: () => {
        this.messageService.add({ severity: 'success', summary: 'Deleted', detail: 'Category deleted' });
        this.loadCategories();
      },
      error: () => {
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete category' });
      },
    });
  }

  toggleActive(category: Category): void {
    this.categoryService.toggleActive(category.id).subscribe({
      next: () => {
        this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Status updated' });
        this.loadCategories();
      },
    });
  }

  getCategoryTypeLabel(type: CategoryType): string {
    return this.categoryTypeOptions.find((t) => t.value === type)?.label || type;
  }

  hasError(field: string, error: string): boolean {
    const control = this.categoryForm.get(field);
    return !!(control?.touched && control?.hasError(error));
  }
}
