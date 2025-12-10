# Test Checklist: UI Features

**Category:** UI Features  
**Features:** Rich Text Editor, Code Blocks, Embedded Media, Story Preview, Keyboard Shortcuts, Dark Mode, Theme Management  
**Estimated Tests:** ~60  
**Priority:** LOW

---

## 1. RICH TEXT EDITOR

### 1.1 Rich Text Editing

**TC-UI-001: Rich Text Editor Display**
- [ ] **Test Case:** Display rich text editor
- [ ] **Page:** Story form or comment form
- [ ] **Steps:**
  1. Open form with rich text editor
  2. Verify editor loads
- [ ] **Expected Result:** 
  - Editor displays correctly
  - Toolbar visible
  - Content area editable
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-002: Rich Text Toolbar**
- [ ] **Test Case:** Use formatting toolbar
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Select text
  2. Click bold button
  3. Click italic button
  4. Click underline button
- [ ] **Expected Result:** 
  - Formatting applied
  - Text styled correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-003: Rich Text Headings**
- [ ] **Test Case:** Add headings
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Click heading button (H1, H2, H3)
  2. Type heading text
- [ ] **Expected Result:** 
  - Heading format applied
  - Text styled as heading
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-004: Rich Text Lists**
- [ ] **Test Case:** Create lists
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Click bullet list button
  2. Type list items
  3. Click numbered list button
- [ ] **Expected Result:** 
  - Lists created correctly
  - Indentation works
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-005: Rich Text Links**
- [ ] **Test Case:** Add links
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Select text
  2. Click link button
  3. Enter URL
- [ ] **Expected Result:** 
  - Link created
  - Text clickable
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-006: Rich Text Images**
- [ ] **Test Case:** Insert images
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Click image button
  2. Enter image URL
- [ ] **Expected Result:** 
  - Image inserted
  - Image displays in editor
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-007: Rich Text Markdown Support**
- [ ] **Test Case:** Paste markdown content
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Paste markdown text
  2. Verify formatting applied
- [ ] **Expected Result:** 
  - Markdown parsed
  - Formatting applied
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-008: Rich Text Keyboard Shortcuts**
- [ ] **Test Case:** Use keyboard shortcuts
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Select text
  2. Press Ctrl+B (bold)
  3. Press Ctrl+I (italic)
  4. Press Ctrl+U (underline)
- [ ] **Expected Result:** 
  - Shortcuts work
  - Formatting applied
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-009: Rich Text Save**
- [ ] **Test Case:** Save rich text content
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Enter formatted text
  2. Save story
  3. View saved story
- [ ] **Expected Result:** 
  - Content saved with formatting
  - Formatting preserved on display
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. CODE BLOCKS

### 2.1 Code Display

**TC-UI-010: Code Block Display**
- [ ] **Test Case:** Display code block
- [ ] **Page:** Story preview
- [ ] **Steps:**
  1. View story with code block
  2. Verify code displayed
- [ ] **Expected Result:** 
  - Code block renders
  - Syntax highlighting applied
  - Line numbers shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-011: Code Block Copy**
- [ ] **Test Case:** Copy code from block
- [ ] **Page:** Story preview
- [ ] **Steps:**
  1. Click copy button on code block
  2. Paste elsewhere
- [ ] **Expected Result:** 
  - Code copied to clipboard
  - Paste works correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-012: Code Block Download**
- [ ] **Test Case:** Download code block
- [ ] **Page:** Story preview
- [ ] **Steps:**
  1. Click download button
  2. Verify file downloads
- [ ] **Expected Result:** 
  - File downloads
  - Filename correct
  - Content correct
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-013: Inline Code**
- [ ] **Test Case:** Display inline code
- [ ] **Page:** Story preview
- [ ] **Expected Result:** 
  - Inline code styled correctly
  - Monospace font
  - Background color
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-014: Code Block Editor**
- [ ] **Test Case:** Edit code block
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Insert code block
  2. Enter code
  3. Select language
- [ ] **Expected Result:** 
  - Code editor works
  - Language selection works
  - Code saved correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. EMBEDDED MEDIA

### 3.1 Media Display

**TC-UI-015: Image Embedding**
- [ ] **Test Case:** Display embedded image
- [ ] **Page:** Story preview
- [ ] **Steps:**
  1. View story with embedded image
  2. Verify image displays
- [ ] **Expected Result:** 
  - Image renders
  - Image clickable for preview
  - Alt text shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-016: Video Embedding**
- [ ] **Test Case:** Display embedded video
- [ ] **Page:** Story preview
- [ ] **Steps:**
  1. View story with video URL
  2. Verify video embedded
- [ ] **Expected Result:** 
  - Video player embedded
  - YouTube/Vimeo videos work
  - Video controls available
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-017: Iframe Embedding**
- [ ] **Test Case:** Display embedded iframe
- [ ] **Page:** Story preview
- [ ] **Steps:**
  1. View story with iframe
  2. Verify iframe displays
- [ ] **Expected Result:** 
  - Iframe renders
  - Content loads
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-018: Media Embedder Component**
- [ ] **Test Case:** Add media via embedder
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Click "Embed Media"
  2. Enter media URL
  3. Select type
  4. Submit
- [ ] **Expected Result:** 
  - Media embedded
  - Preview shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-019: Media Error Handling**
- [ ] **Test Case:** Handle media load errors
- [ ] **Page:** Story preview
- [ ] **Steps:**
  1. View story with invalid media URL
- [ ] **Expected Result:** 
  - Error message shown
  - Fallback display
  - Link to open in new tab
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. STORY PREVIEW

### 4.1 Preview Display

**TC-UI-020: Story Preview Component**
- [ ] **Test Case:** Display story preview
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Open story
  2. View preview section
- [ ] **Expected Result:** 
  - Preview displays
  - Description rendered
  - Acceptance criteria rendered
  - Code blocks, images, etc. rendered
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-021: Markdown Rendering**
- [ ] **Test Case:** Render markdown content
- [ ] **Page:** Story preview
- [ ] **Steps:**
  1. View story with markdown description
- [ ] **Expected Result:** 
  - Markdown parsed correctly
  - Formatting applied
  - Links clickable
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-022: HTML Rendering**
- [ ] **Test Case:** Render HTML content
- [ ] **Page:** Story preview
- [ ] **Steps:**
  1. View story with HTML description
- [ ] **Expected Result:** 
  - HTML rendered
  - XSS protection applied
  - Formatting preserved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. KEYBOARD SHORTCUTS

### 5.1 Global Shortcuts

**TC-UI-023: Global Search Shortcut**
- [ ] **Test Case:** Open search with Ctrl+K
- [ ] **Page:** Any page
- [ ] **Steps:**
  1. Press Ctrl+K (or Cmd+K on Mac)
- [ ] **Expected Result:** 
  - Global search opens
  - Focus on search input
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-024: Keyboard Shortcuts Help**
- [ ] **Test Case:** Show shortcuts help
- [ ] **Page:** Any page
- [ ] **Steps:**
  1. Press "?" key
- [ ] **Expected Result:** 
  - Shortcuts panel opens
  - All shortcuts listed
  - Grouped by category
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-025: Navigation Shortcuts**
- [ ] **Test Case:** Use navigation shortcuts
- [ ] **Page:** Any page
- [ ] **Steps:**
  1. Press Ctrl+H (dashboard)
  2. Press Ctrl+P (projects)
  3. Press Ctrl+A (agents)
- [ ] **Expected Result:** 
  - Navigation works
  - Pages load correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-026: Story Editing Shortcuts**
- [ ] **Test Case:** Use story editing shortcuts
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Press Ctrl+N (new story)
  2. Press Ctrl+S (save)
  3. Press Escape (close)
- [ ] **Expected Result:** 
  - Shortcuts work
  - Actions execute
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-027: Keyboard Shortcuts Panel**
- [ ] **Test Case:** View shortcuts panel
- [ ] **Page:** Any page
- [ ] **Steps:**
  1. Open shortcuts panel
  2. Browse shortcuts
- [ ] **Expected Result:** 
  - Panel displays
  - Shortcuts organized
  - Searchable
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 6. DARK MODE

### 6.1 Theme Management

**TC-UI-028: Toggle Dark Mode**
- [ ] **Test Case:** Switch to dark mode
- [ ] **Page:** Any page
- [ ] **Steps:**
  1. Click theme toggle
  2. Select "Dark"
- [ ] **Expected Result:** 
  - Theme changes to dark
  - All pages use dark theme
  - Preference saved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-029: Toggle Light Mode**
- [ ] **Test Case:** Switch to light mode
- [ ] **Page:** Any page
- [ ] **Steps:**
  1. Click theme toggle
  2. Select "Light"
- [ ] **Expected Result:** 
  - Theme changes to light
  - All pages use light theme
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-030: System Theme Detection**
- [ ] **Test Case:** Use system theme
- [ ] **Page:** Any page
- [ ] **Steps:**
  1. Click theme toggle
  2. Select "System"
  3. Change system theme
- [ ] **Expected Result:** 
  - Theme follows system preference
  - Updates when system theme changes
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-031: Theme Persistence**
- [ ] **Test Case:** Theme preference saved
- [ ] **Page:** Any page
- [ ] **Steps:**
  1. Set theme
  2. Refresh page
  3. Navigate to different page
- [ ] **Expected Result:** 
  - Theme persists
  - Applied on all pages
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-032: Dark Mode Board**
- [ ] **Test Case:** Board displays correctly in dark mode
- [ ] **Page:** Board page
- [ ] **Steps:**
  1. Switch to dark mode
  2. View board
- [ ] **Expected Result:** 
  - Board styled for dark mode
  - Cards readable
  - Colors appropriate
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-033: Theme Toggle Component**
- [ ] **Test Case:** Theme toggle button works
- [ ] **Page:** Any page (header)
- [ ] **Steps:**
  1. Click theme toggle
  2. Select theme
- [ ] **Expected Result:** 
  - Toggle works
  - Theme changes immediately
  - Icon updates
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 7. COLLABORATIVE EDITING

### 7.1 Real-time Collaboration

**TC-UI-034: Collaborative Editing Session**
- [ ] **Test Case:** Multiple users edit same story
- [ ] **Page:** Story edit modal
- [ ] **Steps:**
  1. User A opens story for editing
  2. User B opens same story
  3. Both users edit
- [ ] **Expected Result:** 
  - Both users see each other's edits
  - Cursor positions shown
  - Conflicts resolved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-035: Current Editors Display**
- [ ] **Test Case:** Show who is editing
- [ ] **Page:** Story edit modal
- [ ] **Expected Result:** 
  - Current editors shown
  - Avatars/names displayed
  - Updates in real-time
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-UI-036: Cursor Position Sharing**
- [ ] **Test Case:** Show other users' cursors
- [ ] **Page:** Story edit modal
- [ ] **Expected Result:** 
  - Other users' cursors visible
  - Color-coded by user
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - UI Features  
**Total Test Cases:** ~60  
**Next File:** [11_test_checklist_advanced_features.md](./11_test_checklist_advanced_features.md)

