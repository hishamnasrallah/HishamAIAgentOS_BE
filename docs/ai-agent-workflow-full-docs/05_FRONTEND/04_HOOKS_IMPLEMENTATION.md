# Frontend Hooks Implementation - React Hooks

**Document Type:** Hooks Implementation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 02_PAGES_IMPLEMENTATION.md, 05_SERVICES_IMPLEMENTATION.md  
**File Size:** 488 lines

---

## 📋 Purpose

This document specifies the React hooks for the AI agent workflow enhancement features.

---

## 🎣 New Hooks

### Hook 1: useProjectGeneration

**Location:** `frontend/src/hooks/useProjectGeneration.ts`

**Purpose:** Handle project generation operations

**Implementation:**

```typescript
export function useProjectGeneration() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (config: GenerationConfig) => {
      return projectsAPI.generateProject(config.projectId, {
        workflow_id: config.workflowId,
        input_data: config.inputData
      })
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['projects', data.project_id, 'generated'])
      toast.success('Project generation started')
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to start generation')
    }
  })
}

export function useGeneratedProject(projectId: string, generatedId: string) {
  return useQuery({
    queryKey: ['projects', projectId, 'generated', generatedId],
    queryFn: () => projectsAPI.getGeneratedProject(projectId, generatedId),
    enabled: !!projectId && !!generatedId,
    refetchInterval: (query) => {
      const data = query.state.data
      // Poll while generating
      if (data?.status === 'generating') {
        return 2000 // 2 seconds
      }
      return false
    }
  })
}

export function useGeneratedProjects(projectId: string, filters?: { status?: string }) {
  return useQuery({
    queryKey: ['projects', projectId, 'generated', filters],
    queryFn: () => projectsAPI.listGeneratedProjects(projectId, filters),
    enabled: !!projectId
  })
}
```

---

### Hook 2: useFileManagement

**Location:** `frontend/src/hooks/useFileManagement.ts`

**Purpose:** Handle file operations

**Implementation:**

```typescript
export function useProjectFiles(
  projectId: string,
  generatedId: string,
  filters?: { file_type?: string; path?: string }
) {
  return useQuery({
    queryKey: ['projects', projectId, 'generated', generatedId, 'files', filters],
    queryFn: () => projectsAPI.listProjectFiles(projectId, generatedId, filters),
    enabled: !!projectId && !!generatedId
  })
}

export function useProjectFile(
  projectId: string,
  generatedId: string,
  fileId: string,
  includeContent = false
) {
  return useQuery({
    queryKey: ['projects', projectId, 'generated', generatedId, 'files', fileId, includeContent],
    queryFn: () => projectsAPI.getProjectFile(projectId, generatedId, fileId, includeContent),
    enabled: !!projectId && !!generatedId && !!fileId
  })
}

export function useFileContent(projectId: string, generatedId: string, filePath: string) {
  return useQuery({
    queryKey: ['projects', projectId, 'generated', generatedId, 'files', 'content', filePath],
    queryFn: () => projectsAPI.getFileContent(projectId, generatedId, filePath),
    enabled: !!projectId && !!generatedId && !!filePath,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
```

---

### Hook 3: useRepositoryExport

**Location:** `frontend/src/hooks/useRepositoryExport.ts`

**Purpose:** Handle repository export operations

**Implementation:

```typescript
export function useRepositoryExport() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (config: ExportConfig) => {
      return projectsAPI.exportRepository(
        config.projectId,
        config.generatedProjectId,
        config.exportType,
        config.options
      )
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries([
        'projects',
        variables.projectId,
        'generated',
        variables.generatedProjectId,
        'exports'
      ])
      toast.success('Export started')
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to start export')
    }
  })
}

export function useExportStatus(projectId: string, generatedId: string, exportId: string) {
  return useQuery({
    queryKey: ['projects', projectId, 'generated', generatedId, 'exports', exportId],
    queryFn: () => projectsAPI.getExportStatus(projectId, generatedId, exportId),
    enabled: !!projectId && !!generatedId && !!exportId,
    refetchInterval: (query) => {
      const data = query.state.data
      // Poll while exporting
      if (data?.status === 'exporting') {
        return 2000 // 2 seconds
      }
      return false
    }
  })
}

export function useExports(projectId: string, generatedId: string) {
  return useQuery({
    queryKey: ['projects', projectId, 'generated', generatedId, 'exports'],
    queryFn: () => projectsAPI.listExports(projectId, generatedId),
    enabled: !!projectId && !!generatedId
  })
}
```

---

## 🔄 Hook Patterns

### Pattern 1: React Query Integration

**All data fetching uses React Query:**
- Automatic caching
- Background refetching
- Error handling
- Loading states

---

### Pattern 2: Mutation Hooks

**All mutations include:**
- Success/error callbacks
- Query invalidation
- Toast notifications
- Loading states

---

### Pattern 3: Conditional Queries

**Queries enabled conditionally:**
```typescript
enabled: !!projectId && !!generatedId
```

---

## 📊 Hook Usage Examples

### Example 1: Generate Project

```typescript
function ProjectGenerator() {
  const generateMutation = useProjectGeneration()
  
  const handleGenerate = () => {
    generateMutation.mutate({
      projectId: '...',
      workflowId: '...',
      inputData: { ... }
    })
  }
  
  return (
    <Button 
      onClick={handleGenerate}
      disabled={generateMutation.isPending}
    >
      {generateMutation.isPending ? 'Generating...' : 'Generate'}
    </Button>
  )
}
```

---

### Example 2: View Files

```typescript
function FileList() {
  const { projectId, generatedId } = useParams()
  const { data: files, isLoading } = useProjectFiles(projectId!, generatedId!)
  
  if (isLoading) return <LoadingSpinner />
  
  return (
    <ul>
      {files?.map(file => (
        <li key={file.id}>{file.file_path}</li>
      ))}
    </ul>
  )
}
```

---

## 🔗 Related Documentation

- **Pages:** `02_PAGES_IMPLEMENTATION.md`
- **Services:** `05_SERVICES_IMPLEMENTATION.md`
- **Components:** `03_COMPONENTS_IMPLEMENTATION.md`

---

**Document Owner:** Frontend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

