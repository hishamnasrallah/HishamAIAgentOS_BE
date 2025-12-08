# System Settings & Feature Flags User Guide

**Last Updated:** December 2024  
**Feature:** System Settings and Feature Flags Management  
**Access:** Admin Only

---

## 📋 Overview

System Settings and Feature Flags allow administrators to manage system-wide configuration and control feature availability. These tools provide centralized configuration management for the HishamOS platform.

---

## ⚙️ System Settings

### Accessing System Settings

1. Navigate to **Admin** → **System Settings** (or `/admin/settings`)
2. You'll see two tabs:
   - **System Settings** tab (default)
   - **Feature Flags** tab

### Viewing Settings

The System Settings page displays all system settings in a list view. Each setting shows:

- **Key** - Setting identifier (e.g., `max_file_upload_size`)
- **Category Badge** - Category (General, Security, Performance, etc.)
- **Value Type Badge** - Type (String, Integer, Float, Boolean, JSON)
- **Public Badge** - Whether setting is visible to non-admins
- **Description** - What the setting controls
- **Value** - Current setting value (truncated if long)
- **Actions** - Edit and Delete buttons

### Searching Settings

1. Use the **Search box** at the top
2. Search by:
   - Setting key
   - Description
3. Results update in real-time

### Filtering by Category

Use the **Category dropdown** to filter by:
- **All Categories** - Show all settings
- **General** - General system settings
- **Security** - Security-related settings
- **Performance** - Performance tuning settings
- **Notifications** - Notification settings
- **Integrations** - Integration settings

### Creating a Setting

1. Click **"New Setting"** button
2. Fill in the form:

   **Key** (Required)
   - Unique identifier (e.g., `max_file_upload_size`)
   - Use lowercase with underscores
   - Must be unique

   **Category** (Required)
   - Select from dropdown
   - Choose appropriate category

   **Value Type** (Required)
   - **String** - Text value
   - **Integer** - Whole number
   - **Float** - Decimal number
   - **Boolean** - true/false
   - **JSON** - JSON object/array

   **Value** (Required)
   - Enter the setting value
   - Format depends on value type:
     - String: `"Hello World"`
     - Integer: `12345`
     - Float: `123.45`
     - Boolean: `true` or `false`
     - JSON: `{"key": "value"}`

   **Description** (Optional)
   - Explain what this setting does
   - Helpful for other admins

   **Public** (Checkbox)
   - If checked, non-admin users can view this setting
   - If unchecked, only admins can see it

3. Click **"Create Setting"**

### Editing a Setting

1. Click **"Edit"** button on a setting
2. Modify the value or other fields
3. Click **"Update Setting"**

**Note:** The value type cannot be changed after creation.

### Deleting a Setting

1. Click **"Delete"** button on a setting
2. Confirm deletion in the dialog
3. Setting is permanently removed

### Value Types Explained

#### String
- Text values
- Example: `"Welcome Message"`
- Use for: Messages, labels, text content

#### Integer
- Whole numbers
- Example: `10485760` (for max file size in bytes)
- Use for: Counts, sizes, limits

#### Float
- Decimal numbers
- Example: `3.14`
- Use for: Percentages, ratios, measurements

#### Boolean
- true or false
- Example: `true`
- Use for: Enable/disable flags, feature toggles

#### JSON
- JSON objects or arrays
- Example: `{"timeout": 30, "retries": 3}`
- Use for: Complex configurations, nested data

### Getting Settings by Category

1. Use the **"by_category"** endpoint (API)
2. Or filter using the category dropdown in UI
3. Settings are automatically grouped by category

---

## 🚩 Feature Flags

### Accessing Feature Flags

1. Navigate to **Admin** → **System Settings**
2. Click **"Feature Flags"** tab

### Viewing Feature Flags

The Feature Flags page displays all feature flags. Each flag shows:

- **Key** - Flag identifier (e.g., `new_feature_enabled`)
- **Name** - Human-readable name
- **Status Badge** - Enabled/Disabled
- **Description** - What the feature does
- **Access Control** - Roles/users with access
- **Actions** - Toggle, Edit, Delete buttons

### Searching Feature Flags

1. Use the **Search box**
2. Search by:
   - Key
   - Name
   - Description

### Filtering by Status

- **All** - Show all flags
- **Enabled** - Show only enabled flags
- **Disabled** - Show only disabled flags

### Creating a Feature Flag

1. Click **"New Feature Flag"** button
2. Fill in the form:

   **Key** (Required)
   - Unique identifier (e.g., `new_feature_enabled`)
   - Use lowercase with underscores

   **Name** (Required)
   - Human-readable name
   - Example: "New Feature"

   **Description** (Optional)
   - Explain what this feature does

   **Is Enabled** (Checkbox)
   - Check to enable the feature
   - Uncheck to disable

   **Enabled for Roles** (Optional)
   - List of roles that can access this feature
   - Leave empty for all roles
   - Example: `["admin", "manager"]`

   **Enabled for Users** (Optional)
   - List of user IDs that can access this feature
   - Leave empty for all users
   - Example: `["user-id-1", "user-id-2"]`

3. Click **"Create Feature Flag"**

### Toggling a Feature Flag

**Quick Toggle:**
1. Click the **toggle switch** on a feature flag
2. Status changes immediately
3. No confirmation needed

**Via Edit:**
1. Click **"Edit"** button
2. Check/uncheck **"Is Enabled"**
3. Click **"Update Feature Flag"**

### Editing a Feature Flag

1. Click **"Edit"** button
2. Modify:
   - Name
   - Description
   - Enabled status
   - Access control (roles/users)
3. Click **"Update Feature Flag"**

### Deleting a Feature Flag

1. Click **"Delete"** button
2. Confirm deletion
3. Flag is permanently removed

### Access Control

Feature flags support two types of access control:

#### Role-Based Access
- Specify which roles can access the feature
- Example: `["admin", "manager"]`
- Empty array = all roles have access

#### User-Specific Access
- Specify which users can access the feature
- Example: `["user-id-1", "user-id-2"]`
- Empty array = all users have access

**Combined Logic:**
- If both are specified, user must match EITHER:
  - Their role is in `enabled_for_roles`, OR
  - Their user ID is in `enabled_for_users`

### Viewing Active Feature Flags

1. Use the **"Active"** filter
2. Or use the API endpoint: `GET /api/v1/core/feature-flags/active/`
3. Shows only enabled flags

---

## 🎯 Use Cases

### System Settings Use Cases

1. **File Upload Limits**
   - Key: `max_file_upload_size`
   - Type: Integer
   - Value: `10485760` (10MB)

2. **API Rate Limiting**
   - Key: `api_rate_limit_per_minute`
   - Type: Integer
   - Value: `100`

3. **Email Configuration**
   - Key: `email_from_address`
   - Type: String
   - Value: `"noreply@hishamos.com"`

4. **Feature Configuration**
   - Key: `enable_two_factor_auth`
   - Type: Boolean
   - Value: `true`

5. **Complex Configuration**
   - Key: `cache_settings`
   - Type: JSON
   - Value: `{"timeout": 300, "max_size": 1000}`

### Feature Flags Use Cases

1. **Gradual Rollout**
   - Enable feature for admins first
   - Then enable for managers
   - Finally enable for all users

2. **A/B Testing**
   - Create two flags for different versions
   - Enable for different user groups
   - Compare results

3. **Emergency Disable**
   - Quickly disable problematic features
   - No code deployment needed
   - Instant effect

4. **Beta Features**
   - Enable for specific beta testers
   - Use user-specific access control
   - Gather feedback before full release

---

## 🔐 Permissions

### System Settings

- **View:** All authenticated users (public settings only for non-admins)
- **Create/Edit/Delete:** Admin only

### Feature Flags

- **View:** All authenticated users
- **Create/Edit/Delete/Toggle:** Admin only

---

## 📝 Best Practices

### For System Settings

1. **Use Descriptive Keys**
   - Good: `max_file_upload_size`
   - Bad: `upload1`

2. **Provide Descriptions**
   - Help other admins understand the setting
   - Document expected values

3. **Choose Appropriate Categories**
   - Group related settings together
   - Makes management easier

4. **Use Correct Value Types**
   - Don't use string for numbers
   - Use JSON for complex data

5. **Mark Public Settings Carefully**
   - Only mark truly public settings
   - Security settings should be private

### For Feature Flags

1. **Use Clear Names**
   - Good: "New Dashboard Feature"
   - Bad: "Feature 1"

2. **Document Features**
   - Describe what the feature does
   - Note any dependencies

3. **Plan Rollout Strategy**
   - Start with admins
   - Gradually expand access
   - Monitor for issues

4. **Clean Up Old Flags**
   - Delete flags for removed features
   - Keep only active flags

5. **Use Access Control Wisely**
   - Test with small groups first
   - Use role-based for broad access
   - Use user-specific for targeted testing

---

## 🔗 Related Documentation

- [System Settings API Reference](../API_REFERENCE.md#system-settings-api)
- [Feature Flags API Reference](../API_REFERENCE.md#feature-flags-api)
- [Admin Guide](../ADMIN_GUIDE.md)
- [System Settings Testing Checklist](../../03_TESTING/MANUAL_TEST_CHECKLISTS/SYSTEM_SETTINGS_UI_MANUAL_TESTING_CHECKLIST.md)

---

**Last Updated:** December 2024  
**Maintained by:** Development Team

