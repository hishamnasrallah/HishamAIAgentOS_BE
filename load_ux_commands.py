"""
Load UI/UX Design Commands for Phase 9 Frontend Development

These commands will be used during Phase 9 to design and build the React frontend.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.commands.models import CommandCategory, CommandTemplate
from apps.agents.models import Agent

# UI/UX Design Commands
UX_COMMANDS = [
    {
        'name': 'Create Design System',
        'slug': 'create-design-system',
        'description': 'Generate a comprehensive design system with colors, typography, spacing, and components',
        'template': '''Create a design system for: {{app_name}}

Brand: {{brand_identity}}
Target Users: {{target_users}}

Generate:
1. **Color Palette**
   - Primary, secondary, accent colors
   - Neutral grays
   - Semantic colors (success, warning, error, info)
   - Dark mode variants

2. **Typography Scale**
   - Font families (headings, body, monospace)
   - Type scale (h1-h6, body, small, etc.)
   - Line heights and letter spacing

3. **Spacing System**
   - Base unit (e.g., 4px or 8px)
   - Spacing scale (xs, sm, md, lg, xl, 2xl, etc.)
   - Layout grid

4. **Component Tokens**
   - Border radius values
   - Shadow levels
   - Animation durations
   - Z-index scale

5. **Accessibility**
   - Color contrast ratios (WCAG AA/AAA)
   - Focus indicators
   - Touch target sizes

Output as Tailwind config or CSS variables.''',
        'parameters': [
            {
                'name': 'app_name',
                'type': 'string',
                'required': True,
                'description': 'Application name'
            },
            {
                'name': 'brand_identity',
                'type': 'text',
                'required': False,
                'description': 'Brand identity guidelines'
            },
            {
                'name': 'target_users',
                'type': 'string',
                'required': False,
                'description': 'Target user demographics'
            }
        ],
        'recommended_agent': 'UX Designer Agent',
        'example_usage': 'app_name: "HishamOS" brand_identity: "Professional, modern, AI-focused"',
        'tags': ['design-system', 'ui', 'branding']
    },
    {
        'name': 'Design Component UI',
        'slug': 'design-component-ui',
        'description': 'Create UI design for a specific component with variants and states',
        'template': '''Design UI component: {{component_name}}

Component Type: {{component_type}}
Use Cases: {{use_cases}}

Design specifications:
1. **Variants**
   - Size variants (sm, md, lg)
   - Color/theme variants
   - State variants (default, hover, active, disabled, loading, error)

2. **Layout**
   - Spacing and padding
   - Alignment and positioning
   - Responsive behavior

3. **Interaction States**
   - Default state
   - Hover/focus state
   - Active/pressed state
   - Disabled state
   - Loading state
   - Error state

4. **Accessibility**
   - ARIA labels and roles
   - Keyboard navigation
   - Screen reader considerations
   - Focus management

5. **Implementation Notes**
   - shadcn/ui component mapping (if applicable)
   - Tailwind CSS classes
   - Animation/transition details

Output: Component specification with Figma-style annotations.''',
        'parameters': [
            {
                'name': 'component_name',
                'type': 'string',
                'required': True,
                'description': 'Name of the component (e.g., "Button", "Card", "Modal")'
            },
            {
                'name': 'component_type',
                'type': 'choice',
                'choices': ['Button', 'Input', 'Card', 'Modal', 'Navigation', 'Table', 'Form', 'Custom'],
                'required': False,
                'description': 'Type of component'
            },
            {
                'name': 'use_cases',
                'type': 'text',
                'required': False,
                'description': 'Specific use cases for the component'
            }
        ],
        'recommended_agent': 'UX Designer Agent',
        'example_usage': 'component_name: "Dashboard Card" component_type: "Card"',
        'tags': ['ui-design', 'components', 'shadcn']
    },
    {
        'name': 'Create Page Layout',
        'slug': 'create-page-layout',
        'description': 'Design complete page layout with sections and component placement',
        'template': '''Design page layout for: {{page_name}}

Purpose: {{page_purpose}}
User Flow: {{user_flow}}

Layout structure:
1. **Header/Navigation**
   - Logo placement
   - Navigation items
   - User actions (login, profile, notifications)

2. **Main Content Area**
   - Content sections
   - Sidebar (if applicable)
   - Grid/Flexbox layout
   - Responsive breakpoints

3. **Footer**
   - Links and information
   - Social media
   - Legal/copyright

4. **Interactive Elements**
   - CTAs placement
   - Forms
   - Data visualizations

5. **Responsive Design**
   - Mobile layout (< 640px)
   - Tablet layout (640-1024px)
   - Desktop layout (> 1024px)

6. **Component Inventory**
   - List all components needed
   - Component hierarchy

Output: Wireframe description with component mapping.''',
        'parameters': [
            {
                'name': 'page_name',
                'type': 'string',
                'required': True,
                'description': 'Page name (e.g., "Dashboard", "Login", "Projects")'
            },
            {
                'name': 'page_purpose',
                'type': 'text',
                'required': True,
                'description': 'Main purpose of the page'
            },
            {
                'name': 'user_flow',
                'type': 'text',
                'required': False,
                'description': 'User flow and interactions'
            }
        ],
        'recommended_agent': 'UX Designer Agent',
        'example_usage': 'page_name: "Dashboard" page_purpose: "Overview of projects and agent status"',
        'tags': ['layout', 'wireframe', 'page-design']
    },
    {
        'name': 'Design Form UI',
        'slug': 'design-form-ui',
        'description': 'Create user-friendly form design with validation and error handling',
        'template': '''Design form UI for: {{form_purpose}}

Fields: {{fields}}

Form design:
1. **Field Layout**
   - Field grouping
   - Label placement
   - Input sizing
   - Help text positioning

2. **Field Types**
   - Text inputs
   - Select/dropdown
   - Radio/checkbox
   - Date pickers
   - File upload
   - Rich text editors

3. **Validation**
   - Real-time validation
   - Error message placement
   - Success indicators
   - Required field markers

4. **States**
   - Empty state
   - Focused state
   - Filled state
   - Error state
   - Disabled state

5. **Actions**
   - Submit button
   - Cancel/reset
   - Save draft
   - Multi-step navigation

6. **Accessibility**
   - Tab order
   - Error announcements
   - Field associations (label + input + error)

Output: Form specification with shadcn/ui form components.''',
        'parameters': [
            {
                'name': 'form_purpose',
                'type': 'string',
                'required': True,
                'description': 'Purpose of the form'
            },
            {
                'name': 'fields',
                'type': 'text',
                'required': True,
                'description': 'List of form fields (name:type)'
            }
        ],
        'recommended_agent': 'UX Designer Agent',
        'example_usage': 'form_purpose: "Create new project" fields: "name:text, description:textarea, deadline:date"',
        'tags': ['forms', 'validation', 'ui']
    },
    {
        'name': 'Create Navigation Design',
        'slug': 'create-navigation-design',
        'description': 'Design navigation system (sidebar, top nav, breadcrumbs)',
        'template': '''Design navigation for: {{app_section}}

Navigation Type: {{nav_type}}
Menu Items: {{menu_items}}

Navigation design:
1. **Structure**
   - Primary navigation items
   - Secondary/nested items
   - Icons for each item
   - Active state indication

2. **Layout**
   - Expanded vs collapsed states
   - Mobile hamburger menu
   - Responsive behavior
   - Sticky/fixed positioning

3. **Interactions**
   - Hover states
   - Active item highlighting
   - Expand/collapse animations
   - Sublevel disclosure

4. **User Context**
   - User profile/avatar
   - Current workspace/project indicator
   - Quick actions
   - Notifications badge

5. **Accessibility**
   - Keyboard navigation (arrow keys, Enter, Escape)
   - ARIA roles and labels
   - Focus indicators
   - Screen reader announcements

Output: Navigation specification with shadcn/ui navigation components.''',
        'parameters': [
            {
                'name': 'app_section',
                'type': 'string',
                'required': True,
                'description': 'App section or dashboard name'
            },
            {
                'name': 'nav_type',
                'type': 'choice',
                'choices': ['Sidebar', 'Top Navigation', 'Breadcrumbs', 'Tabs', 'Combined'],
                'required': True,
                'description': 'Type of navigation'
            },
            {
                'name': 'menu_items',
                'type': 'text',
                'required': True,
                'description': 'List of navigation items'
            }
        ],
        'recommended_agent': 'UX Designer Agent',
        'example_usage': 'app_section: "Main Dashboard" nav_type: "Sidebar" menu_items: "Dashboard, Projects, Agents, Workflows"',
        'tags': ['navigation', 'sidebar', 'menu']
    },
    {
        'name': 'Design Data Visualization',
        'slug': 'design-data-visualization',
        'description': 'Create data visualization design (charts, graphs, dashboards)',
        'template': '''Design data visualization for: {{data_type}}

Visualization Type: {{viz_type}}
Metrics: {{metrics}}

Visualization design:
1. **Chart Selection**
   - Chart type recommendation (line, bar, pie, scatter, etc.)
   - Reasoning for chart choice
   - Alternative chart options

2. **Visual Encoding**
   - Color scheme for data categories
   - Axis labels and scales
   - Legend placement
   - Data point markers

3. **Interactivity**
   - Hover tooltips
   - Click/drill-down
   - Zoom/pan
   - Filter controls
   - Date range selector

4. **Layout**
   - Chart sizing
   - Multiple charts arrangement
   - Responsive behavior
   - Empty state design

5. **Accessibility**
   - Color-blind safe palette
   - Alternative text descriptions
   - Data table alternative
   - Keyboard navigation

Library recommendations: Recharts, Chart.js, D3.js

Output: Visualization specification with implementation guide.''',
        'parameters': [
            {
                'name': 'data_type',
                'type': 'string',
                'required': True,
                'description': 'Type of data to visualize'
            },
            {
                'name': 'viz_type',
                'type': 'choice',
                'choices': ['Line Chart', 'Bar Chart', 'Pie Chart', 'Scatter Plot', 'Heatmap', 'Dashboard', 'Table'],
                'required': False,
                'description': 'Preferred visualization type'
            },
            {
                'name': 'metrics',
                'type': 'text',
                'required': False,
                'description': 'Metrics to display'
            }
        ],
        'recommended_agent': 'UX Designer Agent',
        'example_usage': 'data_type: "Sprint burndown" viz_type: "Line Chart"',
        'tags': ['data-viz', 'charts', 'dashboard']
    },
    {
        'name': 'Create Empty State Design',
        'slug': 'create-empty-state-design',
        'description': 'Design engaging empty states with call-to-action',
        'template': '''Design empty state for: {{context}}

User Action: {{primary_action}}

Empty state design:
1. **Visual Elements**
   - Illustration/icon (describe style)
   - Colors matching design system
   - Appropriate sizing

2. **Messaging**
   - Headline (friendly, clear)
   - Supporting text (explain why empty)
   - Tone (helpful, encouraging, not negative)

3. **Call-to-Action**
   - Primary CTA button
   - Secondary actions (if applicable)
   - Help/documentation link

4. **Variants**
   - First-time user (onboarding)
   - No results found (search/filter)
   - No data yet (new feature)
   - Error/permission denied

5. **Microcopy**
   - Examples of good empty state messages
   - Action-oriented language

Output: Empty state specification with copy and layout.''',
        'parameters': [
            {
                'name': 'context',
                'type': 'string',
                'required': True,
                'description': 'Where empty state appears (e.g., "No projects", "No search results")'
            },
            {
                'name': 'primary_action',
                'type': 'string',
                'required': True,
                'description': 'Action user should take (e.g., "Create Project", "Try different search")'
            }
        ],
        'recommended_agent': 'UX Designer Agent',
        'example_usage': 'context: "No projects created" primary_action: "Create your first project"',
        'tags': ['empty-state', 'ux', 'microcopy']
    },
    {
        'name': 'Design Modal/Dialog',
        'slug': 'design-modal-dialog',
        'description': 'Create modal dialog design with proper UX patterns',
        'template': '''Design modal/dialog for: {{modal_purpose}}

Modal Type: {{modal_type}}

Modal design:
1. **Structure**
   - Header with title and close button
   - Body content area
   - Footer with actions

2. **Sizing**
   - Width (sm: 400px, md: 600px, lg: 800px, full)
   - Max-height with scrolling
   - Responsive behavior

3. **Content**
   - Title/heading
   - Description/body text
   - Form fields (if applicable)
   - Illustrations/media

4. **Actions**
   - Primary action button
   - Secondary/cancel button
   - Destructive actions styling
   - Disabled states

5. **Behavior**
   - Backdrop/overlay
   - Focus trap
   - Escape key to close
   - Click outside to close (optional)
   - Animation (fade in/out)

6. **Accessibility**
   - ARIA role="dialog"
   - Focus management
   - Announcement to screen readers

Use shadcn/ui Dialog component.

Output: Modal specification with interaction details.''',
        'parameters': [
            {
                'name': 'modal_purpose',
                'type': 'string',
                'required': True,
                'description': 'Purpose of the modal'
            },
            {
                'name': 'modal_type',
                'type': 'choice',
                'choices': ['Confirmation', 'Form', 'Info', 'Alert', 'Media'],
                'required': False,
                'description': 'Type of modal'
            }
        ],
        'recommended_agent': 'UX Designer Agent',
        'example_usage': 'modal_purpose: "Delete project confirmation" modal_type: "Confirmation"',
        'tags': ['modal', 'dialog', 'overlay']
    },
    {
        'name': 'Create Loading States',
        'slug': 'create-loading-states',
        'description': 'Design loading states and skeleton screens',
        'template': '''Design loading state for: {{component_or_page}}

Loading Type: {{loading_type}}

Loading state design:
1. **Loading Indicator**
   - Spinner/loader style
   - Position (inline, centered, overlay)
   - Size variations
   - Color (matches theme)

2. **Skeleton Screen**
   - Component shape placeholders
   - Shimmer/pulse animation
   - Layout preservation
   - Content sections indication

3. **Progressive Loading**
   - Load priority order
   - Lazy loading strategy
   - Partial content display

4. **Messaging**
   - Loading text (if applicable)
   - Progress percentage
   - Time estimation
   - Error recovery

5. **Accessibility**
   - ARIA live regions
   - Screen reader announcements
   - Keyboard focus during loading

shadcn/ui: Use Skeleton component

Output: Loading state specification with animation details.''',
        'parameters': [
            {
                'name': 'component_or_page',
                'type': 'string',
                'required': True,
                'description': 'What is loading (e.g., "Project list", "Dashboard")'
            },
            {
                'name': 'loading_type',
                'type': 'choice',
                'choices': ['Spinner', 'Skeleton', 'Progress Bar', 'Shimmer'],
                'required': False,
                'description': 'Type of loading indicator'
            }
        ],
        'recommended_agent': 'UX Designer Agent',
        'example_usage': 'component_or_page: "Project dashboard" loading_type: "Skeleton"',
        'tags': ['loading', 'skeleton', 'spinner']
    },
    {
        'name': 'Design Notification System',
        'slug': 'design-notification-system',
        'description': 'Create notification/toast message design',
        'template': '''Design notification system for: {{notification_context}}

Notification Types Needed: {{notification_types}}

Notification design:
1. **Types**
   - Success (green)
   - Error (red)
   - Warning (yellow)
   - Info (blue)
   - Loading (neutral)

2. **Structure**
   - Icon (type-specific)
   - Title
   - Message text
   - Action buttons (optional)
   - Close button

3. **Positioning**
   - Top-right, top-center, bottom-right, etc.
   - Stack behavior (multiple toasts)
   - Z-index handling

4. **Behavior**
   - Auto-dismiss timeout (default 5s)
   - Manual dismiss
   - Action handling
   - Animation (slide in/out)

5. **Variants**
   - Toast (temporary)
   - Banner (persistent)
   - Badge (count indicator)
   - Inline message

shadcn/ui: Use Toast and Alert components

Output: Notification system specification.''',
        'parameters': [
            {
                'name': 'notification_context',
                'type': 'string',
                'required': True,
                'description': 'Where notifications appear'
            },
            {
                'name': 'notification_types',
                'type': 'string',
                'required': False,
                'description': 'Types needed (success, error, warning, info)'
            }
        ],
        'recommended_agent': 'UX Designer Agent',
        'example_usage': 'notification_context: "System-wide notifications" notification_types: "success, error, info"',
        'tags': ['notifications', 'toast', 'alerts']
    },
]


def load_ux_commands():
    """Load UI/UX commands for Phase 9 frontend development."""
    
    print("Loading UI/UX Design Commands for Phase 9...")
    
    # Get UX/UI Design category
    try:
        category = CommandCategory.objects.get(slug='ux-ui-design')
        print(f"\nCategory: {category.name}")
    except CommandCategory.DoesNotExist:
        print("\nError: UX/UI Design category not found!")
        return
    
    total_loaded = 0
    
    for cmd_data in UX_COMMANDS:
        # Check if command already exists
        if CommandTemplate.objects.filter(slug=cmd_data['slug']).exists():
            print(f"  [SKIP] {cmd_data['name']} (already exists)")
            continue
        
        # Lookup recommended agent
        agent = None
        agent_name = cmd_data.get('recommended_agent', '')
        if agent_name:
            try:
                agent = Agent.objects.filter(name__icontains='UX').first()
            except:
                pass
        
        # Create command
        command = CommandTemplate.objects.create(
            category=category,
            name=cmd_data['name'],
            slug=cmd_data['slug'],
            description=cmd_data['description'],
            template=cmd_data['template'],
            parameters=cmd_data['parameters'],
            recommended_agent=agent,
            example_usage=cmd_data.get('example_usage', ''),
            tags=cmd_data.get('tags', []),
            is_active=True,
            usage_count=0
        )
        
        total_loaded += 1
        print(f"  [OK] {command.name}")
    
    print(f"\n{'='*60}")
    print(f"Successfully loaded {total_loaded} UI/UX commands!")
    print(f"{'='*60}")
    
    # Show summary
    total_commands = CommandTemplate.objects.filter(category=category).count()
    print(f"\nTotal UI/UX commands: {total_commands}")


if __name__ == '__main__':
    load_ux_commands()
