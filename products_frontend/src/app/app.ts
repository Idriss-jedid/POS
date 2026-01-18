import { Component, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

// PrimeNG
import { MenubarModule } from 'primeng/menubar';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, MenubarModule, ButtonModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  menuItems = [
    {
      label: 'Dashboard',
      icon: 'pi pi-home',
      routerLink: '/',
    },
    {
      label: 'Products',
      icon: 'pi pi-box',
      routerLink: '/products',
    },
    {
      label: 'Companies',
      icon: 'pi pi-building',
      routerLink: '/companies',
    },
    {
      label: 'Categories',
      icon: 'pi pi-tags',
      routerLink: '/categories',
    },
  ];
}
