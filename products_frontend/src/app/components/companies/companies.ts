import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

// PrimeNG
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { DialogModule } from 'primeng/dialog';
import { ToastModule } from 'primeng/toast';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { TextareaModule } from 'primeng/textarea';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { MessageService, ConfirmationService } from 'primeng/api';

import { CompanyService } from '../../services/company.service';
import { Company, CompanyCreate } from '../../interfaces/product.interface';

@Component({
  selector: 'app-companies',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    TableModule,
    ButtonModule,
    InputTextModule,
    DialogModule,
    ToastModule,
    ConfirmDialogModule,
    TagModule,
    TooltipModule,
    TextareaModule,
    ToggleSwitchModule,
  ],
  providers: [MessageService, ConfirmationService],
  templateUrl: './companies.html',
  styleUrl: './companies.css',
})
export class CompaniesComponent implements OnInit {
  private companyService = inject(CompanyService);
  private messageService = inject(MessageService);
  private confirmationService = inject(ConfirmationService);
  private fb = inject(FormBuilder);

  companies = signal<Company[]>([]);
  loading = signal<boolean>(false);
  totalRecords = signal<number>(0);
  rows = 10;
  first = 0;

  searchValue = '';
  showDialog = signal<boolean>(false);
  editingCompany = signal<Company | null>(null);
  companyForm!: FormGroup;

  ngOnInit(): void {
    this.initForm();
    this.loadCompanies();
  }

  initForm(): void {
    this.companyForm = this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(255)]],
      code: ['', [Validators.required, Validators.maxLength(50)]],
      email: ['', [Validators.email]],
      phone: [''],
      address: [''],
      website: [''],
      contact_person: [''],
      description: [''],
      is_active: [true],
    });
  }

  loadCompanies(): void {
    this.loading.set(true);
    this.companyService.getCompanies(this.first, this.rows, this.searchValue || undefined).subscribe({
      next: (response) => {
        this.companies.set(response.data);
        this.totalRecords.set(response.total);
        this.loading.set(false);
      },
      error: () => {
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to load companies' });
        this.loading.set(false);
      },
    });
  }

  onPageChange(event: any): void {
    this.first = event.first;
    this.rows = event.rows;
    this.loadCompanies();
  }

  onFilter(): void {
    this.first = 0;
    this.loadCompanies();
  }

  openAddDialog(): void {
    this.editingCompany.set(null);
    this.companyForm.reset({ is_active: true });
    this.showDialog.set(true);
  }

  openEditDialog(company: Company): void {
    this.editingCompany.set(company);
    this.companyForm.patchValue({
      name: company.name,
      code: company.code,
      email: company.email,
      phone: company.phone,
      address: company.address,
      website: company.website,
      contact_person: company.contact_person,
      description: company.description,
      is_active: company.is_active,
    });
    this.showDialog.set(true);
  }

  saveCompany(): void {
    if (this.companyForm.invalid) {
      this.companyForm.markAllAsTouched();
      return;
    }

    const formData = { ...this.companyForm.value };
    Object.keys(formData).forEach((key) => {
      if (formData[key] === '' || formData[key] === null) delete formData[key];
    });

    if (this.editingCompany()) {
      this.companyService.updateCompany(this.editingCompany()!.id, formData).subscribe({
        next: () => {
          this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Company updated' });
          this.showDialog.set(false);
          this.loadCompanies();
        },
        error: () => {
          this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to update company' });
        },
      });
    } else {
      this.companyService.createCompany(formData as CompanyCreate).subscribe({
        next: () => {
          this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Company created' });
          this.showDialog.set(false);
          this.loadCompanies();
        },
        error: () => {
          this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to create company' });
        },
      });
    }
  }

  confirmDelete(company: Company): void {
    this.confirmationService.confirm({
      message: `Are you sure you want to delete "${company.name}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: () => this.deleteCompany(company.id),
    });
  }

  deleteCompany(id: number): void {
    this.companyService.deleteCompany(id).subscribe({
      next: () => {
        this.messageService.add({ severity: 'success', summary: 'Deleted', detail: 'Company deleted' });
        this.loadCompanies();
      },
      error: () => {
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete company' });
      },
    });
  }

  toggleActive(company: Company): void {
    this.companyService.toggleActive(company.id).subscribe({
      next: () => {
        this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Status updated' });
        this.loadCompanies();
      },
    });
  }

  hasError(field: string, error: string): boolean {
    const control = this.companyForm.get(field);
    return !!(control?.touched && control?.hasError(error));
  }
}
