# Frontend Services Implementation - API Client

**Document Type:** Services Implementation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 04_HOOKS_IMPLEMENTATION.md, ../04_BACKEND/04_VIEWS_IMPLEMENTATION.md  
**File Size:** 489 lines

---

## 📋 Purpose

This document specifies the API client service methods for the AI agent workflow enhancement endpoints.

---

## 🔌 API Service Enhancements

### Enhanced: projectsAPI

**Location:** `frontend/src/services/api.ts`

**New Methods:**

#### Method 1: generateProject

```typescript
generateProject: (
  projectId: string,
  data: {
    workflow_id: string
    input_data: Record<string, any>
  }
) => {
  return api.post(`/projects/${projectId}/generate/`, data)
}
```

---

#### Method 2: listGeneratedProjects

```typescript
listGeneratedProjects: (
  projectId: string,
  params?: {
    status?: string
    page?: number
    page_size?: number
  }
) => {
  const queryParams = new URLSearchParams()
  if (params?.status) queryParams.append('status', params.status)
  if (params?.page) queryParams.append('page', String(params.page))
  if (params?.page_size) queryParams.append('page_size', String(params.page_size))
  const query = queryParams.toString()
  return api.get(query ? `/projects/${projectId}/generated/?${query}` : `/projects/${projectId}/generated/`)
}
```

---

#### Method 3: getGeneratedProject

```typescript
getGeneratedProject: (projectId: string, generatedId: string) => {
  return api.get(`/projects/${projectId}/generated/${generatedId}/`)
}
```

---

#### Method 4: listProjectFiles

```typescript
listProjectFiles: (
  projectId: string,
  generatedId: string,
  params?: {
    file_type?: string
    path?: string
    page?: number
    page_size?: number
  }
) => {
  const queryParams = new URLSearchParams()
  if (params?.file_type) queryParams.append('file_type', params.file_type)
  if (params?.path) queryParams.append('path', params.path)
  if (params?.page) queryParams.append('page', String(params.page))
  if (params?.page_size) queryParams.append('page_size', String(params.page_size))
  const query = queryParams.toString()
  return api.get(
    query 
      ? `/projects/${projectId}/generated/${generatedId}/files/?${query}`
      : `/projects/${projectId}/generated/${generatedId}/files/`
  )
}
```

---

#### Method 5: getProjectFile

```typescript
getProjectFile: (
  projectId: string,
  generatedId: string,
  fileId: string,
  includeContent = false
) => {
  const params = includeContent ? '?content=true' : ''
  return api.get(`/projects/${projectId}/generated/${generatedId}/files/${fileId}/${params}`)
}
```

---

#### Method 6: getFileContent

```typescript
getFileContent: (
  projectId: string,
  generatedId: string,
  filePath: string
) => {
  return api.get(
    `/projects/${projectId}/generated/${generatedId}/files/content/?path=${encodeURIComponent(filePath)}`,
    { responseType: 'blob' }
  )
}
```

---

#### Method 7: exportRepository

```typescript
exportRepository: (
  projectId: string,
  generatedId: string,
  exportType: 'zip' | 'tar' | 'tar.gz' | 'github' | 'gitlab',
  options: {
    repository_name?: string
    organization?: string
    private?: boolean
    github_token?: string
    gitlab_token?: string
    namespace?: string
    visibility?: string
  }
) => {
  return api.post(`/projects/${projectId}/generated/${generatedId}/export/`, {
    export_type: exportType,
    ...options
  })
}
```

---

#### Method 8: exportToGitHub

```typescript
exportToGitHub: (
  projectId: string,
  generatedId: string,
  data: {
    repository_name: string
    organization?: string
    private?: boolean
    github_token?: string
  }
) => {
  return api.post(`/projects/${projectId}/generated/${generatedId}/export-to-github/`, data)
}
```

---

#### Method 9: exportToGitLab

```typescript
exportToGitLab: (
  projectId: string,
  generatedId: string,
  data: {
    project_name: string
    namespace?: string
    visibility?: 'private' | 'internal' | 'public'
    gitlab_token?: string
  }
) => {
  return api.post(`/projects/${projectId}/generated/${generatedId}/export-to-gitlab/`, data)
}
```

---

#### Method 10: listExports

```typescript
listExports: (
  projectId: string,
  generatedId: string
) => {
  return api.get(`/projects/${projectId}/generated/${generatedId}/exports/`)
}
```

---

#### Method 11: getExportStatus

```typescript
getExportStatus: (
  projectId: string,
  generatedId: string,
  exportId: string
) => {
  return api.get(`/projects/${projectId}/generated/${generatedId}/exports/${exportId}/`)
}
```

---

#### Method 12: downloadExport

```typescript
downloadExport: (exportId: string) => {
  return api.get(`/exports/${exportId}/download/`, {
    responseType: 'blob'
  })
}
```

---

## 📊 Type Definitions

### Types File 1: generated-project.ts

**Location:** `frontend/src/types/generated-project.ts`

**Types:**

```typescript
export interface GeneratedProject {
  id: string
  project: string
  project_name?: string
  workflow_execution?: string
  output_directory: string
  status: 'pending' | 'generating' | 'completed' | 'failed' | 'archived'
  error_message?: string
  total_files: number
  total_size: number
  files_count?: number
  exports_count?: number
  files?: ProjectFile[]
  created_by: string
  created_by_name?: string
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface GenerationConfig {
  projectId: string
  workflowId: string
  inputData: Record<string, any>
}
```

---

### Types File 2: project-file.ts

**Location:** `frontend/src/types/project-file.ts`

**Types:**

```typescript
export interface ProjectFile {
  id: string
  generated_project: string
  file_path: string
  file_name: string
  file_type: string
  file_size: number
  file_size_display?: string
  content_hash: string
  content_preview?: string
  content?: string
  created_at: string
  updated_at: string
}
```

---

### Types File 3: repository-export.ts

**Location:** `frontend/src/types/repository-export.ts`

**Types:**

```typescript
export interface RepositoryExport {
  id: string
  generated_project: string
  export_type: 'zip' | 'tar' | 'tar.gz' | 'github' | 'gitlab'
  repository_name?: string
  repository_url?: string
  archive_path?: string
  archive_size?: number
  status: 'pending' | 'exporting' | 'completed' | 'failed'
  error_message?: string
  config?: Record<string, any>
  download_url?: string
  created_by: string
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface ExportConfig {
  projectId: string
  generatedProjectId: string
  exportType: 'zip' | 'tar' | 'tar.gz' | 'github' | 'gitlab'
  options: {
    repository_name?: string
    organization?: string
    private?: boolean
    github_token?: string
    gitlab_token?: string
    namespace?: string
    visibility?: string
  }
}
```

---

## ⚠️ Error Handling

### Error Response Format

**Expected Format:**
```typescript
interface APIError {
  error: string
  message: string
  details?: Record<string, string>
  timestamp: string
}
```

**Handling:**
- Display user-friendly messages
- Log errors for debugging
- Show toast notifications

---

## 🔗 Related Documentation

- **Hooks:** `04_HOOKS_IMPLEMENTATION.md`
- **Backend Views:** `../04_BACKEND/04_VIEWS_IMPLEMENTATION.md`
- **API Architecture:** `../03_ARCHITECTURE/04_API_ARCHITECTURE.md`

---

**Document Owner:** Frontend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

