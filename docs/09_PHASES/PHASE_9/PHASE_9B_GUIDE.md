---
title: "Phase 9B - Core Components Implementation Guide"
description: "This guide documents the manual steps needed to complete Phase 9B since the `frontend/` directory is in `.gitignore`."

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Project Manager
    - CTO / Technical Lead
  secondary:
    - All

applicable_phases:
  primary:
    - Development

tags:
  - phase-9
  - core
  - guide
  - phase

status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"

estimated_read_time: "10 minutes"

version: "1.0"
last_updated: "2025-12-06"
last_reviewed: "2025-12-06"
review_frequency: "quarterly"

author: "Development Team"
maintainer: "Development Team"

related: []
see_also: []
depends_on: []
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "2025-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# Phase 9B - Core Components Implementation Guide

## Overview
This guide documents the manual steps needed to complete Phase 9B since the `frontend/` directory is in `.gitignore`.

## shadcn/ui Components Installation

Run from `frontend/` directory:
```bash
npx shadcn@latest add button card input label form toast alert badge skeleton dialog dropdown-menu separator avatar
```

This will create `frontend/src/components/ui/` with all shadcn/ui components.

## Files to Create

### 1. Utility Functions

**File:** `frontend/src/lib/utils.ts`
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const d = new Date(date)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric', month: 'short', day: 'numeric'
  }).format(d)
}

export function formatDateTime(date: string | Date): string {
  const d = new Date(date)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  }).format(d)
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}
```

### 2. API Client Service

**File:** `frontend/src/services/api.ts`
```typescript
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        })

        const { access } = response.data
        localStorage.setItem('access_token', access)

        originalRequest.headers.Authorization = `Bearer ${access}`
        return api(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// API methods
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login/', { email, password }),
  
  register: (email: string, password: string, full_name: string) =>
    api.post('/auth/register/', { email, password, full_name }),
  
  logout: () => api.post('/auth/logout/'),
  
  me: () => api.get('/auth/me/'),
}

export const projectsAPI = {
  list: () => api.get('/projects/'),
  get: (id: string) => api.get(`/projects/${id}/`),
  create: (data: any) => api.post('/projects/', data),
  update: (id: string, data: any) => api.patch(`/projects/${id}/`, data),
  delete: (id: string) => api.delete(`/projects/${id}/`),
}

export const agentsAPI = {
  list: () => api.get('/agents/'),
  get: (id: string) => api.get(`/agents/${id}/`),
}

export const workflowsAPI = {
  list: () => api.get('/workflows/'),
  get: (id: string) => api.get(`/workflows/${id}/`),
  execute: (id: string, data: any) => api.post(`/workflows/${id}/execute/`, data),
}

export const commandsAPI = {
  list: () => api.get('/commands/'),
  get: (id: string) => api.get(`/commands/${id}/`),
  execute: (id: string, data: any) => api.post(`/commands/${id}/execute/`, data),
  preview: (id: string, data: any) => api.post(`/commands/${id}/preview/`, data),
}
```

### 3. Authentication Store (Zustand)

**File:** `frontend/src/stores/authStore.ts`
```typescript
import { create } from 'zustand'
import { authAPI } from '@/services/api'

interface User {
  id: string
  email: string
  full_name: string
  role: string
}

interface AuthStore {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, full_name: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authAPI.login(email, password)
      const { access, refresh, user } = response.data

      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)

      set({
        user,
        token: access,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Login failed',
        isLoading: false,
      })
      throw error
    }
  },

  register: async (email, password, full_name) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authAPI.register(email, password, full_name)
      const { access, refresh, user } = response.data

      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)

      set({
        user,
        token: access,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Registration failed',
        isLoading: false,
      })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    })
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ isAuthenticated: false, user: null })
      return
    }

    try {
      const response = await authAPI.me()
      set({
        user: response.data,
        isAuthenticated: true,
      })
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({
        user: null,
        token: null,
        isAuthenticated: false,
      })
    }
  },

  clearError: () => set({ error: null }),
}))
```

### 4. React Query Configuration

**File:** `frontend/src/lib/queryClient.ts`
```typescript
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})
```

### 5. Environment Variables

**File:** `frontend/.env.development`
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=HishamOS
```

**File:** `frontend/.env.production`
```env
VITE_API_BASE_URL=https://api.hishamos.com/api/v1
VITE_APP_NAME=HishamOS
```

## Next Steps (Phase 9C)

1. Create layout components:
   - `DashboardLayout.tsx`
   - `Sidebar.tsx`
   - `Header.tsx`

2. Create authentication pages:
   - `LoginPage.tsx`
   - `RegisterPage.tsx`

3. Setup routing with React Router

4. Test authentication flow

## Current Status

- ✅ React + TypeScript + Vite project created
- ✅ Tailwind CSS + shadcn/ui configured
- ✅ Dependencies installed (259 packages)
- ✅ Project structure created
- ⏳ shadcn/ui components installing...
- ⏸️ Core files need manual creation (gitignore blocks automated creation)

## Manual Setup Required

Since `frontend/` is in `.gitignore`, you'll need to manually create the files listed above in your code editor.

Copy the code snippets from this guide into the corresponding file paths.
