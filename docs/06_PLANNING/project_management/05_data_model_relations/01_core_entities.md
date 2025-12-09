# Data Model Relations - Core Entities

**Document Type:** Business Requirements Document (BRD)  
**Version:** 1.0.0  
**Created By:** BA Agent  
**Created Date:** December 9, 2024  
**Last Updated:** December 9, 2024  
**Last Updated By:** BA Agent  
**Status:** Active  
**Dependencies:** `01_overview_and_scope.md`  
**Related Features:** All project management features

---

## 📋 Table of Contents

1. [Project Model](#project-model)
2. [Epic Model](#epic-model)
3. [UserStory Model](#userstory-model)
4. [Task Model](#task-model)
5. [Sprint Model](#sprint-model)
6. [Relationships Overview](#relationships-overview)

---

## 1. Project Model

### 1.1 Fields
```python
id: UUID (primary key, auto-generated)
name: CharField(max_length=200)
slug: SlugField(max_length=200, unique=True)
description: TextField(blank=True, default='')
status: CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
start_date: DateField(null=True, blank=True)
end_date: DateField(null=True, blank=True)
owner: ForeignKey(User, SET_NULL, null=True, related_name='owned_projects')
members: ManyToManyField(User, related_name='projects', blank=True)
tags: JSONField(default=list, blank=True)
created_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='created_projects')
updated_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='updated_projects')
created_at: DateTimeField(auto_now_add=True, db_index=True)
updated_at: DateTimeField(auto_now=True, db_index=True)
```

### 1.2 Indexes
- `['slug']` - For slug-based lookups
- `['status']` - For status filtering

### 1.3 Relationships
- **One-to-One:** Project → ProjectConfiguration
- **One-to-Many:** Project → Epics
- **One-to-Many:** Project → UserStories
- **One-to-Many:** Project → Tasks (via stories)
- **One-to-Many:** Project → Sprints
- **One-to-Many:** Project → Bugs
- **One-to-Many:** Project → Issues
- **Many-to-Many:** Project ↔ Users (members)

### 1.4 Cascade Behavior
- **CASCADE:** Deleting project deletes all related entities (epics, stories, sprints, etc.)
- **SET_NULL:** Owner, created_by, updated_by set to NULL if user deleted

---

## 2. Epic Model

### 2.1 Fields
```python
id: UUID (primary key, auto-generated)
project: ForeignKey(Project, CASCADE, related_name='epics')
title: CharField(max_length=300)
description: TextField()
status: CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
start_date: DateField(null=True, blank=True)
target_date: DateField(null=True, blank=True)
tags: JSONField(default=list, blank=True)
owner: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='owned_epics')
created_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='created_epics')
updated_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='updated_epics')
created_at: DateTimeField(auto_now_add=True, db_index=True)
updated_at: DateTimeField(auto_now=True, db_index=True)
```

### 2.2 Indexes
- `['project', 'status']` - For filtering epics by project and status

### 2.3 Relationships
- **Many-to-One:** Epic → Project (CASCADE)
- **One-to-Many:** Epic → UserStories (SET_NULL)
- **Many-to-One:** Epic → Owner (SET_NULL)

### 2.4 Cascade Behavior
- **CASCADE:** Deleting project deletes epic
- **SET_NULL:** Deleting epic sets story.epic to NULL
- **SET_NULL:** Owner set to NULL if user deleted

---

## 3. UserStory Model

### 3.1 Fields
```python
id: UUID (primary key, auto-generated)
project: ForeignKey(Project, CASCADE, related_name='stories')
epic: ForeignKey(Epic, SET_NULL, null=True, blank=True, related_name='stories')
sprint: ForeignKey(Sprint, SET_NULL, null=True, blank=True, related_name='stories')
title: CharField(max_length=300)
description: TextField()
acceptance_criteria: TextField()
status: CharField(max_length=50, default='backlog')  # Validated against custom_states
priority: CharField(max_length=20, default='medium')
story_points: IntegerField(null=True, blank=True)
story_type: CharField(max_length=20, choices=STORY_TYPE_CHOICES, default='feature')
component: CharField(max_length=100, blank=True)
due_date: DateField(null=True, blank=True)
labels: JSONField(default=list, blank=True)
tags: JSONField(default=list, blank=True)
custom_fields: JSONField(default=dict, blank=True)
assigned_to: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='assigned_stories')
generated_by_ai: BooleanField(default=False)
generation_workflow: ForeignKey(WorkflowExecution, SET_NULL, null=True, blank=True)
created_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='created_stories')
updated_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='updated_stories')
created_at: DateTimeField(auto_now_add=True, db_index=True)
updated_at: DateTimeField(auto_now=True, db_index=True)
```

### 3.2 Indexes
- `['project', 'status']` - For filtering stories by project and status
- `['sprint', 'status']` - For filtering stories by sprint and status

### 3.3 Relationships
- **Many-to-One:** UserStory → Project (CASCADE)
- **Many-to-One:** UserStory → Epic (SET_NULL)
- **Many-to-One:** UserStory → Sprint (SET_NULL)
- **Many-to-One:** UserStory → AssignedTo (SET_NULL)
- **One-to-Many:** UserStory → Tasks (CASCADE)
- **One-to-Many:** UserStory → Comments (CASCADE)
- **One-to-Many:** UserStory → Attachments (CASCADE)
- **One-to-Many:** UserStory → Dependencies (outgoing) (CASCADE)
- **One-to-Many:** UserStory → Dependencies (incoming) (CASCADE)
- **One-to-Many:** UserStory → Mentions (CASCADE)
- **One-to-Many:** UserStory → Time Logs (CASCADE)

### 3.4 Cascade Behavior
- **CASCADE:** Deleting project deletes story
- **CASCADE:** Deleting story deletes tasks, comments, attachments, dependencies, mentions, time logs
- **SET_NULL:** Deleting epic sets story.epic to NULL
- **SET_NULL:** Deleting sprint sets story.sprint to NULL
- **SET_NULL:** AssignedTo, created_by, updated_by set to NULL if user deleted

---

## 4. Task Model

### 4.1 Fields
```python
id: UUID (primary key, auto-generated)
story: ForeignKey(UserStory, CASCADE, null=True, blank=True, related_name='tasks')
parent_task: ForeignKey('self', CASCADE, null=True, blank=True, related_name='subtasks')
title: CharField(max_length=300)
description: TextField(blank=True)
status: CharField(max_length=50, default='todo')  # Validated against custom_states
priority: CharField(max_length=20, default='medium')
assigned_to: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='assigned_tasks')
estimated_hours: DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
actual_hours: DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
progress_percentage: IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
tags: JSONField(default=list, blank=True)
labels: JSONField(default=list, blank=True)
custom_fields: JSONField(default=dict, blank=True)
component: CharField(max_length=100, blank=True)
due_date: DateField(null=True, blank=True)
created_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='created_tasks')
updated_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='updated_tasks')
created_at: DateTimeField(auto_now_add=True, db_index=True)
updated_at: DateTimeField(auto_now=True, db_index=True)
```

### 4.2 Indexes
- `['story', 'status']` - For filtering tasks by story and status
- `['parent_task', 'status']` - For filtering tasks by parent and status
- `['assigned_to', 'status']` - For filtering tasks by assignee and status

### 4.3 Relationships
- **Many-to-One:** Task → Story (CASCADE, nullable for standalone tasks)
- **Many-to-One:** Task → ParentTask (CASCADE, self-referential)
- **Many-to-One:** Task → AssignedTo (SET_NULL)
- **One-to-Many:** Task → Subtasks (CASCADE)
- **One-to-Many:** Task → Time Logs (CASCADE)

### 4.4 Cascade Behavior
- **CASCADE:** Deleting story deletes task
- **CASCADE:** Deleting parent task deletes subtasks
- **SET_NULL:** AssignedTo, created_by, updated_by set to NULL if user deleted

### 4.5 Validation
- **Circular Reference:** Task cannot be its own parent
- **Circular Reference:** Task cannot have circular parent chain

---

## 5. Sprint Model

### 5.1 Fields
```python
id: UUID (primary key, auto-generated)
project: ForeignKey(Project, CASCADE, related_name='sprints')
name: CharField(max_length=200)
sprint_number: IntegerField()
goal: TextField(blank=True)
status: CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
start_date: DateField()
end_date: DateField()
total_story_points: IntegerField(default=0)
completed_story_points: IntegerField(default=0)
created_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='created_sprints')
updated_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='updated_sprints')
created_at: DateTimeField(auto_now_add=True, db_index=True)
updated_at: DateTimeField(auto_now=True, db_index=True)
```

### 5.2 Indexes
- Unique constraint: `['project', 'sprint_number']` - Unique sprint number per project
- Ordering: `['project', '-sprint_number']` - Latest sprints first

### 5.3 Relationships
- **Many-to-One:** Sprint → Project (CASCADE)
- **One-to-Many:** Sprint → UserStories (SET_NULL)

### 5.4 Cascade Behavior
- **CASCADE:** Deleting project deletes sprint
- **SET_NULL:** Deleting sprint sets story.sprint to NULL
- **SET_NULL:** Created_by, updated_by set to NULL if user deleted

### 5.5 Validation
- **Date Validation:** start_date < end_date
- **Overlap Validation:** Sprints cannot overlap (enforced in serializer)
- **Capacity Validation:** Total story points cannot exceed max (if configured)

---

## 6. Relationships Overview

### 6.1 Entity Hierarchy
```
Project
  ├── Epic (One-to-Many)
  │     └── UserStory (One-to-Many)
  │           └── Task (One-to-Many)
  │                 └── Task (One-to-Many, parent_task)
  ├── UserStory (One-to-Many, can also belong to Epic)
  │     └── Task (One-to-Many)
  ├── Sprint (One-to-Many)
  │     └── UserStory (One-to-Many)
  ├── Bug (One-to-Many)
  └── Issue (One-to-Many)
```

### 6.2 User Relationships
- **Project Owner:** Project.owner (ForeignKey, SET_NULL)
- **Project Members:** Project.members (ManyToMany)
- **Epic Owner:** Epic.owner (ForeignKey, SET_NULL)
- **Story Assignee:** UserStory.assigned_to (ForeignKey, SET_NULL)
- **Task Assignee:** Task.assigned_to (ForeignKey, SET_NULL)
- **Bug Reporter:** Bug.reporter (ForeignKey, SET_NULL)
- **Bug Assignee:** Bug.assigned_to (ForeignKey, SET_NULL)
- **Issue Reporter:** Issue.reporter (ForeignKey, SET_NULL)
- **Issue Assignee:** Issue.assigned_to (ForeignKey, SET_NULL)

### 6.3 Cross-Entity Relationships
- **Story Dependencies:** StoryDependency (Many-to-Many via junction table)
- **Story Links:** Linked stories via dependencies
- **Bug Links:** Bug.linked_stories (ManyToMany)
- **Issue Links:** Issue.linked_stories, linked_tasks, linked_bugs (ManyToMany)

---

**End of Document**

**Next Document:** `02_collaboration_entities.md` - Collaboration-related models (Comments, Mentions, Attachments, Dependencies)

