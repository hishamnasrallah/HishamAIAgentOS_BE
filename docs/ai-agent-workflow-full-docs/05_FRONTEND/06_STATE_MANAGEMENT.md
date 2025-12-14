# Frontend State Management - Zustand Stores

**Document Type:** State Management  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 02_PAGES_IMPLEMENTATION.md, 04_HOOKS_IMPLEMENTATION.md  
**File Size:** 485 lines

---

## 📋 Purpose

This document specifies the Zustand state management stores for the AI agent workflow enhancement features.

---

## 🗄️ New Stores

### Store 1: useGeneratedProjectStore

**Location:** `frontend/src/stores/generatedProjectStore.ts`

**Purpose:** Manage generated project state

**State:**
```typescript
interface GeneratedProjectState {
  selectedProject: string | null
  selectedGenerated: string | null
  selectedFile: string | null
  fileTreeExpanded: Set<string>
  setSelectedProject: (id: string | null) => void
  setSelectedGenerated: (id: string | null) => void
  setSelectedFile: (path: string | null) => void
  toggleFileTreePath: (path: string) => void
  reset: () => void
}
```

**Implementation:**

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useGeneratedProjectStore = create<GeneratedProjectState>()(
  persist(
    (set) => ({
      selectedProject: null,
      selectedGenerated: null,
      selectedFile: null,
      fileTreeExpanded: new Set(),
      
      setSelectedProject: (id) => set({ selectedProject: id }),
      setSelectedGenerated: (id) => set({ selectedGenerated: id }),
      setSelectedFile: (path) => set({ selectedFile: path }),
      
      toggleFileTreePath: (path) => set((state) => {
        const expanded = new Set(state.fileTreeExpanded)
        if (expanded.has(path)) {
          expanded.delete(path)
        } else {
          expanded.add(path)
        }
        return { fileTreeExpanded: expanded }
      }),
      
      reset: () => set({
        selectedProject: null,
        selectedGenerated: null,
        selectedFile: null,
        fileTreeExpanded: new Set()
      })
    }),
    {
      name: 'generated-project-store',
      partialize: (state) => ({
        selectedProject: state.selectedProject,
        selectedGenerated: state.selectedGenerated,
        selectedFile: state.selectedFile,
        fileTreeExpanded: Array.from(state.fileTreeExpanded)
      })
    }
  )
)
```

---

### Store 2: useFileViewerStore

**Location:** `frontend/src/stores/fileViewerStore.ts`

**Purpose:** Manage file viewer state

**State:**
```typescript
interface FileViewerState {
  fileContentCache: Map<string, string>
  selectedLanguage: string | null
  lineNumbers: boolean
  wordWrap: boolean
  setFileContent: (path: string, content: string) => void
  getFileContent: (path: string) => string | undefined
  clearCache: () => void
  setSelectedLanguage: (lang: string | null) => void
  setLineNumbers: (enabled: boolean) => void
  setWordWrap: (enabled: boolean) => void
}
```

**Implementation:**

```typescript
export const useFileViewerStore = create<FileViewerState>()(
  persist(
    (set, get) => ({
      fileContentCache: new Map(),
      selectedLanguage: null,
      lineNumbers: true,
      wordWrap: false,
      
      setFileContent: (path, content) => set((state) => {
        const cache = new Map(state.fileContentCache)
        cache.set(path, content)
        return { fileContentCache: cache }
      }),
      
      getFileContent: (path) => {
        return get().fileContentCache.get(path)
      },
      
      clearCache: () => set({ fileContentCache: new Map() }),
      
      setSelectedLanguage: (lang) => set({ selectedLanguage: lang }),
      setLineNumbers: (enabled) => set({ lineNumbers: enabled }),
      setWordWrap: (enabled) => set({ wordWrap: enabled })
    }),
    {
      name: 'file-viewer-store'
    }
  )
)
```

---

## 🔄 Enhanced Stores

### Store 1: useWorkflowStore (Enhanced)

**Location:** `frontend/src/stores/workflowStore.ts`

**Enhancements:**
- Add new step types to step type registry
- Support for new step configuration

**New Step Types:**
- `api_call`
- `file_generation`
- `repo_creation`

---

## 🔗 Store Integration

### Integration with React Query

**Pattern:**
- Zustand for UI state
- React Query for server state
- Zustand can trigger React Query invalidations

**Example:**
```typescript
const { setSelectedGenerated } = useGeneratedProjectStore()
const queryClient = useQueryClient()

const handleSelect = (id: string) => {
  setSelectedGenerated(id)
  queryClient.invalidateQueries(['projects', projectId, 'generated', id])
}
```

---

## 📊 Store Persistence

### Persistence Strategy

**Persisted:**
- UI preferences (line numbers, word wrap)
- Selected files/paths
- Expanded tree paths

**Not Persisted:**
- File content cache (too large)
- Temporary state
- Loading states

---

## 🔗 Related Documentation

- **Pages:** `02_PAGES_IMPLEMENTATION.md`
- **Hooks:** `04_HOOKS_IMPLEMENTATION.md`

---

**Document Owner:** Frontend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

