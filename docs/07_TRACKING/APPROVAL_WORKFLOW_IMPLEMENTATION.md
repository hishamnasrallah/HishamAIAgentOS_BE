# Approval Workflow Implementation - Complete

**Date:** December 9, 2024  
**Status:** ✅ 100% Complete

---

## 🎉 Implementation Summary

The approval workflow system has been fully implemented, allowing projects to require approval for status changes when `require_approval_for_status_change` is enabled in project configuration.

---

## ✅ Backend Implementation

### 1. Model: `StatusChangeApproval`
**Location:** `backend/apps/projects/models.py`

**Features:**
- Generic foreign key to work items (Story, Task, Bug, Issue)
- Status tracking: `pending`, `approved`, `rejected`, `cancelled`
- Tracks old and new status
- Stores approval reason and rejection reason
- Links to project, requester, approver, and approver
- Methods: `approve()`, `reject()`, `cancel()`, `_apply_status_change()`

**Database Fields:**
- `id` (UUID, primary key)
- `content_type` (GenericForeignKey)
- `object_id` (UUID)
- `old_status`, `new_status` (CharField)
- `reason`, `rejection_reason` (TextField)
- `status` (CharField, choices)
- `requested_by`, `approver`, `approved_by` (ForeignKey to User)
- `project` (ForeignKey to Project)
- `created_at`, `updated_at`, `approved_at` (DateTimeField)

---

### 2. Serializer: `StatusChangeApprovalSerializer`
**Location:** `backend/apps/projects/serializers_approval.py`

**Features:**
- Full CRUD support
- Read-only fields: `id`, `created_at`, `updated_at`, `approved_by`, `approved_at`, `requested_by`, `content_type`, `object_id`, `project`
- Computed fields: `requested_by_name`, `approver_name`, `approved_by_name`, `work_item_title`, `work_item_type`, `project_name`
- Validation: Only pending approvals can be modified

---

### 3. ViewSet: `StatusChangeApprovalViewSet`
**Location:** `backend/apps/projects/views.py`

**Endpoints:**
- `GET /api/v1/projects/status-change-approvals/` - List approvals
- `POST /api/v1/projects/status-change-approvals/` - Create approval request
- `GET /api/v1/projects/status-change-approvals/{id}/` - Get approval details
- `PATCH /api/v1/projects/status-change-approvals/{id}/` - Update approval
- `POST /api/v1/projects/status-change-approvals/{id}/approve/` - Approve request
- `POST /api/v1/projects/status-change-approvals/{id}/reject/` - Reject request
- `POST /api/v1/projects/status-change-approvals/{id}/cancel/` - Cancel request

**Features:**
- Permission filtering: Users see their own requests, requests they need to approve, or all if project owner/admin
- Project-based filtering via query parameter
- Status filtering via query parameter
- Automatic approver assignment (defaults to project owner)

---

### 4. Serializer Integration

**Location:** `backend/apps/projects/serializers.py`

**Updated Serializers:**
- ✅ `StorySerializer.update()` - Checks for approval requirement
- ✅ `TaskSerializer.update()` - Checks for approval requirement
- ✅ `BugSerializer.update()` - Checks for approval requirement
- ✅ `IssueSerializer.update()` - Checks for approval requirement

**Logic:**
1. Before status change, check if `require_approval_for_status_change` is enabled
2. If enabled, create `StatusChangeApproval` request instead of changing status
3. Return validation error with approval ID
4. Status change is applied when approval is approved

---

## ✅ Frontend Implementation

### 1. API Service: `approvalsAPI`
**Location:** `frontend/src/services/api.ts`

**Methods:**
- `list(params?)` - List approvals with optional project/status filters
- `get(id)` - Get approval details
- `create(data)` - Create approval request
- `approve(id, comment?)` - Approve request
- `reject(id, reason)` - Reject request
- `cancel(id)` - Cancel request

---

### 2. Hook: `useApprovals`
**Location:** `frontend/src/hooks/useApprovals.ts`

**Features:**
- Query approvals with filters
- Mutations for create, approve, reject, cancel
- Automatic query invalidation on mutations
- Toast notifications for success/error
- Helper hook: `usePendingApprovals(projectId)`

**Returns:**
- `approvals` - Array of approval objects
- `isLoading` - Loading state
- `error` - Error object
- `createApproval`, `approve`, `reject`, `cancel` - Mutation functions
- `isCreating`, `isApproving`, `isRejecting`, `isCancelling` - Loading states

---

### 3. Components

#### `ApprovalRequestModal`
**Location:** `frontend/src/components/approvals/ApprovalRequestModal.tsx`

**Features:**
- Modal for creating approval requests
- Shows work item title and status change
- Required reason field
- Integrates with `useApprovals` hook
- Success callback support

**Props:**
- `open` - Modal visibility
- `onOpenChange` - Visibility change handler
- `workItemType` - 'userstory' | 'task' | 'bug' | 'issue'
- `workItemId` - Work item UUID
- `workItemTitle` - Work item title
- `oldStatus` - Current status
- `newStatus` - Desired status
- `onSuccess` - Success callback

---

#### `PendingApprovalsList`
**Location:** `frontend/src/components/approvals/PendingApprovalsList.tsx`

**Features:**
- Lists pending approval requests
- Shows approval details (work item, status change, reason, requester)
- Approve/reject buttons for approvers
- Cancel button for requesters
- Approval/rejection dialogs with comments
- Compact mode for badges
- Empty state handling

**Props:**
- `projectId` - Project UUID
- `compact` - Show as badge only (optional)

---

### 4. Form Integration

#### `StoryEditModal`
**Location:** `frontend/src/components/stories/StoryEditModal.tsx`

**Integration:**
- Checks `require_approval_for_status_change` from configuration
- Shows `ApprovalRequestModal` when status change requires approval
- Handles backend approval response
- Shows success toast when approval request is created

**Flow:**
1. User changes status in form
2. Form checks if approval is required
3. If yes, shows approval modal instead of submitting
4. User fills reason and submits approval request
5. Backend creates approval request
6. Status change is applied when approval is approved

---

### 5. Board Integration

#### `BoardPage`
**Location:** `frontend/src/pages/projects/BoardPage.tsx`

**Features:**
- Shows pending approvals badge at top of page
- Displays count of pending approvals
- "Review Approvals" button to navigate to approvals page
- Yellow warning banner when approvals are pending

---

## 📋 Usage

### Enabling Approval Workflow

1. Go to Project Settings → Permissions
2. Enable `require_approval_for_status_change`
3. Save configuration

### Requesting Approval

1. User attempts to change work item status
2. If approval is required, approval modal appears
3. User enters reason for status change
4. Approval request is created
5. Status remains unchanged until approved

### Approving/Rejecting

1. Approver sees pending approvals in list
2. Clicks "Approve" or "Reject"
3. Enters optional comment (approve) or required reason (reject)
4. Status change is applied if approved
5. Notification sent to requester

---

## 🔄 Workflow Diagram

```
User Changes Status
    ↓
Check require_approval_for_status_change
    ↓
Is Approval Required?
    ├─ No → Apply Status Change Directly
    └─ Yes → Create Approval Request
            ↓
        Status Remains Unchanged
            ↓
        Approver Reviews Request
            ↓
        Approve or Reject?
            ├─ Approve → Apply Status Change
            └─ Reject → Notify Requester
```

---

## 📝 Database Migration

**Required Migration:**
```bash
python manage.py makemigrations projects --name add_status_change_approval
python manage.py migrate
```

**Migration Creates:**
- `status_change_approvals` table
- Indexes on `project`, `status`, `content_type`, `object_id`, `requested_by`, `approver`

---

## 🧪 Testing Checklist

- [ ] Enable approval workflow in project settings
- [ ] Try changing story status - should show approval modal
- [ ] Create approval request with reason
- [ ] View pending approvals list
- [ ] Approve request - status should change
- [ ] Reject request - status should remain unchanged
- [ ] Cancel own request
- [ ] Test with Task/Bug/Issue
- [ ] Test permission filtering (only see own requests or requests to approve)
- [ ] Test project owner can approve any request

---

## 📊 Files Created/Modified

### Backend
- ✅ `backend/apps/projects/models.py` - Added `StatusChangeApproval` model
- ✅ `backend/apps/projects/serializers_approval.py` - New serializer file
- ✅ `backend/apps/projects/serializers.py` - Added approval checks to all work item serializers
- ✅ `backend/apps/projects/views.py` - Added `StatusChangeApprovalViewSet`
- ✅ `backend/apps/projects/urls.py` - Registered approval endpoints

### Frontend
- ✅ `frontend/src/services/api.ts` - Added `approvalsAPI`
- ✅ `frontend/src/hooks/useApprovals.ts` - New hook
- ✅ `frontend/src/components/approvals/ApprovalRequestModal.tsx` - New component
- ✅ `frontend/src/components/approvals/PendingApprovalsList.tsx` - New component
- ✅ `frontend/src/components/stories/StoryEditModal.tsx` - Integrated approval workflow
- ✅ `frontend/src/pages/projects/BoardPage.tsx` - Added pending approvals badge

---

## 🎯 Future Enhancements (Optional)

1. **Email Notifications** - Send emails when approval is requested/approved/rejected
2. **Approval History** - Show history of all approvals (not just pending)
3. **Multiple Approvers** - Support for requiring multiple approvals
4. **Approval Timeouts** - Auto-reject if not approved within time limit
5. **Approval Templates** - Pre-defined approval workflows
6. **Approval Delegation** - Allow approvers to delegate to others
7. **Approval Comments** - Threaded comments on approval requests
8. **Approval Analytics** - Track approval times, rejection rates, etc.

---

## ✅ Status

**Implementation:** ✅ 100% Complete  
**Backend:** ✅ Complete  
**Frontend:** ✅ Complete  
**Integration:** ✅ Complete  
**Testing:** ⏳ Pending User Testing

---

**Last Updated:** December 9, 2024

