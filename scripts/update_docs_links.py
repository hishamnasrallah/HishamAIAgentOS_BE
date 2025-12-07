#!/usr/bin/env python3
"""
Script to update documentation links after reorganization.
"""

import os
import re
from pathlib import Path

# Path mapping from old to new
PATH_MAPPINGS = {
    # Old paths → New paths
    r'docs/testing/': r'docs/03_TESTING/',
    r'\.\./testing/': r'../03_TESTING/',
    r'\.\./\.\./testing/': r'../../03_TESTING/',
    
    r'docs/tracking/': r'docs/07_TRACKING/',
    r'\.\./tracking/': r'../07_TRACKING/',
    r'\.\./\.\./tracking/': r'../../07_TRACKING/',
    
    r'docs/project_planning/': r'docs/06_PLANNING/',
    r'\.\./project_planning/': r'../06_PLANNING/',
    r'\.\./\.\./project_planning/': r'../../06_PLANNING/',
    
    r'docs/how_to_develop/': r'docs/05_DEVELOPMENT/',
    r'\.\./how_to_develop/': r'../05_DEVELOPMENT/',
    r'\.\./\.\./how_to_develop/': r'../../05_DEVELOPMENT/',
    
    r'docs/commands/': r'docs/08_COMMANDS/',
    r'\.\./commands/': r'../08_COMMANDS/',
    r'\.\./\.\./commands/': r'../../08_COMMANDS/',
    
    r'docs/deployment/': r'docs/04_DEPLOYMENT/',
    r'\.\./deployment/': r'../04_DEPLOYMENT/',
    r'\.\./\.\./deployment/': r'../../04_DEPLOYMENT/',
    
    r'docs/design/': r'docs/02_DESIGN/',
    r'\.\./design/': r'../02_DESIGN/',
    r'\.\./\.\./design/': r'../../02_DESIGN/',
    
    r'docs/implementation_plan/': r'docs/06_PLANNING/IMPLEMENTATION/',
    r'\.\./implementation_plan/': r'../06_PLANNING/IMPLEMENTATION/',
}

# Specific file mappings
FILE_MAPPINGS = {
    # Old path → New path
    r'QUICK_START_TESTING_GUIDE\.md': r'03_TESTING/QUICK_START_TESTING_GUIDE.md',
    r'UAT_TESTING_CHECKLIST\.md': r'03_TESTING/UAT_TESTING_CHECKLIST.md',
    r'COMMAND_TESTING_CHECKLIST\.md': r'03_TESTING/COMMAND_TESTING_CHECKLIST.md',
    r'TEST_EXECUTION_WORKSHEET\.md': r'03_TESTING/TEST_EXECUTION_WORKSHEET.md',
    r'USER_JOURNEY_GUIDE\.md': r'03_TESTING/USER_JOURNEY_GUIDE.md',
    r'PROJECT_STATUS_DEC_2024\.md': r'01_CORE/STATUS/PROJECT_STATUS_DEC_2024.md',
    r'RELEASE_NOTES_DEC_2024\.md': r'01_CORE/STATUS/RELEASE_NOTES_DEC_2024.md',
    r'MASTER_DEVELOPMENT_GUIDE\.md': r'05_DEVELOPMENT/MASTER_DEVELOPMENT_GUIDE.md',
    r'DOCUMENTATION_MAINTENANCE\.md': r'05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md',
    r'PRODUCTION_DEPLOYMENT_GUIDE\.md': r'04_DEPLOYMENT/PRODUCTION_DEPLOYMENT_GUIDE.md',
    r'COMMAND_LIBRARY_DOCUMENTATION\.md': r'08_COMMANDS/COMMAND_LIBRARY_DOCUMENTATION.md',
    r'COMMAND_TESTING_GUIDE\.md': r'08_COMMANDS/COMMAND_TESTING_GUIDE.md',
    r'TRACKING_LOGGING_AUDIT\.md': r'07_TRACKING/TRACKING_LOGGING_AUDIT.md',
    r'01_BA_Artifacts\.md': r'06_PLANNING/BA_ARTIFACTS.md',
    r'02_User_Stories\.md': r'06_PLANNING/USER_STORIES.md',
    r'03_Technical_Architecture\.md': r'06_PLANNING/TECHNICAL_ARCHITECTURE.md',
    r'04_Project_Plan\.md': r'06_PLANNING/PROJECT_PLANS/PROJECT_PLAN.md',
    r'05_Implementation_Specs\.md': r'06_PLANNING/IMPLEMENTATION/IMPLEMENTATION_SPECS.md',
    r'06_Full_Technical_Reference\.md': r'06_PLANNING/IMPLEMENTATION/FULL_TECHNICAL_REFERENCE.md',
    r'MASTER_DEVELOPMENT_PLAN\.md': r'06_PLANNING/PROJECT_PLANS/MASTER_DEVELOPMENT_PLAN.md',
}

def update_file_links(file_path: Path):
    """Update links in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        # Apply path mappings
        for old_path, new_path in PATH_MAPPINGS.items():
            pattern = re.compile(old_path, re.IGNORECASE)
            if pattern.search(content):
                content = pattern.sub(new_path, content)
                updated = True
        
        # Apply file mappings (more specific)
        for old_file, new_file in FILE_MAPPINGS.items():
            # Match in markdown links: [text](path/to/old_file.md)
            pattern1 = re.compile(rf'(\[.*?\]\()([^)]*?){old_file}\)', re.IGNORECASE)
            if pattern1.search(content):
                def replace_func(match):
                    prefix = match.group(2)
                    # Normalize path
                    if prefix.startswith('./'):
                        prefix = prefix[2:]
                    elif prefix.startswith('../'):
                        # Count ../ to determine depth
                        depth = prefix.count('../')
                        prefix = '../' * depth
                    elif not prefix.startswith('01_') and not prefix.startswith('02_') and not prefix.startswith('03_'):
                        # Relative path without prefix
                        prefix = ''
                    return f'{match.group(1)}{prefix}{new_file})'
                content = pattern1.sub(replace_func, content)
                updated = True
        
        # Only write if changed
        if updated and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function."""
    docs_dir = Path("docs")
    
    if not docs_dir.exists():
        print("❌ docs/ directory not found!")
        return
    
    print("🔗 Starting link update...")
    print(f"📂 Scanning: {docs_dir}")
    print()
    
    updated_count = 0
    error_count = 0
    
    # Process all markdown files
    for md_file in docs_dir.rglob("*.md"):
        if update_file_links(md_file):
            rel_path = md_file.relative_to(docs_dir)
            print(f"✅ Updated: {rel_path}")
            updated_count += 1
    
    print()
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"✅ Updated: {updated_count} files")
    print(f"❌ Errors: {error_count} files")
    print()
    print("✨ Link update complete!")

if __name__ == "__main__":
    main()

