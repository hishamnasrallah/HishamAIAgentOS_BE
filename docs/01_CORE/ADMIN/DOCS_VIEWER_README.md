---
title: "📚 Documentation Viewer"
description: "**Location:** `/docs` in frontend"

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
  - core

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

# 📚 Documentation Viewer

**Location:** `/docs` in frontend  
**Status:** ✅ Ready

---

## Features

### ✅ Backend API
- **List Files:** `GET /api/v1/docs/list_files/` - Get all markdown files
- **Get File:** `GET /api/v1/docs/get_file/?path=<file_path>` - Get file content (HTML or raw)
- **Search:** `GET /api/v1/docs/search/?q=<query>&limit=50` - Search documentation

### ✅ Frontend Viewer
- **File Tree:** Browse all documentation files in a tree structure
- **Search:** Real-time search across all documentation
- **Markdown Rendering:** Beautiful HTML rendering with syntax highlighting
- **Responsive:** Works on all screen sizes

---

## Usage

1. **Navigate to `/docs`** in the frontend
2. **Browse files** using the sidebar tree
3. **Search** using the search box
4. **Click a file** to view its content
5. **Content is rendered** as beautiful HTML

---

## Technical Details

### Backend
- **App:** `apps.docs`
- **Views:** `DocumentationViewSet`
- **Permissions:** Authenticated users only
- **Markdown Library:** `markdown` with extensions (codehilite, fenced_code, tables, toc)

### Frontend
- **Page:** `DocumentationViewerPage.tsx`
- **API Service:** `docsAPI.ts`
- **Styling:** Tailwind CSS with custom prose styles
- **Routing:** `/docs` route in App.tsx

---

## File Structure

```
backend/apps/docs/
├── __init__.py
├── apps.py
├── views.py          # API endpoints
└── urls.py           # URL routing

frontend/src/
├── pages/docs/
│   └── DocumentationViewerPage.tsx
├── services/
│   └── docsAPI.ts
└── index.css         # Prose styling
```

---

## API Endpoints

### List Files
```http
GET /api/v1/docs/list_files/
Authorization: Bearer <token>

Response:
{
  "files": [...],
  "tree": {...},
  "total_files": 172
}
```

### Get File
```http
GET /api/v1/docs/get_file/?path=testing/QUICK_START_TESTING_GUIDE.md&format=html
Authorization: Bearer <token>

Response:
{
  "path": "testing/QUICK_START_TESTING_GUIDE.md",
  "name": "QUICK_START_TESTING_GUIDE.md",
  "size": 12345,
  "modified": 1234567890,
  "html": "<div>...</div>"
}
```

### Search
```http
GET /api/v1/docs/search/?q=testing&limit=50
Authorization: Bearer <token>

Response:
{
  "query": "testing",
  "results": [...],
  "total": 10
}
```

---

## Styling

Markdown content is styled using Tailwind's prose classes with custom CSS in `index.css`:
- Headings (h1-h6)
- Paragraphs and lists
- Code blocks with syntax highlighting
- Tables
- Blockquotes
- Links and images

---

## Security

- ✅ Authentication required
- ✅ Path traversal protection
- ✅ File path validation
- ✅ Only markdown files accessible

---

**Last Updated:** December 6, 2024

