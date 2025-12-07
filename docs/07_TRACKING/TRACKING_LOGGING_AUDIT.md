---
title: "HishamOS - Tracking, Logging, and Audit Documentation"
description: "**Last Updated:** December 6, 2024"

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

# HishamOS - Tracking, Logging, and Audit Documentation

**Last Updated:** December 6, 2024  
**Status:** Active Documentation  
**Maintainer:** Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Logging System](#logging-system)
4. [Audit Trail](#audit-trail)
5. [Tracking & Monitoring](#tracking--monitoring)
6. [Known Issues](#known-issues)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

HishamOS implements a comprehensive tracking, logging, and audit system to ensure:
- **Traceability**: All user actions and system events are logged
- **Security**: Audit trails for compliance and security monitoring
- **Debugging**: Detailed logs for troubleshooting and performance analysis
- **Monitoring**: Real-time system health and performance metrics

### Key Components

- **Structured Logging**: JSON-formatted logs with consistent schema
- **Audit Logs**: Immutable records of all critical actions
- **Performance Tracking**: Metrics for API calls, database queries, and workflow executions
- **Cost Tracking**: AI platform usage and cost monitoring
- **Error Tracking**: Centralized error logging and alerting

---

## System Architecture

### Logging Layers

```
┌─────────────────────────────────────────┐
│         Application Layer                │
│  (Django Views, Services, Consumers)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Logging Middleware                  │
│  - Request/Response Logging              │
│  - Authentication Logging                │
│  - Error Capture                        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Log Handlers                        │
│  - Console Handler (Development)         │
│  - File Handler (Production)             │
│  - External Service (Sentry, etc.)      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Storage & Analysis                  │
│  - Database (Audit Logs)                 │
│  - Log Files                             │
│  - Monitoring Dashboards                │
└─────────────────────────────────────────┘
```

### Database Schema

#### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### System Metrics Table
```sql
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value DECIMAL(15, 4),
    unit VARCHAR(20),
    tags JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## Logging System

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| **DEBUG** | Detailed diagnostic information | SQL query execution, function entry/exit |
| **INFO** | General informational messages | User login, workflow execution started |
| **WARNING** | Warning messages for potential issues | Deprecated API usage, rate limit approaching |
| **ERROR** | Error events that don't stop execution | API call failure, validation error |
| **CRITICAL** | Critical errors that may stop execution | Database connection failure, security breach |

### Log Format

All logs follow a structured JSON format:

```json
{
  "timestamp": "2024-12-06T08:28:15.901Z",
  "level": "INFO",
  "logger": "apps.workflows.consumers",
  "message": "Connection attempt for execution: 01df55eb-5788-4892-bae4-8581b8cfb48e",
  "execution_id": "01df55eb-5788-4892-bae4-8581b8cfb48e",
  "user_id": "0b407fa6-66fe-408b-92e3-9636ee09725f",
  "request_id": "req_123456",
  "ip_address": "127.0.0.1"
}
```

### Logging Configuration

#### Development (Console Logging)
```python
# backend/core/settings/development.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

#### Production (File + External Service)
```python
# backend/core/settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/hishamos/app.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'sentry': {
            'class': 'raven.handlers.logging.SentryHandler',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['file', 'sentry'],
        'level': 'INFO',
    },
}
```

### Key Loggers

| Logger Name | Purpose | Log Level |
|-------------|---------|-----------|
| `apps.authentication` | Authentication events | INFO |
| `apps.agents.engine` | Agent execution | DEBUG |
| `apps.workflows.executor` | Workflow execution | INFO |
| `apps.workflows.consumers` | WebSocket connections | INFO |
| `apps.integrations.adapters` | AI platform calls | INFO |
| `apps.monitoring` | System metrics | INFO |
| `core.middleware` | Request/response logging | INFO |

---

## Audit Trail

### What Gets Audited

#### User Actions
- Login/Logout events
- Password changes
- Profile updates
- Role/permission changes

#### Resource Operations
- Create/Update/Delete operations on:
  - Agents
  - Workflows
  - Projects
  - Commands
  - AI Platform configurations

#### Security Events
- Failed authentication attempts
- Unauthorized access attempts
- API key creation/revocation
- Permission changes

#### System Events
- Workflow executions
- Agent executions
- Cost tracking events
- System configuration changes

### Audit Log Structure

```python
{
    "id": "uuid",
    "user_id": "uuid",
    "action": "workflow.executed",
    "resource_type": "WorkflowExecution",
    "resource_id": "uuid",
    "details": {
        "workflow_id": "uuid",
        "workflow_name": "Bug Triage Workflow",
        "status": "completed",
        "steps_completed": 5,
        "total_steps": 5,
        "duration_seconds": 45.2
    },
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "created_at": "2024-12-06T08:28:15Z"
}
```

### Audit Log Service

```python
# backend/apps/monitoring/services/audit_service.py
from apps.monitoring.models import AuditLog

class AuditService:
    @staticmethod
    @database_sync_to_async
    def log_action(
        user_id: str,
        action: str,
        resource_type: str = None,
        resource_id: str = None,
        details: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """Log an audit event"""
        AuditLog.objects.create(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
```

---

## Tracking & Monitoring

### Performance Metrics

#### API Response Times
- Tracked per endpoint
- P50, P95, P99 percentiles
- Stored in `system_metrics` table

#### Database Query Performance
- Slow query logging (>100ms)
- Query count per request
- Connection pool metrics

#### Workflow Execution Metrics
- Execution duration
- Steps completed/failed
- Agent execution times
- Cost per execution

### Cost Tracking

#### AI Platform Usage
- Tokens used (input/output)
- Cost per request
- Model used
- Platform (OpenAI, Anthropic, Google)

#### Cost Tracking Service
```python
# backend/apps/integrations/services/cost_tracker.py
class CostTracker:
    @staticmethod
    def track_completion(
        platform_name: str,
        model: str,
        tokens_input: int,
        tokens_output: int,
        user_id: str = None,
        agent_id: str = None
    ):
        """Track AI platform usage and cost"""
        # Calculate cost based on platform pricing
        # Store in database
        # Update user/agent usage statistics
```

### Real-time Monitoring

#### WebSocket Connections
- Active connections count
- Connection duration
- Messages sent/received
- Connection errors

#### System Health
- Database connectivity
- Redis connectivity
- AI platform availability
- Disk space
- Memory usage

---

## Known Issues

### WebSocket Connection Issues

**Issue ID:** WS-001  
**Date Reported:** December 6, 2024  
**Status:** 🔧 **FIXED** (December 2024)  
**Severity:** Medium

#### Description
WebSocket connections for workflow execution updates were being established successfully on the backend, but connections were closing immediately after the initial message was sent. The frontend reported "WebSocket is closed before the connection is established."

#### Symptoms (RESOLVED)
- ✅ Backend logs show successful connection establishment
- ✅ Initial message is sent successfully
- ❌ Connection was closing within 7-15ms after message sent (FIXED)
- ❌ Frontend showed connection error (FIXED)
- ✅ No error logs in backend

#### Root Cause
The primary issue was that the `WorkflowExecutionDetailPage` was not using WebSocket connections at all - it was only using polling. When a workflow execution was started:
1. WebSocket connected on the execute page
2. After 2 seconds, the page navigated to the execution detail page
3. The execution detail page didn't use WebSocket, so the connection was lost
4. The execution detail page only used polling (refetchInterval), missing real-time updates

#### Solution Implemented
1. **Added WebSocket support to WorkflowExecutionDetailPage:**
   - Integrated `useWorkflowWebSocket` hook
   - Added connection status indicator
   - WebSocket automatically connects when execution is running
   - Falls back to polling if WebSocket fails

2. **Improved connection lifecycle:**
   - Added explicit comment in consumer that connection should remain open
   - Improved error handling and logging
   - Better handling of connection state transitions

3. **Enhanced user experience:**
   - Added visual connection status indicator
   - Reduced polling interval (from 2s to 5s) as fallback
   - Real-time updates when WebSocket is connected

#### Affected Components (Updated)
- ✅ `backend/apps/workflows/consumers.py` - WorkflowExecutionConsumer (improved)
- ✅ `frontend/src/hooks/useWorkflowWebSocket.ts` - WebSocket hook (working)
- ✅ `frontend/src/pages/workflows/WorkflowExecutionDetailPage.tsx` - **NEW: Added WebSocket support**
- ✅ `backend/apps/workflows/routing.py` - WebSocket routing (working)

#### Testing Status
- ✅ WebSocket connects successfully on execute page
- ✅ WebSocket reconnects on execution detail page
- ✅ Real-time updates received during workflow execution
- ✅ Connection status indicator shows connection state
- ⚠️ **Note:** InMemoryChannelLayer is used in development - for production, Redis channel layer should be used for multi-process support

#### Next Steps (Future Improvements)
1. Consider using Redis channel layer for production (multi-process support)
2. Add WebSocket connection metrics/monitoring
3. Implement connection health checks/heartbeat
4. Add reconnection exponential backoff

#### Related Files
- `backend/apps/workflows/consumers.py` (lines 70-95)
- `frontend/src/hooks/useWorkflowWebSocket.ts` (lines 93-188)
- `backend/core/middleware.py` (JWT authentication)

#### Tracking
- **GitHub Issue:** (To be created)
- **Priority:** Medium
- **Assigned To:** Development Team
- **Target Resolution:** TBD

---

### Other Known Issues

#### Issue: AsyncHttpxClientWrapper State Error
**Issue ID:** HTTPX-001  
**Status:** Low Priority  
**Description:** AttributeError when closing httpx client wrapper  
**Impact:** Non-critical, doesn't affect functionality

---

## Best Practices

### Logging Best Practices

1. **Use Appropriate Log Levels**
   - DEBUG: Development diagnostics
   - INFO: Normal operations
   - WARNING: Potential issues
   - ERROR: Errors that don't stop execution
   - CRITICAL: System-stopping errors

2. **Include Context**
   ```python
   # Good
   logger.info(
       "Workflow execution started",
       extra={
           "execution_id": execution_id,
           "workflow_id": workflow_id,
           "user_id": user_id
       }
   )
   
   # Bad
   logger.info("Workflow started")
   ```

3. **Don't Log Sensitive Data**
   - Never log passwords, API keys, or tokens
   - Mask sensitive data in logs
   - Use environment-specific log levels

4. **Structured Logging**
   - Always use structured format (JSON)
   - Include request IDs for traceability
   - Add timestamps and context

### Audit Trail Best Practices

1. **Immutable Records**
   - Never delete audit logs
   - Archive old logs instead of deleting
   - Use append-only storage

2. **Comprehensive Coverage**
   - Log all critical operations
   - Include before/after states for updates
   - Track user context (IP, user agent)

3. **Performance Considerations**
   - Use async logging for high-volume events
   - Batch audit log writes when possible
   - Index frequently queried fields

### Monitoring Best Practices

1. **Set Up Alerts**
   - Error rate thresholds
   - Response time thresholds
   - Resource usage thresholds

2. **Dashboard Design**
   - Key metrics at a glance
   - Historical trends
   - Real-time status

3. **Cost Monitoring**
   - Track costs per user/agent
   - Set budget alerts
   - Regular cost reviews

---

## Troubleshooting

### Common Issues

#### Issue: Logs Not Appearing
**Symptoms:** No log output in console/files  
**Solutions:**
1. Check log level configuration
2. Verify logger name matches
3. Check file permissions for file handlers
4. Verify logging configuration is loaded

#### Issue: High Log Volume
**Symptoms:** Log files growing too large  
**Solutions:**
1. Increase log rotation frequency
2. Adjust log levels (reduce DEBUG logs)
3. Implement log filtering
4. Use external log aggregation service

#### Issue: Missing Audit Logs
**Symptoms:** Expected audit events not recorded  
**Solutions:**
1. Verify AuditService is being called
2. Check database connection
3. Verify user_id is available
4. Check for exceptions in audit logging

#### Issue: WebSocket Connection Issues
**Symptoms:** Connections closing immediately  
**Solutions:**
1. Check backend logs for errors
2. Verify execution exists
3. Check JWT token validity
4. Verify routing patterns
5. See [Known Issues - WebSocket Connection Issues](#websocket-connection-issues)

---

## References

- [Django Logging Documentation](https://docs.djangoproject.com/en/stable/topics/logging/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Structured Logging Guide](https://www.structlog.org/en/stable/)
- [Audit Trail Best Practices](https://owasp.org/www-community/vulnerabilities/Insufficient_Logging_and_Monitoring)

---

## Documentation Viewer System

### Overview

The Documentation Viewer (`/docs`) is a comprehensive documentation browsing system that provides:
- **File Tree View**: Hierarchical file structure navigation
- **Topics View**: Content-based classification by topics/categories
- **Role-based Filtering**: Filter documentation by user role/interest (BA, QA, Developer, etc.)
- **Search Functionality**: Full-text search across all documentation files
- **Real-time Features**: Recent files tracking, keyboard shortcuts, scroll management

### System Architecture

```
┌─────────────────────────────────────────┐
│      Frontend (React + TypeScript)       │
│  - DocumentationViewerPage.tsx           │
│  - docsAPI.ts (API client)              │
│  - File tree / Topics view              │
│  - Role filters                         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Backend (Django REST Framework)     │
│  - apps.docs.views.DocumentationViewSet  │
│  - File listing & classification         │
│  - Role-based filtering                  │
│  - Markdown rendering                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      File System                         │
│  - docs/ directory                       │
│  - Markdown files (.md)                  │
│  - Directory structure                   │
└─────────────────────────────────────────┘
```

### Features Implemented

#### 1. File Listing & Classification

**Backend Implementation:**
- `DocumentationViewSet.list_files()`: Lists all markdown files in `docs/` directory
- `_classify_by_topics()`: Classifies files into 8 topics based on `فهرس_المحتوى.md`
- `_classify_by_roles()`: Classifies files by role/interest (9 roles)
- `_build_directory_tree()`: Builds hierarchical file tree structure

**Topics Classification:**
- Core Documentation
- Testing Documentation
- Tracking & Monitoring
- Design & Specifications
- Development & Deployment
- Planning & Projects
- Commands & Libraries
- Status & Reports

**Role Classification:**
- Business Analyst
- QA / Tester
- Developer
- Technical Writer
- Project Manager
- DevOps
- Infrastructure
- Scrum Master
- CTO / Technical Lead
- General (default)

#### 2. Role-based Filtering

**Implementation:**
- Files are automatically tagged with role classifications based on:
  - Filename patterns
  - Directory structure
  - File path
  - File description (first 150 characters)
- Frontend filter buttons allow filtering by role
- API supports `?role=<role_name>` query parameter

**Example:**
```
GET /api/v1/docs/list_files/?view=topics&role=Developer
```

#### 3. Recent Files Tracking

**Frontend Implementation:**
- Tracks last 10 files opened by user
- Stored in component state (`recentFiles`)
- Displays last 5 files in empty state
- Clicking a recent file opens it immediately

**State Management:**
```typescript
const [recentFiles, setRecentFiles] = useState<string[]>([])

// Updated when file is opened
setRecentFiles(prev => {
  const updated = [selectedFile, ...prev.filter(f => f !== selectedFile)]
  return updated.slice(0, 10)
})
```

#### 4. Keyboard Shortcuts

**Implemented Shortcuts:**
- `Ctrl+F` / `Cmd+F`: Focus search input
- `Esc`: Clear search query

**Implementation:**
- Global keyboard event listener
- Prevents default browser search behavior
- Works only when not typing in input fields

#### 5. Breadcrumbs Navigation

**Display:**
- Shows file path in header: `Documentation > folder > filename.md`
- Helps users understand file location
- Clickable path segments (future enhancement)

#### 6. File Metadata Display

**Information Shown:**
- File size (formatted: B, KB, MB)
- Last modified date (relative: Today, Yesterday, X days ago)
- Displayed in:
  - File list (under each file name)
  - File header (when file is open)

**Formatting Functions:**
```typescript
formatFileSize(bytes: number): string
formatDate(timestamp: number): string
```

#### 7. Scroll to Top Button

**Behavior:**
- Appears when scroll position > 300px
- Fixed position: bottom-right corner
- Smooth scroll animation
- Monitors all scroll containers (`.overflow-y-auto`)

**Implementation:**
- Uses `useRef` to track scroll containers
- Periodic check every 500ms
- Listens to scroll events on all containers

#### 8. Search Improvements

**Features:**
- Clear button (X) appears when search has text
- Placeholder hint: "Search documentation... (Ctrl+F)"
- Full-text search across file content
- Search results show match count

#### 9. Empty States

**Welcome Screen:**
- Shown when no file is selected
- Displays:
  - Welcome message
  - Total file count
  - Recent Files list (if any)
  - Keyboard shortcuts guide

#### 10. Auto-open Index File

**Behavior:**
- Automatically opens `فهرس_المحتوى.md` on first page load
- Uses `useRef` to prevent multiple auto-opens
- Helps users start with documentation index

### API Endpoints

#### List Files
```
GET /api/v1/docs/list_files/
Query Parameters:
  - view: 'tree' | 'topics' (default: 'tree')
  - role: string (optional, filter by role)

Response:
{
  "files": [...],
  "topics": {...} | "tree": {...},
  "view": "topics" | "tree",
  "total_files": 172,
  "total_topics": 8,
  "available_roles": ["Business Analyst", "Developer", ...]
}
```

#### Get File Content
```
GET /api/v1/docs/get_file/
Query Parameters:
  - path: string (relative path to file)
  - output_format: 'raw' | 'html' (default: 'html')

Response:
{
  "path": "file.md",
  "name": "file.md",
  "size": 1024,
  "modified": 1234567890,
  "html": "<rendered markdown>" | "content": "raw markdown"
}
```

#### Search Files
```
GET /api/v1/docs/search/
Query Parameters:
  - q: string (search query)
  - limit: number (default: 50)

Response:
{
  "query": "search term",
  "results": [...],
  "total": 10
}
```

### Logging & Tracking

#### Frontend Logging

**Console Logs:**
- `[DocsViewer] Recent files updated:` - When file is opened
- `[DocsViewer] Search focused via keyboard shortcut` - Ctrl+F pressed
- `[DocsViewer] Search cleared via Esc key` - Esc pressed
- `[DocsViewer] Scroll position changed:` - Scroll position updates
- `[DocsViewer] Closing file:` - File closed
- `[DocsViewer] Scroll to top clicked` - Scroll to top button clicked

**Debug Info (Development Mode):**
- Fixed position debug panel (bottom-left)
- Shows:
  - Recent Files count
  - Scroll to Top button state
  - Selected File state

#### Backend Logging

**File Operations:**
- File listing operations logged at INFO level
- File read operations logged
- Search operations logged
- Errors logged at ERROR level with full traceback

**Example Log:**
```
INFO 2024-12-06 15:57:31,767 runserver 11824 6308 HTTP GET /api/v1/docs/list_files/ 200 [0.36, 127.0.0.1:51875]
```

### Performance Considerations

1. **File Reading:**
   - Description extraction reads only first 5 lines
   - Cached in file list response
   - No repeated file system access

2. **Role Classification:**
   - Performed once during file listing
   - Cached in file metadata
   - Pattern matching is efficient

3. **Markdown Rendering:**
   - Rendered on-demand (when file is opened)
   - HTML output cached in response
   - Uses `markdown` and `Pygments` libraries

4. **Search:**
   - Full-text search across all files
   - Results limited to 50 by default
   - Case-insensitive matching

### Security Considerations

1. **Path Traversal Prevention:**
   - Validates file paths
   - Prevents `..` in paths
   - Ensures files are within `docs/` directory
   - Uses `pathlib` for safe path operations

2. **Authentication:**
   - All endpoints require authentication
   - Uses Django REST Framework permissions
   - JWT token validation

3. **File Access:**
   - Only `.md` files are accessible
   - Directory listing restricted to `docs/` directory
   - No execution of file content

### Known Issues

#### Issue: useEffect Dependency Array Warning
**Issue ID:** DOCS-001  
**Date Reported:** December 2024  
**Status:** ✅ **FIXED**  
**Severity:** Low

**Description:**
React warning: "The final argument passed to useEffect changed size between renders"

**Solution:**
- Used `useRef` to track state without dependencies
- Fixed dependency arrays to be consistent
- Used `useRef` for scroll container tracking

**Affected Components:**
- `DocumentationViewerPage.tsx` - Auto-open index useEffect
- `DocumentationViewerPage.tsx` - Scroll to top useEffect

### Future Enhancements

1. **Table of Contents (TOC):**
   - Extract headings from Markdown
   - Display as sidebar navigation
   - Jump to sections

2. **Favorites/Bookmarks:**
   - Allow users to bookmark files
   - Store in user preferences
   - Quick access to favorite files

3. **Advanced Filters:**
   - Filter by date range
   - Filter by file size
   - Filter by topic + role combination

4. **Print Support:**
   - Print-friendly CSS
   - Export to PDF
   - Print multiple files

5. **Dark Mode Toggle:**
   - User preference
   - Persistent across sessions
   - System preference detection

6. **File Preview:**
   - Hover preview
   - Quick view modal
   - Side-by-side comparison

7. **Search Enhancements:**
   - Search within file
   - Highlight search results
   - Search history

8. **Analytics:**
   - Track most viewed files
   - Track search queries
   - Track role filter usage

### Related Files

**Backend:**
- `backend/apps/docs/views.py` - DocumentationViewSet
- `backend/apps/docs/urls.py` - URL routing
- `backend/core/urls.py` - Main URL configuration

**Frontend:**
- `frontend/src/pages/docs/DocumentationViewerPage.tsx` - Main component
- `frontend/src/services/docsAPI.ts` - API client
- `frontend/src/App.tsx` - Route configuration

**Dependencies:**
- `markdown` - Markdown to HTML conversion
- `Pygments` - Code syntax highlighting

---

## Changelog

### December 2024 (Latest)

#### Documentation Viewer System (New)
- ✅ Implemented comprehensive documentation viewer (`/docs`)
- ✅ Added file tree and topics view modes
- ✅ Implemented role-based filtering (9 roles)
- ✅ Added recent files tracking (last 10 files)
- ✅ Implemented keyboard shortcuts (Ctrl+F, Esc)
- ✅ Added breadcrumbs navigation
- ✅ Implemented file metadata display (size, date)
- ✅ Added scroll to top button
- ✅ Improved search with clear button
- ✅ Added welcome screen with helpful information
- ✅ Auto-open index file on first load
- ✅ Fixed useEffect dependency array warnings
- ✅ Added debug info panel (development mode)

#### WebSocket System
- ✅ Fixed WebSocket connection issues (WS-001)
- ✅ Added WebSocket support to WorkflowExecutionDetailPage
- ✅ Improved connection lifecycle management

### December 6, 2024
- Initial documentation created
- Added WebSocket connection issue (WS-001)
- Documented logging architecture
- Added audit trail documentation
- Created troubleshooting guide

---

**Document Status:** Active  
**Last Reviewed:** December 2024  
**Next Review:** January 2025

