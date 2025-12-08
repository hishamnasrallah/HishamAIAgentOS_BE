# Command Library User Guide

**Last Updated:** December 2024  
**Feature:** Command Library - Browse, Execute, and Create AI-Powered Commands

---

## 📋 Overview

The Command Library is a comprehensive collection of AI-powered commands that automate various tasks across software development, project management, documentation, and more. You can browse, execute, and create commands to streamline your workflow.

---

## 🚀 Getting Started

### Accessing the Command Library

1. Navigate to **Commands** in the main navigation menu
2. You'll see the Command Library page with:
   - Popular Commands section
   - Search and filter options
   - All available commands

---

## 🔍 Browsing Commands

### Viewing All Commands

The Command Library displays all available commands in a grid layout. Each command card shows:

- **Command Name** - The name of the command
- **Category Badge** - Which category it belongs to (e.g., Code Generation, Testing)
- **Description** - Brief description of what the command does
- **Tags** - Relevant tags for searching
- **Success Rate** - Percentage of successful executions
- **Usage Count** - How many times it's been used
- **Recommended Agent** - Best agent to use with this command

### Popular Commands

At the top of the page, you'll see a **Popular Commands** section showing:
- Top 6 most-used commands
- Commands with highest success rates
- Quick access to frequently used commands

Click any popular command to view its details.

### Searching Commands

1. Use the **Search box** at the top
2. Type keywords to search by:
   - Command name
   - Description
   - Tags
3. Results update in real-time as you type
4. Click the **X** icon to clear search

### Filtering by Category

1. Click category buttons below the search box:
   - **All Categories** - Shows all commands
   - **Requirements Engineering** 📋
   - **Code Generation** 💻
   - **Code Review** 🔍
   - **Testing & QA** ✅
   - **DevOps & Deployment** 🚀
   - **Documentation** 📚
   - **Project Management** 📊
   - **Design & Architecture** 🏗️
   - **Legal & Compliance** ⚖️
   - **Business Analysis** 💼
   - **UX/UI Design** 🎨
   - **Research & Analysis** 🔬

2. The active category is highlighted
3. Commands filter automatically when you select a category

---

## 📖 Viewing Command Details

### Opening a Command

1. Click any command card from the list
2. The command detail page shows:
   - Full description
   - All parameters with descriptions
   - Example usage
   - Template preview
   - Execution history (if any)

### Command Information

Each command detail page includes:

- **Name & Description** - What the command does
- **Category** - Which category it belongs to
- **Parameters** - Required and optional parameters
  - Parameter name
  - Type (string, integer, text, etc.)
  - Required/Optional indicator
  - Description
  - Example values
- **Recommended Agent** - Best agent to use
- **Tags** - Searchable tags
- **Usage Statistics** - Success rate, usage count, estimated cost

---

## ▶️ Executing Commands

### Step 1: Select a Command

1. Browse or search for the command you want
2. Click on the command card to open details
3. Click **"Execute"** button (or navigate to `/commands/{id}/execute`)

### Step 2: Fill in Parameters

1. Review the **Required Parameters** section:
   - Required parameters are marked with a red badge
   - Fill in all required fields
   
2. Review the **Optional Parameters** section:
   - Optional parameters can be left empty
   - Fill them in if needed for better results

3. Parameter types:
   - **Text** - Single line text input
   - **Long Text** - Multi-line textarea
   - **Integer** - Number input
   - **Float** - Decimal number input
   - **Dropdown** - Select from allowed values

### Step 3: Preview (Optional)

1. Click **"Preview"** button to see the rendered template
2. Review the preview to ensure parameters are correct
3. Check for any validation errors
4. Fix any errors before executing

### Step 4: Execute

1. Click **"Execute Command"** button
2. Wait for execution (may take a few seconds to minutes)
3. View results:
   - **Success/Error Status** - Whether execution succeeded
   - **Output** - The generated result
   - **Execution Time** - How long it took
   - **Cost** - Estimated cost in USD
   - **Tokens Used** - Number of tokens consumed
   - **Agent Used** - Which agent executed the command

### Execution Results

**Success Response:**
- Green success indicator
- Full output displayed
- Execution metrics shown
- Option to copy output

**Error Response:**
- Red error indicator
- Error message displayed
- Suggestions for fixing the issue
- Option to retry

---

## ➕ Creating New Commands (Admin Only)

### Accessing Command Creation

1. Navigate to **Commands** page
2. Click **"Create New Command"** button (admin only)
3. Or go to `/commands/new`

### Step 1: Basic Information

Fill in:
- **Name** - Command name (e.g., "Generate API Documentation")
- **Slug** - URL-friendly identifier (auto-generated from name)
- **Description** - What the command does
- **Category** - Select from dropdown
- **Tags** - Add relevant tags (comma-separated)

### Step 2: Template

Create the command template using placeholders:

```
Generate API documentation for {{project_name}}.

Project Details:
- Framework: {{framework}}
- Language: {{language}}
- API Version: {{api_version}}

Include:
- Endpoint descriptions
- Request/response examples
- Authentication requirements
```

**Placeholder Syntax:**
- Use `{{parameter_name}}` for parameters
- Parameters will be replaced with actual values during execution

### Step 3: Parameters

Define parameters that users will fill in:

For each parameter, specify:
- **Name** - Parameter identifier (used in template)
- **Type** - string, integer, float, text, boolean, etc.
- **Required** - Whether parameter is mandatory
- **Description** - What this parameter is for
- **Example** - Example value
- **Allowed Values** - (Optional) Restrict to specific values

**Example Parameters:**
```json
[
  {
    "name": "project_name",
    "type": "string",
    "required": true,
    "description": "Name of the project",
    "example": "E-commerce Platform"
  },
  {
    "name": "framework",
    "type": "string",
    "required": false,
    "description": "Framework used",
    "example": "Django",
    "allowed_values": ["Django", "Flask", "FastAPI"]
  }
]
```

### Step 4: Agent Integration

- **Recommended Agent** - Select the best agent for this command
- **Required Capabilities** - Select capabilities needed (e.g., CODE_GENERATION, DOCUMENTATION)

### Step 5: Metadata

- **Version** - Command version (default: 1.0.0)
- **Estimated Cost** - Expected cost per execution
- **Estimated Duration** - Expected execution time in seconds
- **Is Active** - Enable/disable the command

### Step 6: Save

1. Click **"Create Command"** button
2. Command is created and immediately available
3. You'll be redirected to the command detail page

---

## 🎯 Tips & Best Practices

### For Browsing

- Use **search** to quickly find commands
- Filter by **category** to narrow down options
- Check **popular commands** for commonly used ones
- Review **success rates** to find reliable commands

### For Executing

- **Preview first** - Always preview before executing to catch errors
- **Fill required fields** - Ensure all required parameters are provided
- **Use examples** - Check parameter examples for format guidance
- **Be patient** - Some commands may take time to execute
- **Review output** - Check the generated output for quality

### For Creating Commands

- **Clear descriptions** - Write clear, concise descriptions
- **Good templates** - Create detailed templates with context
- **Parameter validation** - Use allowed values for dropdowns
- **Test thoroughly** - Test commands before making them active
- **Version control** - Update version when making changes

---

## 🔗 Related Features

### Command Categories

Commands are organized into 12 categories:

1. **Requirements Engineering** - User stories, requirements analysis
2. **Code Generation** - Generate code in various languages
3. **Code Review** - Code quality analysis and reviews
4. **Testing & QA** - Test generation and quality assurance
5. **DevOps & Deployment** - CI/CD, infrastructure, deployment
6. **Documentation** - API docs, user guides, technical docs
7. **Project Management** - Sprint planning, task breakdown
8. **Design & Architecture** - System design, architecture decisions
9. **Legal & Compliance** - Policies, contracts, compliance
10. **Business Analysis** - Market research, ROI analysis
11. **UX/UI Design** - User experience, interface design
12. **Research & Analysis** - Technology research, competitive analysis

### Integration with Agents

- Commands can be linked to **recommended agents**
- Agents execute commands using their AI capabilities
- Each command specifies **required capabilities**
- System automatically selects the best agent if not specified

### Execution Tracking

- All command executions are tracked
- View execution history
- Monitor success rates
- Track costs and token usage

---

## ❓ Troubleshooting

### Command Not Found

- Check if command is active
- Verify you have access permissions
- Try refreshing the page

### Execution Failed

- Check error message for details
- Verify all required parameters are filled
- Ensure parameter values are in correct format
- Try previewing first to catch validation errors

### Slow Execution

- Some commands take longer (especially code generation)
- Check execution timeout (4 minutes max)
- Large outputs may take more time
- Check system status if consistently slow

### Can't Create Command

- Verify you have admin permissions
- Check that all required fields are filled
- Ensure template syntax is correct
- Verify parameter definitions are valid

---

## 📚 Related Documentation

- [Command Library API Reference](../API_REFERENCE.md#commands-api)
- [Command Testing Guide](../../08_COMMANDS/COMMAND_TESTING_GUIDE.md)
- [Command Library Documentation](../../08_COMMANDS/COMMAND_LIBRARY_DOCUMENTATION.md)

---

**Last Updated:** December 2024  
**Maintained by:** Development Team

