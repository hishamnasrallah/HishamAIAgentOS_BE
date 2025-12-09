# Business Logic Rules - Validation and Constraints

**Document Type:** Business Requirements Document (BRD)  
**Version:** 1.0.0  
**Created By:** BA Agent  
**Created Date:** December 9, 2024  
**Last Updated:** December 9, 2024  
**Last Updated By:** BA Agent  
**Status:** Active  
**Dependencies:** `01_overview_and_scope.md`, `04_business_logic_rules/01_workflow_and_state_management.md`  
**Related Features:** All project management features

---

## 📋 Table of Contents

1. [Story Points Validation Rules](#story-points-validation-rules)
2. [Required Fields Validation](#required-fields-validation)
3. [Task Completion Validation](#task-completion-validation)
4. [Sprint Capacity Validation](#sprint-capacity-validation)
5. [Date Validation Rules](#date-validation-rules)
6. [Relationship Validation](#relationship-validation)

---

## 1. Story Points Validation Rules

### 1.1 Story Point Scale Validation
- **Rule:** Story points must be from allowed scale if configured
- **Rule:** Scale defined in `ProjectConfiguration.story_point_scale` (JSONField)
- **Rule:** Default scale: Fibonacci [1, 2, 3, 5, 8, 13, 21]
- **Rule:** Validation occurs in serializer and model
- **Rule:** Invalid story points raise ValidationError with allowed values

### 1.2 Story Point Limits Validation
- **Rule:** Story points must be within min/max limits
- **Rule:** Min limit: `ProjectConfiguration.min_story_points_per_story` (default: 1)
- **Rule:** Max limit: `ProjectConfiguration.max_story_points_per_story` (default: 21)
- **Rule:** Validation occurs in serializer
- **Rule:** Out-of-range story points raise ValidationError

### 1.3 Story Points Required Validation
- **Rule:** Story points may be required before moving to 'in_progress'
- **Rule:** Controlled by `ProjectConfiguration.story_points_required` (boolean)
- **Rule:** If enabled, story points must be set before status change to 'in_progress'
- **Rule:** Validation occurs in ValidationService
- **Rule:** Missing story points raise ValidationError

### 1.4 Sprint Capacity Validation
- **Rule:** Sprint total story points cannot exceed max if overcommitment not allowed
- **Rule:** Max limit: `ProjectConfiguration.max_story_points_per_sprint` (default: 40)
- **Rule:** Overcommitment: `ProjectConfiguration.allow_overcommitment` (boolean)
- **Rule:** If overcommitment disabled, validation error on capacity exceed
- **Rule:** If overcommitment enabled, warning only
- **Rule:** Validation occurs in serializer and ValidationService

---

## 2. Required Fields Validation

### 2.1 Always Required Fields
- **Rule:** Title always required for all work items
- **Rule:** Description always required for stories, epics, bugs, issues
- **Rule:** Description optional for tasks
- **Rule:** Validation occurs in serializer
- **Rule:** Missing required fields raise ValidationError

### 2.2 Conditionally Required Fields

#### Assignee Requirement
- **Rule:** Assignee may be required before moving to 'in_progress'
- **Rule:** Controlled by `ProjectConfiguration.validation_rules.require_assignee_before_in_progress`
- **Rule:** If enabled, assignee must be set before status change to 'in_progress'
- **Rule:** Validation occurs in ValidationService
- **Rule:** Missing assignee raises ValidationError

#### Acceptance Criteria Requirement
- **Rule:** Acceptance criteria may be required
- **Rule:** Controlled by `ProjectConfiguration.validation_rules.require_acceptance_criteria`
- **Rule:** If enabled, acceptance criteria must be non-empty
- **Rule:** Validation occurs in ValidationService
- **Rule:** Missing acceptance criteria raises ValidationError

#### Description Length Requirement
- **Rule:** Description may have minimum length requirement
- **Rule:** Controlled by `ProjectConfiguration.validation_rules.require_description_min_length`
- **Rule:** If set, description must be at least N characters
- **Rule:** Validation occurs in ValidationService
- **Rule:** Short description raises ValidationError

---

## 3. Task Completion Validation

### 3.1 Task Completion Blocking
- **Rule:** Story status change to 'done' may be blocked if tasks incomplete
- **Rule:** Controlled by `ProjectConfiguration.validation_rules.block_status_change_if_tasks_incomplete`
- **Rule:** If enabled, all tasks must be 'done' before story can be 'done'
- **Rule:** Validation occurs in ValidationService
- **Rule:** Incomplete tasks raise ValidationError

### 3.2 Task Status Validation
- **Rule:** Task status must be from project's custom states
- **Rule:** Task status validated against story's project configuration
- **Rule:** Validation occurs in model clean() method
- **Rule:** Invalid status raises ValidationError

### 3.3 Task Progress Validation
- **Rule:** Progress percentage must be 0-100
- **Rule:** Validation occurs in model (MinValueValidator, MaxValueValidator)
- **Rule:** Out-of-range progress raises ValidationError

---

## 4. Sprint Capacity Validation

### 4.1 Sprint Story Points Limit
- **Rule:** Sprint total story points cannot exceed max if overcommitment not allowed
- **Rule:** Max limit: `ProjectConfiguration.max_story_points_per_sprint`
- **Rule:** Overcommitment: `ProjectConfiguration.allow_overcommitment`
- **Rule:** Validation occurs in SprintSerializer
- **Rule:** Capacity exceeded raises ValidationError (if overcommitment disabled)

### 4.2 Sprint Capacity Warnings
- **Rule:** Warnings shown when capacity exceeded (even if overcommitment allowed)
- **Rule:** Controlled by `ProjectConfiguration.validation_rules.warn_if_story_points_exceed_sprint_capacity`
- **Rule:** Warnings do not block operations
- **Rule:** Warnings returned in serializer warnings list

### 4.3 Sprint Date Validation
- **Rule:** Sprint start_date must be before end_date
- **Rule:** Sprint dates must be within project dates (if project has dates)
- **Rule:** Sprints cannot overlap
- **Rule:** Validation occurs in SprintSerializer
- **Rule:** Invalid dates raise ValidationError

---

## 5. Date Validation Rules

### 5.1 Date Range Validation
- **Rule:** End dates must be after start dates
- **Rule:** Applies to: Project, Sprint, Epic, Work items with due dates
- **Rule:** Validation occurs in serializer
- **Rule:** Invalid date ranges raise ValidationError

### 5.2 Project Date Constraints
- **Rule:** Sprint dates must be within project dates (if project has dates)
- **Rule:** Sprint start_date >= project.start_date (if project.start_date exists)
- **Rule:** Sprint end_date <= project.end_date (if project.end_date exists)
- **Rule:** Validation occurs in SprintSerializer
- **Rule:** Out-of-range dates raise ValidationError

### 5.3 Due Date Validation
- **Rule:** Due dates are optional
- **Rule:** Due dates can be in past (for tracking)
- **Rule:** No validation on due date range (flexible)
- **Rule:** Future enhancement: Due date approaching notifications

---

## 6. Relationship Validation

### 6.1 Foreign Key Validation
- **Rule:** All foreign keys must reference existing objects
- **Rule:** Foreign keys validated by Django ORM
- **Rule:** Invalid foreign keys raise DoesNotExist exception
- **Rule:** Validation occurs in serializer

### 6.2 Circular Reference Validation

#### Task Parent-Child
- **Rule:** Task cannot be its own parent
- **Rule:** Task cannot have circular parent chain
- **Rule:** Validation occurs in model clean() method
- **Rule:** Circular reference raises ValidationError

#### Story Dependencies
- **Rule:** Story cannot depend on itself
- **Rule:** Circular dependencies detected and prevented
- **Rule:** Validation occurs in StoryDependencySerializer
- **Rule:** Circular dependency raises ValidationError

### 6.3 Many-to-Many Validation
- **Rule:** Project members must be valid users
- **Rule:** Issue watchers must be valid users
- **Rule:** Bug linked_stories must be valid stories
- **Rule:** Validation occurs in serializer

### 6.4 Unique Constraint Validation
- **Rule:** Project slug must be unique
- **Rule:** Sprint (project, sprint_number) must be unique
- **Rule:** Validation occurs in model and serializer
- **Rule:** Duplicate values raise IntegrityError

---

## 7. Custom Field Validation

### 7.1 Schema Validation
- **Rule:** Custom field values must match schema
- **Rule:** Schema defined in `ProjectConfiguration.custom_fields_schema`
- **Rule:** Field types validated (text, number, select, date, boolean)
- **Rule:** Required custom fields validated
- **Rule:** Validation occurs in serializer

### 7.2 Value Validation
- **Rule:** Text fields: Max length validation
- **Rule:** Number fields: Min/max value validation
- **Rule:** Select fields: Value must be from allowed options
- **Rule:** Date fields: Date format validation
- **Rule:** Boolean fields: True/false validation
- **Rule:** Validation occurs in serializer

---

## 8. Permission-Based Validation

### 8.1 Permission Checks
- **Rule:** All operations require appropriate permissions
- **Rule:** Permission checks occur in ViewSet and Service layers
- **Rule:** Insufficient permissions raise PermissionDenied exception
- **Rule:** Permission settings from ProjectConfiguration

### 8.2 Role-Based Validation
- **Rule:** Admin has full access
- **Rule:** Owner has full access
- **Rule:** Member access based on permission settings
- **Rule:** Viewer has read-only access
- **Rule:** Validation occurs in PermissionEnforcementService

---

**End of Document**

**Next Document:** `03_permission_rules.md` - Permission enforcement rules

