# Frontend File Structure - Project Organization

**Document Type:** File Structure Documentation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 01_FRONTEND_OVERVIEW.md  
**File Size:** 482 lines

---

## 📋 Purpose

This document describes the file structure and organization for the frontend implementation.

---

## 📁 File Structure

### Complete Structure

```
frontend/src/
├── pages/
│   ├── projects/
│   │   ├── ProjectGeneratorPage.tsx (NEW)
│   │   ├── GeneratedProjectViewPage.tsx (NEW)
│   │   └── ProjectExportPage.tsx (NEW)
│   └── workflows/
│       └── WorkflowBuilderPage.tsx (enhanced)
│
├── components/
│   ├── projects/
│   │   ├── ProjectGenerator.tsx (NEW)
│   │   ├── FileTree.tsx (NEW)
│   │   ├── FileViewer.tsx (NEW)
│   │   ├── RepositoryExport.tsx (NEW)
│   │   └── GenerationProgress.tsx (NEW)
│   └── workflows/
│       ├── StepTypeSelector.tsx (enhanced)
│       ├── APICallStepEditor.tsx (NEW)
│       ├── FileGenerationStepEditor.tsx (NEW)
│       └── RepoCreationStepEditor.tsx (NEW)
│
├── hooks/
│   ├── useProjectGeneration.ts (NEW)
│   ├── useFileManagement.ts (NEW)
│   └── useRepositoryExport.ts (NEW)
│
├── stores/
│   ├── generatedProjectStore.ts (NEW)
│   └── fileViewerStore.ts (NEW)
│
├── services/
│   └── api.ts (enhanced)
│
├── types/
│   ├── generated-project.ts (NEW)
│   ├── project-file.ts (NEW)
│   └── repository-export.ts (NEW)
│
└── App.tsx (enhanced - add routes)
```

---

## 📝 New Files Summary

### Pages (3 files)
- `ProjectGeneratorPage.tsx` - Project generation page
- `GeneratedProjectViewPage.tsx` - Generated project view
- `ProjectExportPage.tsx` - Export page

### Components (8 files)
- `ProjectGenerator.tsx` - Generation form
- `FileTree.tsx` - File tree navigation
- `FileViewer.tsx` - File content viewer
- `RepositoryExport.tsx` - Export interface
- `GenerationProgress.tsx` - Progress display
- `APICallStepEditor.tsx` - API call step editor
- `FileGenerationStepEditor.tsx` - File generation step editor
- `RepoCreationStepEditor.tsx` - Repo creation step editor

### Hooks (3 files)
- `useProjectGeneration.ts` - Generation hooks
- `useFileManagement.ts` - File management hooks
- `useRepositoryExport.ts` - Export hooks

### Stores (2 files)
- `generatedProjectStore.ts` - Generated project state
- `fileViewerStore.ts` - File viewer state

### Types (3 files)
- `generated-project.ts` - Generated project types
- `project-file.ts` - Project file types
- `repository-export.ts` - Export types

### Enhanced Files (2 files)
- `api.ts` - Add new API methods
- `App.tsx` - Add new routes

---

## 🔗 Related Documentation

- **Frontend Overview:** `01_FRONTEND_OVERVIEW.md`
- **Pages:** `02_PAGES_IMPLEMENTATION.md`
- **Components:** `03_COMPONENTS_IMPLEMENTATION.md`

---

**Document Owner:** Frontend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

