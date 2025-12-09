# Features Master List - Partially Implemented Features

**Document Type:** Business Requirements Document (BRD)  
**Version:** 1.0.0  
**Created By:** BA Agent  
**Created Date:** December 9, 2024  
**Last Updated:** December 9, 2024  
**Last Updated By:** BA Agent  
**Status:** Active  
**Dependencies:** `01_overview_and_scope.md`, `02_features_master_list/01_complete_features.md`  
**Related Features:** All project management features

---

## 📋 Table of Contents

1. [Data Model Enhancements](#data-model-enhancements)
2. [Collaboration Features](#collaboration-features)
3. [Board Enhancements](#board-enhancements)
4. [Workflow & Automation](#workflow--automation)

---

## 1. Data Model Enhancements

### 1.1 Due Dates ⏳ PARTIAL

**Status:** Backend ✅, Frontend ⏳

**Description:**
Individual due dates for stories/tasks with tracking and notifications.

**Current Implementation:**
- **Backend:** `due_date` field on UserStory and Task models ✅
- **Backend:** Due date validation ✅
- **Frontend:** Due date input in forms ⏳ (partially implemented)
- **Frontend:** Due date display in cards ⏳ (partially implemented)
- **Frontend:** Due date approaching notifications ❌ (not implemented)

**Missing:**
- Due date display in Kanban cards
- Due date filtering
- Due date approaching notifications
- Overdue indicators

**Dependencies:**
- UserStory model
- Task model
- Notification system

**Cross-System Impact:**
- Affects filtering
- Affects notifications
- Affects board display

---

### 1.2 Epic Owner ⏳ PARTIAL

**Status:** Backend ✅, Frontend ⏳

**Description:**
Assign owner to epics for accountability.

**Current Implementation:**
- **Backend:** `owner` field on Epic model ✅
- **Backend:** Owner filtering ✅
- **Frontend:** Owner selection in Epic form ⏳ (partially implemented)
- **Frontend:** Owner display in Epic cards ⏳ (partially implemented)

**Missing:**
- Owner display in Epic list
- Owner filtering in Epic views
- Owner assignment notifications

**Dependencies:**
- Epic model
- User model

**Cross-System Impact:**
- Affects Epic management
- Affects filtering

---

### 1.3 Story Type ⏳ PARTIAL

**Status:** Backend ✅, Frontend ⏳

**Description:**
Story type classification (Feature, Bug, Enhancement, Technical Debt, etc.).

**Current Implementation:**
- **Backend:** `story_type` field on UserStory model ✅
- **Backend:** STORY_TYPE_CHOICES defined ✅
- **Frontend:** Story type selection in forms ⏳ (partially implemented)
- **Frontend:** Story type display in cards ⏳ (partially implemented)

**Missing:**
- Story type filtering
- Story type grouping in board
- Story type statistics

**Dependencies:**
- UserStory model

**Cross-System Impact:**
- Affects filtering
- Affects board grouping

---

### 1.4 Labels ⏳ PARTIAL

**Status:** Backend ✅, Frontend ⏳

**Description:**
Color-coded labels (different from tags) for visual grouping.

**Current Implementation:**
- **Backend:** `labels` JSONField on UserStory, Task, Bug, Issue models ✅
- **Backend:** Label structure: `[{'name': 'Urgent', 'color': '#red'}]` ✅
- **Frontend:** Label input in forms ⏳ (partially implemented)
- **Frontend:** Label display in cards ⏳ (partially implemented)

**Missing:**
- Label management UI
- Label color picker
- Label filtering
- Label grouping

**Dependencies:**
- Work item models

**Cross-System Impact:**
- Affects filtering
- Affects board display

---

### 1.5 Components ⏳ PARTIAL

**Status:** Backend ✅, Frontend ⏳

**Description:**
Component/module assignment for work items.

**Current Implementation:**
- **Backend:** `component` field on UserStory, Task, Bug, Issue models ✅
- **Backend:** Component filtering ✅
- **Frontend:** Component input in forms ⏳ (partially implemented)
- **Frontend:** Component display in cards ⏳ (partially implemented)

**Missing:**
- Component autocomplete
- Component filtering
- Component grouping in board
- Component statistics

**Dependencies:**
- Work item models

**Cross-System Impact:**
- Affects filtering
- Affects board grouping

---

## 2. Collaboration Features

### 2.1 User Avatars ⏳ PARTIAL

**Status:** Partial (avatars shown in comments)

**Description:**
Display user avatars in cards, comments, mentions.

**Current Implementation:**
- **Frontend:** Avatars shown in comments ✅
- **Frontend:** Avatars in cards ❌ (not implemented)
- **Frontend:** Avatars in mentions ❌ (not implemented)

**Missing:**
- Avatar display in Kanban cards
- Avatar display in mentions
- Avatar upload/management
- Default avatar generation

**Dependencies:**
- User model
- File storage (for avatar uploads)

**Cross-System Impact:**
- Affects UI display
- Affects user experience

---

## 3. Board Enhancements

### 3.1 Card Colors ⏳ PARTIAL

**Status:** Partial (colors from states work, custom colors pending)

**Description:**
Color-code cards by priority, epic, type, component.

**Current Implementation:**
- **Backend:** `card_color_by` configuration ✅
- **Frontend:** Colors from states work ✅
- **Frontend:** Custom colors based on priority/epic/type ❌ (not fully implemented)

**Missing:**
- Custom color application based on configuration
- Color coding by epic
- Color coding by type
- Color coding by component

**Dependencies:**
- Board configuration
- Kanban components

**Cross-System Impact:**
- Affects board display
- Affects visual grouping

---

### 3.2 Board Views (Timeline & Calendar) ❌ NOT IMPLEMENTED

**Status:** Not Implemented

**Description:**
Timeline and Calendar board views.

**Current Implementation:**
- **Backend:** Configuration supports timeline/calendar ✅
- **Frontend:** Timeline view ❌ (not implemented)
- **Frontend:** Calendar view ❌ (not implemented)

**Missing:**
- Timeline view component
- Calendar view component
- Date-based filtering
- Drag-and-drop in timeline/calendar

**Dependencies:**
- Board components
- Date utilities

**Cross-System Impact:**
- Affects board views
- Affects user experience

---

## 4. Workflow & Automation

### 4.1 Automation Rule Execution (Full) ⏳ PARTIAL

**Status:** Structure Complete, Some Triggers Missing

**Description:**
Full automation rule execution for all trigger types.

**Current Implementation:**
- **Backend:** Automation engine ✅
- **Backend:** Status change triggers ✅
- **Backend:** Field update triggers ✅
- **Backend:** On-create triggers ⏳ (partially implemented)
- **Backend:** On-task-complete triggers ⏳ (partially implemented)

**Missing:**
- Full on-create trigger support
- Full on-task-complete trigger support
- Scheduled triggers
- Conditional triggers

**Dependencies:**
- Automation service
- Project configuration

**Cross-System Impact:**
- Affects workflow automation
- Affects user experience

---

### 4.2 Notification Delivery (Email) ❌ NOT IMPLEMENTED

**Status:** Structure Exists, Email Delivery Not Implemented

**Description:**
Email notification delivery for events.

**Current Implementation:**
- **Backend:** Notification model ✅
- **Backend:** In-app notifications ✅
- **Backend:** Email notification settings ✅
- **Backend:** Email delivery ❌ (not implemented)

**Missing:**
- Email template system
- Email delivery service
- Email preferences
- Email digests

**Dependencies:**
- Notification service
- Email service
- Project configuration

**Cross-System Impact:**
- Affects notifications
- Affects user engagement

---

### 4.3 Integration Execution ❌ NOT IMPLEMENTED

**Status:** Structure Exists, Actual Integrations Not Implemented

**Description:**
External integrations (GitHub, Jira, Slack).

**Current Implementation:**
- **Backend:** Integration settings JSONField ✅
- **Backend:** Integration structure ✅
- **Backend:** GitHub integration ❌ (not implemented)
- **Backend:** Jira integration ❌ (not implemented)
- **Backend:** Slack integration ❌ (not implemented)

**Missing:**
- GitHub webhook handling
- Jira API integration
- Slack webhook integration
- Integration authentication
- Integration data sync

**Dependencies:**
- Integration service
- External APIs
- Project configuration

**Cross-System Impact:**
- Affects external tool integration
- Affects workflow

---

**End of Document**

**Next Document:** `03_planned_features.md` - Not implemented but planned features

