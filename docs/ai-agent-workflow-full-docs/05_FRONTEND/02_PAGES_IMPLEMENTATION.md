# Frontend Pages Implementation - React Pages

**Document Type:** Pages Implementation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 03_COMPONENTS_IMPLEMENTATION.md, 04_HOOKS_IMPLEMENTATION.md, ../10_UX/  
**File Size:** 498 lines

---

## 📋 Purpose

This document specifies the implementation of React pages for the AI agent workflow enhancement features.

---

## 📄 New Pages

### Page 1: ProjectGeneratorPage

**Location:** `frontend/src/pages/projects/ProjectGeneratorPage.tsx`

**Purpose:** Allow users to generate projects from workflows

**Route:** `/projects/:projectId/generate`

**Features:**
- Project selection
- Workflow selection
- Input parameter form
- Generation trigger
- Progress tracking
- Results display

**Implementation Structure:**

```typescript
export function ProjectGeneratorPage() {
  const { projectId } = useParams()
  const { data: project } = useProject(projectId || '')
  const { data: workflows } = useWorkflows()
  const generateMutation = useProjectGeneration()
  
  // State
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null)
  const [inputData, setInputData] = useState<Record<string, any>>({})
  const [generationStatus, setGenerationStatus] = useState<string | null>(null)
  
  // Handlers
  const handleGenerate = () => {
    generateMutation.mutate({
      projectId: projectId!,
      workflowId: selectedWorkflow!,
      inputData
    })
  }
  
  return (
    <div className="container mx-auto py-8">
      <PageHeader 
        title="Generate Project"
        description="Generate a complete project from a workflow"
      />
      
      <Card>
        <CardHeader>
          <CardTitle>Project: {project?.name}</CardTitle>
        </CardHeader>
        <CardContent>
          <ProjectGenerator
            project={project}
            workflows={workflows}
            onGenerate={handleGenerate}
            isGenerating={generateMutation.isPending}
          />
        </CardContent>
      </Card>
      
      {generationStatus && (
        <GenerationProgress status={generationStatus} />
      )}
    </div>
  )
}
```

**Key Components:**
- `ProjectGenerator` - Main form component
- `GenerationProgress` - Progress indicator
- `WorkflowSelector` - Workflow selection

---

### Page 2: GeneratedProjectViewPage

**Location:** `frontend/src/pages/projects/GeneratedProjectViewPage.tsx`

**Purpose:** View generated project details and files

**Route:** `/projects/:projectId/generated/:generatedId`

**Features:**
- Generated project details
- File tree navigation
- File content viewer
- Export options
- Status display

**Implementation Structure:**

```typescript
export function GeneratedProjectViewPage() {
  const { projectId, generatedId } = useParams()
  const { data: generatedProject } = useGeneratedProject(projectId!, generatedId!)
  const { data: files } = useProjectFiles(projectId!, generatedId!)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  
  return (
    <div className="container mx-auto py-8">
      <PageHeader 
        title={`Generated Project: ${generatedProject?.project.name}`}
        description={generatedProject?.status}
      />
      
      <div className="grid grid-cols-3 gap-4">
        {/* File Tree */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Files</CardTitle>
          </CardHeader>
          <CardContent>
            <FileTree
              files={files}
              onFileSelect={setSelectedFile}
              selectedFile={selectedFile}
            />
          </CardContent>
        </Card>
        
        {/* File Content */}
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>
              {selectedFile ? selectedFile : 'Select a file'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedFile && (
              <FileViewer filePath={selectedFile} />
            )}
          </CardContent>
        </Card>
      </div>
      
      {/* Export Actions */}
      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Export Options</CardTitle>
        </CardHeader>
        <CardContent>
          <RepositoryExport generatedProjectId={generatedId!} />
        </CardContent>
      </Card>
    </div>
  )
}
```

**Key Components:**
- `FileTree` - File navigation
- `FileViewer` - File content display
- `RepositoryExport` - Export interface

---

### Page 3: ProjectExportPage

**Location:** `frontend/src/pages/projects/ProjectExportPage.tsx`

**Purpose:** Export generated project as repository

**Route:** `/projects/:projectId/generated/:generatedId/export`

**Features:**
- Export type selection
- Configuration forms
- Export progress
- Download/redirect links

**Implementation Structure:**

```typescript
export function ProjectExportPage() {
  const { projectId, generatedId } = useParams()
  const { data: generatedProject } = useGeneratedProject(projectId!, generatedId!)
  const exportMutation = useRepositoryExport()
  const [exportType, setExportType] = useState<'zip' | 'github' | 'gitlab'>('zip')
  
  const handleExport = (config: ExportConfig) => {
    exportMutation.mutate({
      generatedProjectId: generatedId!,
      exportType,
      config
    })
  }
  
  return (
    <div className="container mx-auto py-8">
      <PageHeader 
        title="Export Project"
        description="Export generated project as repository"
      />
      
      <Card>
        <CardHeader>
          <CardTitle>Export Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <ExportTypeSelector
            value={exportType}
            onChange={setExportType}
          />
          
          {exportType === 'zip' && (
            <ZipExportConfig onSubmit={handleExport} />
          )}
          
          {exportType === 'github' && (
            <GitHubExportConfig onSubmit={handleExport} />
          )}
          
          {exportType === 'gitlab' && (
            <GitLabExportConfig onSubmit={handleExport} />
          )}
        </CardContent>
      </Card>
      
      {exportMutation.isPending && (
        <ExportProgress />
      )}
      
      {exportMutation.isSuccess && (
        <ExportSuccess result={exportMutation.data} />
      )}
    </div>
  )
}
```

**Key Components:**
- `ExportTypeSelector` - Export type selection
- `ZipExportConfig` - ZIP export configuration
- `GitHubExportConfig` - GitHub export configuration
- `GitLabExportConfig` - GitLab export configuration
- `ExportProgress` - Progress indicator
- `ExportSuccess` - Success message with links

---

## 🔄 Enhanced Pages

### Page 1: WorkflowBuilderPage (Enhanced)

**Location:** `frontend/src/pages/workflows/WorkflowBuilderPage.tsx`

**Enhancements:**
- Add new step types to selector
- Add step editors for new types
- Update validation logic

**New Step Types:**
- `api_call` - API call step
- `file_generation` - File generation step
- `repo_creation` - Repository creation step

**Key Changes:**
- Extend `StepTypeSelector` component
- Add new step editor components
- Update step validation

---

## 🔗 Routing Configuration

**Location:** `frontend/src/App.tsx`

**New Routes:**

```typescript
<Route path="/projects/:projectId/generate" element={<ProjectGeneratorPage />} />
<Route path="/projects/:projectId/generated/:generatedId" element={<GeneratedProjectViewPage />} />
<Route path="/projects/:projectId/generated/:generatedId/export" element={<ProjectExportPage />} />
```

---

## 🎨 Page Layout Structure

### Common Layout Elements

**All Pages Include:**
- Page header with title and description
- Breadcrumb navigation
- Action buttons
- Status indicators
- Error handling UI

---

## 📊 Page State Management

### State Per Page

**ProjectGeneratorPage:**
- Selected workflow
- Input parameters
- Generation status
- Error state

**GeneratedProjectViewPage:**
- Selected file
- File tree expanded state
- File content cache

**ProjectExportPage:**
- Export type
- Export configuration
- Export status
- Export result

---

## ✅ Page Requirements

### Common Requirements
- Responsive design
- Error handling
- Loading states
- Success notifications
- Accessibility (ARIA labels)

### Specific Requirements
- **ProjectGeneratorPage:** Real-time progress updates
- **GeneratedProjectViewPage:** Large file handling
- **ProjectExportPage:** Token security (don't expose in UI)

---

## 🔗 Related Documentation

- **Components:** `03_COMPONENTS_IMPLEMENTATION.md`
- **Hooks:** `04_HOOKS_IMPLEMENTATION.md`
- **UX Design:** `../10_UX/`
- **Routing:** `07_ROUTING_IMPLEMENTATION.md`

---

**Document Owner:** Frontend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

