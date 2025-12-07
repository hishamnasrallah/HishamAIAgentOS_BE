#!/usr/bin/env python3
"""
Enhanced Role Classification Script - Version 2.0
تحليل محتوى الملفات لتحديد الأدوار المناسبة بدقة عالية بناءً على المحتوى الفعلي
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict

# Enhanced role patterns based on actual content analysis
ENHANCED_ROLE_PATTERNS = {
    'Business Analyst': {
        'strong': [
            'requirements', 'requirement', 'business requirements', 'user story', 'user stories',
            'stakeholder', 'stakeholders', 'elicitation', 'business analysis', 'ba ',
            'business process', 'use case', 'use cases', 'functional requirements',
            'business rules', 'acceptance criteria', 'product owner', 'product backlog',
            'business value', 'business needs', 'business goals', 'business objectives',
            'requirements gathering', 'requirements analysis', 'requirements documentation',
            'project management', 'project plan', 'project planning', 'roadmap',
            'project status', 'milestone', 'sprint planning', 'release planning',
            'scope', 'feature specification', 'business logic', 'domain model'
        ],
        'medium': [
            'planning', 'plan', 'specification', 'spec', 'project', 'status report',
            'phase', 'tracking', 'audit', 'comprehensive audit', 'project roadmap'
        ]
    },
    'QA / Tester': {
        'strong': [
            'test', 'testing', 'qa', 'quality assurance', 'uat', 'test case', 'test cases',
            'manual test', 'automation', 'test execution', 'test checklist', 'test guide',
            'test results', 'bug', 'bugs', 'defect', 'defects', 'verification',
            'validation', 'test coverage', 'test plan', 'test strategy', 'test suite',
            'regression', 'smoke test', 'integration test', 'unit test', 'acceptance test',
            'user acceptance testing', 'test script', 'test data', 'test environment',
            'checklist', 'worksheet',
            'checklist', 'worksheet'
        ],
        'medium': [
            'guide', 'manual', 'tutorial', 'walkthrough', 'quick start', 'execution'
        ]
    },
    'Developer': {
        'strong': [
            'development', 'developer', 'coding', 'code', 'implementation', 'api',
            'backend', 'frontend', 'programming', 'technical', 'architecture', 'design',
            'sdlc', 'dev', 'deployment', 'infrastructure', 'docker', 'database', 'db',
            'class', 'function', 'method', 'module', 'component', 'service', 'endpoint',
            'framework', 'library', 'dependency', 'package', 'import', 'export',
            'migration', 'model', 'view', 'controller', 'middleware', 'authentication',
            'authorization', 'jwt', 'token', 'session', 'redis', 'celery', 'websocket',
            'command', 'commands', 'workflow', 'agent', 'agents',
            'command', 'commands', 'workflow', 'agent', 'agents'
        ],
        'medium': [
            'guide', 'manual', 'reference', 'documentation', 'specification',
            'technical architecture', 'system design', 'data model', 'master development'
        ]
    },
    'Project Manager': {
        'strong': [
            'project management', 'project manager', 'pm', 'sprint', 'sprints',
            'milestone', 'milestones', 'roadmap', 'project plan', 'project planning',
            'release plan', 'release planning', 'status report', 'status reports',
            'project status', 'progress', 'tracking', 'task', 'tasks', 'backlog',
            'sprint planning', 'sprint review', 'retrospective', 'standup',
            'project timeline', 'project schedule', 'project scope', 'risk management',
            'stakeholder management', 'resource management', 'delivery', 'deadline',
            'phase status', 'completion', 'blocker', 'blockers'
        ],
        'medium': [
            'plan', 'planning', 'status', 'phase', 'phase status', 'completion',
            'tracking', 'audit', 'summary', 'overview', 'report'
        ]
    },
    'CTO / Technical Lead': {
        'strong': [
            'architecture', 'technical architecture', 'system architecture', 'design',
            'system design', 'technical design', 'cto', 'technical lead', 'leadership',
            'strategy', 'roadmap', 'vision', 'complete design', 'technical reference',
            'master development', 'technical strategy', 'technology stack', 'tech stack',
            'infrastructure design', 'scalability', 'performance', 'security architecture',
            'enterprise architecture', 'solution architecture'
        ],
        'medium': [
            'overview', 'summary', 'guide', 'reference', 'specification', 'documentation'
        ]
    },
    'Technical Writer': {
        'strong': [
            'documentation', 'doc', 'guide', 'manual', 'tutorial', 'walkthrough',
            'reference', 'specification', 'specs',             'documentation_maintenance',
            'api_documentation', 'docs_viewer', 'user guide', 'user manual',
            'technical writing', 'documentation guide', 'writing guidelines',
            'changelog', 'release notes',
            'changelog', 'release notes'
        ],
        'medium': [
            'readme', 'index', 'overview', 'introduction', 'getting started'
        ]
    },
    'DevOps': {
        'strong': [
            'devops', 'deployment', 'infrastructure', 'docker', 'ci/cd', 'cicd',
            'production', 'environment', 'server', 'kubernetes', 'k8s', 'terraform',
            'ansible', 'jenkins', 'gitlab', 'github actions', 'deployment_infrastructure',
            'container', 'containers', 'dockerfile', 'docker-compose', 'orchestration',
            'monitoring', 'logging', 'monitoring', 'alerting', 'scaling', 'load balancing'
        ],
        'medium': [
            'deployment guide', 'infrastructure guide', 'deployment infrastructure'
        ]
    },
    'Scrum Master': {
        'strong': [
            'scrum', 'agile', 'sprint', 'retrospective', 'standup', 'ceremony',
            'backlog', 'velocity', 'burndown', 'kanban', 'sdlc_roles', 'sprint planning',
            'sprint review', 'daily standup', 'sprint retrospective', 'scrum master',
            'product owner', 'stakeholder', 'sprint goal', 'definition of done'
        ],
        'medium': [
            'agile', 'sprint', 'planning', 'tracking'
        ]
    },
    'Infrastructure': {
        'strong': [
            'infrastructure', 'infra', 'server', 'network', 'security', 'monitoring',
            'logging', 'tracking', 'audit', 'performance', 'scalability', 'availability',
            'backup', 'disaster recovery', 'cloud', 'aws', 'azure', 'gcp', 'server',
            'database', 'storage', 'compute', 'network', 'security', 'firewall',
            'load balancer', 'cdn', 'dns', 'ssl', 'certificate'
        ],
        'medium': [
            'infrastructure', 'deployment', 'configuration', 'setup'
        ]
    }
}

def analyze_file_content(file_path: Path) -> dict:
    """Analyze file content to determine appropriate roles - ENHANCED VERSION."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return {}
    
    # Parse YAML frontmatter if present
    yaml_metadata = None
    frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    match = frontmatter_pattern.match(content)
    
    # If metadata already has good roles, prefer them
    if match:
        try:
            yaml_metadata = yaml.safe_load(match.group(1))
            existing_audience = yaml_metadata.get('target_audience', {})
            existing_primary = existing_audience.get('primary', [])
            existing_secondary = existing_audience.get('secondary', [])
            
            # If metadata has good roles (not "All" or empty), use them
            if existing_primary and existing_primary != ['All'] and len(existing_primary) >= 1:
                # Return existing if they look good
                if any(role != 'All' for role in existing_primary):
                    return {
                        'primary': [r for r in existing_primary if r != 'All'][:2],
                        'secondary': [r for r in existing_secondary if r != 'All'],
                        'scores': {},
                        'from_metadata': True
                    }
        except:
            pass
    
    # Remove frontmatter for content analysis
    if match:
        content_body = content[match.end():]
    else:
        content_body = content
    
    content_lower = content_body.lower()
    
    # Get file info
    filename = file_path.name.lower()
    path_parts = str(file_path).lower().split(os.sep)
    directory = '/'.join(path_parts[-2:-1]) if len(path_parts) > 1 else ''
    
    # Read first 3000 chars for analysis (enough to understand context)
    analysis_content = content_lower[:3000]
    
    # Combine all searchable text
    all_text = f"{filename} {directory} {analysis_content}"
    
    # Score each role with improved logic
    role_scores = defaultdict(int)
    
    for role, patterns in ENHANCED_ROLE_PATTERNS.items():
        # Strong patterns = 5 points (more weight)
        strong_matches = 0
        for pattern in patterns.get('strong', []):
            if pattern.lower() in all_text:
                strong_matches += 1
                role_scores[role] += 5
        # Limit strong matches bonus
        if strong_matches > 3:
            role_scores[role] += 2  # Bonus for many strong matches
        
        # Medium patterns = 2 points
        for pattern in patterns.get('medium', []):
            if pattern.lower() in all_text:
                role_scores[role] += 2
                break  # Count once per role
    
    # Enhanced directory-based rules
    if 'testing' in directory or 'test' in directory or 'qa' in directory:
        role_scores['QA / Tester'] += 5  # Strong signal
        role_scores['Developer'] += 2
    
    if 'planning' in directory or 'project' in directory.lower():
        role_scores['Project Manager'] += 4
        role_scores['Business Analyst'] += 3
        role_scores['Scrum Master'] += 2
    
    if 'development' in directory or 'dev' in directory:
        role_scores['Developer'] += 5
        role_scores['CTO / Technical Lead'] += 2
    
    if 'tracking' in directory or 'status' in directory:
        role_scores['Project Manager'] += 4
        role_scores['Business Analyst'] += 2
    
    if 'design' in directory or 'architecture' in directory:
        role_scores['CTO / Technical Lead'] += 5
        role_scores['Developer'] += 3
        role_scores['Business Analyst'] += 1
    
    if 'deployment' in directory or 'infrastructure' in directory:
        role_scores['DevOps'] += 5
        role_scores['Infrastructure'] += 3
        role_scores['Developer'] += 2
    
    if 'commands' in directory:
        role_scores['Developer'] += 4
        role_scores['Technical Writer'] += 2
        role_scores['QA / Tester'] += 1
    
    # Content-based analysis (check for key phrases in content)
    content_indicators = {
        'Business Analyst': ['user story', 'requirements', 'stakeholder', 'business process', 'acceptance criteria'],
        'QA / Tester': ['test case', 'test execution', 'bug', 'defect', 'verification', 'validation', 'checklist'],
        'Developer': ['code', 'implementation', 'api', 'function', 'class', 'module', 'endpoint', 'database', 'migration'],
        'Project Manager': ['sprint', 'milestone', 'roadmap', 'timeline', 'resource allocation', 'risk register'],
        'Technical Writer': ['documentation', 'guide', 'manual', 'tutorial', 'reference', 'writing guidelines'],
        'DevOps': ['docker', 'kubernetes', 'deployment', 'ci/cd', 'infrastructure', 'production'],
        'CTO / Technical Lead': ['architecture', 'system design', 'technical strategy', 'technology stack']
    }
    
    for role, indicators in content_indicators.items():
        matches = sum(1 for indicator in indicators if indicator in analysis_content)
        if matches >= 2:
            role_scores[role] += matches * 2  # 2 points per match
    
    # Determine primary and secondary roles
    # Primary: roles with score >= 6 (higher threshold for accuracy)
    # Secondary: roles with score >= 3 and < 6
    primary_roles = [role for role, score in role_scores.items() if score >= 6]
    secondary_roles = [role for role, score in role_scores.items() if 3 <= score < 6]
    
    # If no primary roles, use top 2 roles with score >= 3
    if not primary_roles:
        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        primary_roles = [role for role, score in sorted_roles[:2] if score >= 3]
        secondary_roles = [role for role, score in sorted_roles[2:5] if score >= 2]
    
    # Ensure at least one role
    if not primary_roles and not secondary_roles:
        # Default based on directory or file type
        if 'test' in filename or 'testing' in directory:
            primary_roles = ['QA / Tester']
        elif 'project' in filename.lower() or 'status' in filename.lower() or 'roadmap' in filename.lower():
            primary_roles = ['Project Manager']
        elif 'development' in filename.lower() or 'dev' in filename.lower() or 'master' in filename.lower():
            primary_roles = ['Developer']
        elif 'deployment' in filename.lower() or 'docker' in filename.lower():
            primary_roles = ['DevOps']
        else:
            primary_roles = ['General']
    
    # Remove duplicates
    primary_roles = list(dict.fromkeys(primary_roles))[:2]
    secondary_roles = [r for r in dict.fromkeys(secondary_roles) if r not in primary_roles]
    
    return {
        'primary': primary_roles,
        'secondary': secondary_roles,
        'scores': dict(role_scores)
    }

def update_file_metadata(file_path: Path, force=False):
    """Update file metadata with improved roles."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False, "Could not read file"
    
    # Parse YAML frontmatter
    frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    match = frontmatter_pattern.match(content)
    
    if not match:
        return False, "No frontmatter found"
    
    try:
        yaml_content = match.group(1)
        metadata = yaml.safe_load(yaml_content) or {}
        remaining_content = content[match.end():]
    except Exception as e:
        # Try to fix common YAML issues (unescaped quotes in strings)
        try:
            # Replace problematic double quotes with single quotes in description
            fixed_yaml = yaml_content
            # Fix description field if it has unescaped quotes
            if 'description:' in fixed_yaml:
                import re as re_module
                # Find description field and fix quotes
                desc_pattern = r'description:\s*["\'](.*?)["\']'
                def fix_quotes(m):
                    content = m.group(1)
                    # Replace internal double quotes with single quotes
                    content = content.replace('"', "'")
                    return f"description: \"{content}\""
                fixed_yaml = re_module.sub(desc_pattern, fix_quotes, fixed_yaml, flags=re_module.DOTALL)
            
            metadata = yaml.safe_load(fixed_yaml) or {}
            remaining_content = content[match.end():]
        except Exception as e2:
            return False, f"Error parsing YAML (could not auto-fix): {e2}"
    
    # Check if already has good roles and force=False
    if not force:
        existing_audience = metadata.get('target_audience', {})
        existing_primary = existing_audience.get('primary', [])
        # Skip if has good primary roles (not "All" or empty)
        if existing_primary and existing_primary != ['All'] and len(existing_primary) >= 1:
            if all(role != 'All' for role in existing_primary):
                return False, "Already has good roles"
    
    # Analyze file to get roles
    analysis = analyze_file_content(file_path)
    
    if not analysis.get('primary'):
        return False, "Could not determine roles"
    
    # Update target_audience
    if 'target_audience' not in metadata:
        metadata['target_audience'] = {}
    
    metadata['target_audience']['primary'] = analysis['primary']
    metadata['target_audience']['secondary'] = analysis['secondary']
    
    # Write updated content
    try:
        updated_yaml = yaml.dump(metadata, default_flow_style=False, allow_unicode=True, sort_keys=False)
        # Ensure proper formatting
        if not updated_yaml.endswith('\n'):
            updated_yaml += '\n'
        updated_content = f"---\n{updated_yaml}---\n\n{remaining_content}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True, f"Updated: primary={analysis['primary']}, secondary={analysis['secondary']}"
    except Exception as e:
        return False, f"Error writing file: {e}"

def main():
    """Main function to process all documentation files."""
    import sys
    
    docs_dir = Path('docs')
    if not docs_dir.exists():
        print("Error: docs directory not found")
        return
    
    # Check for --force flag
    force = '--force' in sys.argv
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"🔍 Analyzing documentation files...")
    print(f"Mode: {'FORCE (updating all)' if force else 'Smart (skipping good ones)'}")
    print("-" * 80)
    
    # Process all markdown files
    for md_file in sorted(docs_dir.rglob('*.md')):
        # Skip README files
        if md_file.name == 'README.md':
            continue
        
        rel_path = md_file.relative_to(docs_dir)
        success, message = update_file_metadata(md_file, force=force)
        
        if success:
            print(f"✅ {rel_path}")
            print(f"   {message}")
            updated_count += 1
        elif "Already has good roles" in message:
            print(f"⏭️  {rel_path} - Skipped (already has good roles)")
            skipped_count += 1
        else:
            print(f"❌ {rel_path} - {message}")
            error_count += 1
    
    print("-" * 80)
    print(f"\n📊 Summary:")
    print(f"✅ Updated: {updated_count} files")
    print(f"⏭️  Skipped: {skipped_count} files")
    print(f"❌ Errors: {error_count} files")
    print(f"\n💡 Tip: Use --force to update all files including those with existing good roles")

if __name__ == '__main__':
    main()
