# Quick Start Guide - Project Configuration & Approval Workflow

**Date:** December 9, 2024

---

## 🚀 Getting Started

### 1. Run Database Migration

The approval workflow requires a new database table. Run:

```bash
cd backend
python manage.py makemigrations projects --name add_status_change_approval
python manage.py migrate
```

### 2. Verify Celery Task

Ensure the auto-close sprints task is scheduled:

```bash
# Check backend/core/celery.py has:
'app.conf.beat_schedule = {
    ...
    "auto-close-sprints": {
        "task": "apps.projects.tasks.auto_close_sprints",
        "schedule": crontab(hour=4, minute=0),
    },
}'
```

Start Celery worker and beat:
```bash
celery -A core worker -l info
celery -A core beat -l info
```

---

## 📋 Configuration Guide

### Enable Approval Workflow

1. Navigate to **Project Settings** → **Permissions**
2. Enable **"Require Approval for Status Change"**
3. Save configuration

### Configure Custom States

1. Navigate to **Project Settings** → **Workflow**
2. Define custom states (e.g., Backlog, To Do, In Progress, Review, Done)
3. Configure state transitions (which states can transition to which)
4. Save configuration

### Set Up Custom Fields

1. Navigate to **Project Settings** → **Custom Fields**
2. Add custom field definitions:
   - Field ID (unique identifier)
   - Field Name (display name)
   - Field Type (text, number, date, select, multi_select, boolean)
   - Required (yes/no)
   - Options (for select/multi_select)
3. Save configuration

### Configure Permissions

1. Navigate to **Project Settings** → **Permissions**
2. Set who can:
   - Create stories/tasks/bugs/issues
   - Edit stories/tasks/bugs/issues
   - Delete work items
   - Manage sprints
   - Add/remove members
3. Save configuration

---

## 🎯 Usage Examples

### Example 1: Status Change with Approval

1. **User edits a story** and changes status from "In Progress" to "Done"
2. **If approval is required:**
   - Approval modal appears
   - User enters reason: "All acceptance criteria met, tested and verified"
   - Approval request is created
   - Status remains "In Progress" until approved

3. **Approver reviews:**
   - Sees pending approval in list
   - Clicks "Approve"
   - Enters optional comment: "Looks good!"
   - Status changes to "Done"

### Example 2: Custom Fields

1. **Project has custom field:** "Release Version" (select: v1.0, v1.1, v2.0)
2. **User creates story:**
   - Custom field appears in form
   - User selects "v2.0"
   - Story is saved with custom field value

3. **Story displays:**
   - Custom field shown in story details
   - Can filter/search by custom field

### Example 3: Automation Rule

1. **Configure rule:**
   - Trigger: Status changes to "Done"
   - Action: Assign to project owner
   - Action: Notify assignee

2. **When story status changes to "Done":**
   - Story is automatically assigned to project owner
   - Project owner receives notification

---

## 🔍 Testing Checklist

### Basic Functionality
- [ ] Create project with custom configuration
- [ ] Create story with custom fields
- [ ] Change story status (with/without approval)
- [ ] View board in Kanban/List/Table views
- [ ] Create sprint with default values
- [ ] Add member with default role

### Approval Workflow
- [ ] Enable approval workflow
- [ ] Try changing status - should show approval modal
- [ ] Create approval request
- [ ] View pending approvals list
- [ ] Approve request - status should change
- [ ] Reject request - status should remain unchanged

### Permissions
- [ ] Test as project owner (should see all actions)
- [ ] Test as project member (should see limited actions)
- [ ] Test as viewer (should see read-only)

### Automation
- [ ] Create automation rule
- [ ] Trigger rule (e.g., status change)
- [ ] Verify action executed (e.g., assign, notify)

---

## 📚 Documentation

- **Full Implementation:** `FINAL_IMPLEMENTATION_SUMMARY.md`
- **Approval Workflow:** `APPROVAL_WORKFLOW_COMPLETE.md`
- **Remaining Work:** `REMAINING_WORK.md`
- **Verification:** `IMPLEMENTATION_VERIFICATION.md`

---

## 🆘 Troubleshooting

### Approval requests not showing
- Check `require_approval_for_status_change` is enabled
- Verify user has permission to view approvals
- Check browser console for errors

### Custom fields not appearing
- Verify `custom_fields_schema` is configured
- Check field IDs match schema
- Ensure form includes `CustomFieldsForm` component

### Automation not triggering
- Check automation rules are configured
- Verify trigger conditions match
- Check Celery worker is running (for scheduled tasks)

### Permissions not working
- Verify `permission_settings` are saved
- Check user role in project
- Ensure `useProjectPermissions` hook is used

---

**Last Updated:** December 9, 2024

