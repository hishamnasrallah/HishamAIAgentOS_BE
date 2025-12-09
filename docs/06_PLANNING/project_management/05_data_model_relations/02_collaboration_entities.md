# Data Model Relations - Collaboration Entities

**Document Type:** Business Requirements Document (BRD)  
**Version:** 1.0.0  
**Created By:** BA Agent  
**Created Date:** December 9, 2024  
**Last Updated:** December 9, 2024  
**Last Updated By:** BA Agent  
**Status:** Active  
**Dependencies:** `01_overview_and_scope.md`, `05_data_model_relations/01_core_entities.md`  
**Related Features:** Collaboration features

---

## 📋 Table of Contents

1. [Mention Model](#mention-model)
2. [StoryComment Model](#storycomment-model)
3. [StoryDependency Model](#storydependency-model)
4. [StoryAttachment Model](#storyattachment-model)
5. [Notification Model](#notification-model)
6. [Watcher Model](#watcher-model)
7. [Activity Model](#activity-model)
8. [EditHistory Model](#edithistory-model)

---

## 1. Mention Model

### 1.1 Fields
```python
id: UUID (primary key, auto-generated)
mention_text: CharField(max_length=200)  # e.g., '@john.doe'
mentioned_user: ForeignKey(User, CASCADE, related_name='mentions')
story: ForeignKey(UserStory, CASCADE, null=True, blank=True, related_name='mentions')
comment: ForeignKey(StoryComment, CASCADE, null=True, blank=True, related_name='mentions')
read: BooleanField(default=False)
notified: BooleanField(default=False)
read_at: DateTimeField(null=True, blank=True)
created_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='created_mentions')
created_at: DateTimeField(auto_now_add=True, db_index=True)
```

### 1.2 Indexes
- `['mentioned_user', 'read']` - For filtering unread mentions
- `['story']` - For filtering mentions by story
- `['created_at']` - For sorting mentions

### 1.3 Relationships
- **Many-to-One:** Mention → MentionedUser (CASCADE)
- **Many-to-One:** Mention → Story (CASCADE, nullable)
- **Many-to-One:** Mention → Comment (CASCADE, nullable)
- **Many-to-One:** Mention → CreatedBy (SET_NULL)

### 1.4 Cascade Behavior
- **CASCADE:** Deleting story deletes mentions
- **CASCADE:** Deleting comment deletes mentions
- **CASCADE:** Deleting user deletes mentions

---

## 2. StoryComment Model

### 2.1 Fields
```python
id: UUID (primary key, auto-generated)
story: ForeignKey(UserStory, CASCADE, related_name='comments')
parent: ForeignKey('self', CASCADE, null=True, blank=True, related_name='replies')
author: ForeignKey(User, CASCADE, related_name='story_comments')
content: TextField()
reactions: JSONField(default=dict)  # e.g., {'👍': ['user_id1', 'user_id2']}
deleted: BooleanField(default=False)
deleted_at: DateTimeField(null=True, blank=True)
deleted_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='deleted_story_comments')
created_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='created_story_comments')
updated_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='updated_story_comments')
created_at: DateTimeField(auto_now_add=True, db_index=True)
updated_at: DateTimeField(auto_now=True, db_index=True)
```

### 2.2 Indexes
- `['story', 'created_at']` - For filtering comments by story
- `['parent']` - For filtering replies

### 2.3 Relationships
- **Many-to-One:** Comment → Story (CASCADE)
- **Many-to-One:** Comment → Parent (CASCADE, self-referential, nullable)
- **Many-to-One:** Comment → Author (CASCADE)
- **One-to-Many:** Comment → Replies (CASCADE)
- **One-to-Many:** Comment → Mentions (CASCADE)

### 2.4 Cascade Behavior
- **CASCADE:** Deleting story deletes all comments
- **CASCADE:** Deleting parent comment deletes replies
- **CASCADE:** Deleting author deletes comments
- **Soft Delete:** Comments marked as deleted, not actually deleted

---

## 3. StoryDependency Model

### 3.1 Fields
```python
id: UUID (primary key, auto-generated)
source_story: ForeignKey(UserStory, CASCADE, related_name='outgoing_dependencies')
target_story: ForeignKey(UserStory, CASCADE, related_name='incoming_dependencies')
dependency_type: CharField(max_length=20, choices=DEPENDENCY_TYPE_CHOICES, default='blocks')
description: TextField(blank=True)
resolved: BooleanField(default=False)
resolved_at: DateTimeField(null=True, blank=True)
resolved_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='resolved_dependencies')
created_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='created_story_dependencies')
updated_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='updated_story_dependencies')
created_at: DateTimeField(auto_now_add=True, db_index=True)
updated_at: DateTimeField(auto_now=True, db_index=True)
```

### 3.2 Indexes
- `['source_story', 'dependency_type']` - For filtering dependencies by source
- `['target_story', 'dependency_type']` - For filtering dependencies by target
- `['resolved']` - For filtering unresolved dependencies

### 3.3 Relationships
- **Many-to-One:** Dependency → SourceStory (CASCADE)
- **Many-to-One:** Dependency → TargetStory (CASCADE)
- **Many-to-One:** Dependency → ResolvedBy (SET_NULL)

### 3.4 Cascade Behavior
- **CASCADE:** Deleting source story deletes dependency
- **CASCADE:** Deleting target story deletes dependency
- **Unique Constraint:** `['source_story', 'target_story', 'dependency_type']` - Prevents duplicate dependencies

### 3.5 Dependency Types
- `blocks` - Source story blocks target story
- `blocked_by` - Source story is blocked by target story
- `relates_to` - Source story relates to target story
- `duplicates` - Source story duplicates target story
- `depends_on` - Source story depends on target story

---

## 4. StoryAttachment Model

### 4.1 Fields
```python
id: UUID (primary key, auto-generated)
story: ForeignKey(UserStory, CASCADE, related_name='attachments')
file: FileField(upload_to='story_attachments/%Y/%m/%d/')
file_name: CharField(max_length=255)
file_size: BigIntegerField()
file_type: CharField(max_length=100)  # MIME type
description: TextField(blank=True)
uploaded_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='uploaded_attachments')
created_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='created_story_attachments')
updated_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='updated_story_attachments')
created_at: DateTimeField(auto_now_add=True, db_index=True)
updated_at: DateTimeField(auto_now=True, db_index=True)
```

### 4.2 Indexes
- `['story', 'created_at']` - For filtering attachments by story

### 4.3 Relationships
- **Many-to-One:** Attachment → Story (CASCADE)
- **Many-to-One:** Attachment → UploadedBy (SET_NULL)

### 4.4 Cascade Behavior
- **CASCADE:** Deleting story deletes all attachments
- **CASCADE:** Deleting attachment deletes file from storage

---

## 5. Notification Model

### 5.1 Fields
```python
id: UUID (primary key, auto-generated)
recipient: ForeignKey(User, CASCADE, related_name='notifications')
notification_type: CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
title: CharField(max_length=255)
message: TextField()
metadata: JSONField(default=dict)  # Additional notification data
is_read: BooleanField(default=False, db_index=True)
read_at: DateTimeField(null=True, blank=True)
email_sent: BooleanField(default=False)
email_sent_at: DateTimeField(null=True, blank=True)
project: ForeignKey(Project, CASCADE, null=True, blank=True, related_name='notifications')
story: ForeignKey(UserStory, CASCADE, null=True, blank=True, related_name='notifications')
comment: ForeignKey(StoryComment, CASCADE, null=True, blank=True, related_name='notifications')
mention: ForeignKey(Mention, CASCADE, null=True, blank=True, related_name='notifications')
created_by: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='created_notifications')
created_at: DateTimeField(auto_now_add=True, db_index=True)
```

### 5.2 Indexes
- `['recipient', 'is_read', '-created_at']` - For filtering unread notifications
- `['recipient', '-created_at']` - For sorting notifications
- `['notification_type', '-created_at']` - For filtering by type

### 5.3 Relationships
- **Many-to-One:** Notification → Recipient (CASCADE)
- **Many-to-One:** Notification → Project (CASCADE, nullable)
- **Many-to-One:** Notification → Story (CASCADE, nullable)
- **Many-to-One:** Notification → Comment (CASCADE, nullable)
- **Many-to-One:** Notification → Mention (CASCADE, nullable)

### 5.4 Cascade Behavior
- **CASCADE:** Deleting recipient deletes notifications
- **CASCADE:** Deleting project deletes notifications
- **CASCADE:** Deleting story deletes notifications
- **CASCADE:** Deleting comment deletes notifications
- **CASCADE:** Deleting mention deletes notifications

### 5.5 Notification Types
- `mention` - User mentioned
- `comment` - Comment added
- `status_change` - Status changed
- `assignment` - Assigned to work item
- `story_created` - Story created
- `story_updated` - Story updated
- `dependency_added` - Dependency added
- `dependency_resolved` - Dependency resolved
- `attachment_added` - Attachment added
- `due_date_approaching` - Due date approaching
- `sprint_start` - Sprint started
- `sprint_end` - Sprint ended
- `automation_triggered` - Automation triggered

---

## 6. Watcher Model

### 6.1 Fields
```python
id: UUID (primary key, auto-generated)
user: ForeignKey(User, CASCADE, related_name='watchers')
content_type: ForeignKey(ContentType, CASCADE)
object_id: UUIDField(db_index=True)
content_object: GenericForeignKey('content_type', 'object_id')
created_at: DateTimeField(auto_now_add=True)
```

### 6.2 Indexes
- `['content_type', 'object_id']` - For filtering watchers by object
- `['user', 'created_at']` - For sorting watchers

### 6.3 Relationships
- **Many-to-One:** Watcher → User (CASCADE)
- **Generic Foreign Key:** Watcher → ContentObject (any model)

### 6.4 Cascade Behavior
- **CASCADE:** Deleting user deletes watchers
- **CASCADE:** Deleting content object deletes watchers
- **Unique Constraint:** `['user', 'content_type', 'object_id']` - Prevents duplicate watchers

---

## 7. Activity Model

### 7.1 Fields
```python
id: UUID (primary key, auto-generated)
activity_type: CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES, db_index=True)
user: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='activities')
project: ForeignKey(Project, CASCADE, null=True, blank=True, db_index=True, related_name='activities')
content_type: ForeignKey(ContentType, CASCADE, null=True, blank=True)
object_id: UUIDField(db_index=True, null=True, blank=True)
content_object: GenericForeignKey('content_type', 'object_id')
description: TextField()
metadata: JSONField(default=dict)  # Additional activity data
created_at: DateTimeField(auto_now_add=True, db_index=True)
```

### 7.2 Indexes
- `['project', '-created_at']` - For filtering activities by project
- `['activity_type', '-created_at']` - For filtering by type
- `['user', '-created_at']` - For filtering by user
- `['content_type', 'object_id', '-created_at']` - For filtering by object
- `['-created_at']` - For sorting activities

### 7.3 Relationships
- **Many-to-One:** Activity → User (SET_NULL)
- **Many-to-One:** Activity → Project (CASCADE, nullable)
- **Generic Foreign Key:** Activity → ContentObject (any model)

### 7.4 Cascade Behavior
- **CASCADE:** Deleting project deletes activities
- **SET_NULL:** Deleting user sets user to NULL
- **CASCADE:** Deleting content object may delete activities (depends on model)

### 7.5 Activity Types
- Story activities: created, updated, deleted, status_changed, priority_changed, assigned, unassigned, moved_to_sprint, removed_from_sprint, story_points_changed
- Task activities: created, updated, deleted, status_changed, priority_changed, assigned, unassigned, progress_updated
- Bug activities: created, updated, deleted, status_changed, severity_changed, resolved, closed, reopened
- Issue activities: created, updated, deleted, status_changed, resolved, closed
- Epic activities: created, updated, deleted, status_changed
- Sprint activities: created, updated, deleted, started, completed
- Project activities: created, updated, deleted, status_changed, member_added, member_removed
- Comment activities: added, updated, deleted
- Dependency activities: added, removed, resolved
- Attachment activities: added, deleted
- Time log activities: logged, updated, deleted
- Watcher activities: added, removed
- Tag/Label activities: added, removed

---

## 8. EditHistory Model

### 8.1 Fields
```python
id: UUID (primary key, auto-generated)
user: ForeignKey(User, SET_NULL, null=True, blank=True, related_name='edit_histories')
project: ForeignKey(Project, CASCADE, null=True, blank=True, db_index=True, related_name='edit_histories')
content_type: ForeignKey(ContentType, CASCADE, null=True, blank=True)
object_id: UUIDField(db_index=True, null=True, blank=True)
content_object: GenericForeignKey('content_type', 'object_id')
version: IntegerField(default=1, db_index=True)
old_values: JSONField(default=dict)  # Field values before edit
new_values: JSONField(default=dict)  # Field values after edit
changed_fields: JSONField(default=list)  # List of changed field names
diffs: JSONField(default=dict)  # Computed diffs for text fields
comment: TextField(blank=True)  # Optional edit comment
created_at: DateTimeField(auto_now_add=True, db_index=True)
```

### 8.2 Indexes
- `['content_type', 'object_id', '-version']` - For filtering history by object and version
- `['content_type', 'object_id', '-created_at']` - For sorting history by date
- `['project', '-created_at']` - For filtering by project
- `['user', '-created_at']` - For filtering by user
- `['-created_at']` - For sorting history

### 8.3 Relationships
- **Many-to-One:** EditHistory → User (SET_NULL)
- **Many-to-One:** EditHistory → Project (CASCADE, nullable)
- **Generic Foreign Key:** EditHistory → ContentObject (any model)

### 8.4 Cascade Behavior
- **CASCADE:** Deleting project deletes edit histories
- **SET_NULL:** Deleting user sets user to NULL
- **CASCADE:** Deleting content object may delete edit histories (depends on model)

### 8.5 Unique Constraint
- `['content_type', 'object_id', 'version']` - Ensures unique version numbers per object

---

## 9. Relationships Overview

### 9.1 Collaboration Entity Relationships
```
UserStory
  ├── Mentions (One-to-Many)
  ├── Comments (One-to-Many)
  │     └── Mentions (One-to-Many)
  ├── Dependencies (One-to-Many, outgoing)
  ├── Dependencies (One-to-Many, incoming)
  ├── Attachments (One-to-Many)
  ├── Notifications (One-to-Many)
  └── Watchers (One-to-Many, via GenericForeignKey)

User
  ├── Mentions (One-to-Many, as mentioned_user)
  ├── Comments (One-to-Many, as author)
  ├── Notifications (One-to-Many, as recipient)
  └── Watchers (One-to-Many)
```

### 9.2 Cross-Entity Relationships
- **Mentions → Notifications:** Mentions trigger notifications
- **Comments → Notifications:** Comments trigger notifications
- **Dependencies → Notifications:** Dependencies trigger notifications
- **Attachments → Notifications:** Attachments trigger notifications
- **Status Changes → Notifications:** Status changes trigger notifications
- **All Changes → Activities:** All changes create activity entries
- **All Edits → EditHistory:** All edits create edit history entries

---

**End of Document**

**Next Document:** `03_configuration_entities.md` - Configuration and tracking entities

