#!/usr/bin/env python3
"""
Script to reorganize documentation files from backend/docs/ to docs/
with automatic metadata generation.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Paths
SOURCE_DIR = Path("backend/docs")
TARGET_DIR = Path("docs")

# Mapping from old paths to new paths
FILE_MAPPING = {
    # 01_CORE - Core Documentation
    "README.md": "01_CORE/README.md",
    "فهرس_المحتوى.md": "01_CORE/INDEXES/فهرس_المحتوى.md",
    "hishamos_INDEX.md": "01_CORE/INDEXES/hishamos_INDEX.md",
    "PROJECT_STATUS_DEC_2024.md": "01_CORE/STATUS/PROJECT_STATUS_DEC_2024.md",
    "RELEASE_NOTES_DEC_2024.md": "01_CORE/STATUS/RELEASE_NOTES_DEC_2024.md",
    "TASK_TRACKER.md": "01_CORE/STATUS/TASK_TRACKER.md",
    "PROJECT_MANAGEMENT_USER_GUIDE.md": "01_CORE/USER_GUIDES/PROJECT_MANAGEMENT_USER_GUIDE.md",
    "WALKTHROUGH.md": "01_CORE/USER_GUIDES/WALKTHROUGH.md",
    "ADMIN_USER_MANAGEMENT.md": "01_CORE/USER_GUIDES/ADMIN_USER_MANAGEMENT.md",
    "DOCS_VIEWER_README.md": "01_CORE/ADMIN/DOCS_VIEWER_README.md",
    "FINAL_SUMMARY_AR.md": "01_CORE/SUMMARIES/FINAL_SUMMARY_AR.md",
    "RESTRUCTURING_SUMMARY.md": "01_CORE/SUMMARIES/RESTRUCTURING_SUMMARY.md",
    "analysis_hishamos.md": "01_CORE/SUMMARIES/analysis_hishamos.md",
    "API_DOCUMENTATION_FIXES.md": "01_CORE/ADMIN/API_DOCUMENTATION_FIXES.md",
    
    # 02_DESIGN - Design & Specifications
    "design/ui_redesign_plan.md": "02_DESIGN/UI/ui_redesign_plan.md",
    "hishamos_admin_management_screens.md": "02_DESIGN/UI/hishamos_admin_management_screens.md",
    "hishamos_ai_project_management.md": "02_DESIGN/UI/hishamos_ai_project_management.md",
    "hishamos_complete_design_part1.md": "02_DESIGN/ARCHITECTURE/hishamos_complete_design_part1.md",
    "hishamos_complete_design_part2.md": "02_DESIGN/ARCHITECTURE/hishamos_complete_design_part2.md",
    "hishamos_complete_design_part3.md": "02_DESIGN/ARCHITECTURE/hishamos_complete_design_part3.md",
    "hishamos_complete_design_part4.md": "02_DESIGN/ARCHITECTURE/hishamos_complete_design_part4.md",
    "hishamos_complete_design_part5.md": "02_DESIGN/ARCHITECTURE/hishamos_complete_design_part5.md",
    "hishamos_complete_sdlc_roles_workflows.md": "02_DESIGN/ARCHITECTURE/hishamos_complete_sdlc_roles_workflows.md",
    "hishamos_complete_prompts_library.md": "02_DESIGN/PROMPTS/hishamos_complete_prompts_library.md",
    "reference_prompts.md": "02_DESIGN/PROMPTS/reference_prompts.md",
    "hishamos_critical_gaps_solutions.md": "02_DESIGN/GAPS/hishamos_critical_gaps_solutions.md",
    "hishamos_critical_gaps_solutions_part2.md": "02_DESIGN/GAPS/hishamos_critical_gaps_solutions_part2.md",
    "hishamos_critical_gaps_solutions_part3.md": "02_DESIGN/GAPS/hishamos_critical_gaps_solutions_part3.md",
    "hishamos_missing_features_roadmap.md": "02_DESIGN/ROADMAP/hishamos_missing_features_roadmap.md",
    
    # 03_TESTING - Testing Documentation
    "testing/QUICK_START_TESTING_GUIDE.md": "03_TESTING/QUICK_START_TESTING_GUIDE.md",
    "testing/UAT_TESTING_CHECKLIST.md": "03_TESTING/UAT_TESTING_CHECKLIST.md",
    "testing/UAT_USER_ACCEPTANCE_TESTING.md": "03_TESTING/UAT_USER_ACCEPTANCE_TESTING.md",
    "testing/COMMAND_TESTING_CHECKLIST.md": "03_TESTING/COMMAND_TESTING_CHECKLIST.md",
    "testing/DOCUMENTATION_INDEX.md": "03_TESTING/DOCUMENTATION_INDEX.md",
    "testing/USER_JOURNEY_GUIDE.md": "03_TESTING/USER_JOURNEY_GUIDE.md",
    "testing/TEST_EXECUTION_WORKSHEET.md": "03_TESTING/TEST_EXECUTION_WORKSHEET.md",
    "testing/ADMIN_UI_MANUAL_TESTING_CHECKLIST.md": "03_TESTING/MANUAL_TEST_CHECKLISTS/ADMIN_UI_MANUAL_TESTING_CHECKLIST.md",
    "testing/ADMIN_UI_BUG_FIXES.md": "03_TESTING/MANUAL_TEST_CHECKLISTS/ADMIN_UI_BUG_FIXES.md",
    "testing/SYSTEM_SETTINGS_UI_MANUAL_TESTING_CHECKLIST.md": "03_TESTING/MANUAL_TEST_CHECKLISTS/SYSTEM_SETTINGS_UI_MANUAL_TESTING_CHECKLIST.md",
    "testing/SYSTEM_SETTINGS_UI_IMPLEMENTATION.md": "03_TESTING/IMPLEMENTATION/SYSTEM_SETTINGS_UI_IMPLEMENTATION.md",
    "testing/USAGE_ANALYTICS_UI_IMPLEMENTATION.md": "03_TESTING/IMPLEMENTATION/USAGE_ANALYTICS_UI_IMPLEMENTATION.md",
    
    # 04_DEPLOYMENT - Deployment Documentation
    "deployment/PRODUCTION_DEPLOYMENT_GUIDE.md": "04_DEPLOYMENT/PRODUCTION_DEPLOYMENT_GUIDE.md",
    "deployment/DEPLOYMENT_INFRASTRUCTURE_SUMMARY.md": "04_DEPLOYMENT/DEPLOYMENT_INFRASTRUCTURE_SUMMARY.md",
    
    # 05_DEVELOPMENT - Development Guides
    "how_to_develop/MASTER_DEVELOPMENT_GUIDE.md": "05_DEVELOPMENT/MASTER_DEVELOPMENT_GUIDE.md",
    "how_to_develop/DOCUMENTATION_MAINTENANCE.md": "05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md",
    "how_to_develop/VERIFICATION_CHECKLIST.md": "05_DEVELOPMENT/VERIFICATION_CHECKLIST.md",
    
    # 06_PLANNING - Planning & Projects
    "project_planning/01_BA_Artifacts.md": "06_PLANNING/BA_ARTIFACTS.md",
    "project_planning/02_User_Stories.md": "06_PLANNING/USER_STORIES.md",
    "project_planning/03_Technical_Architecture.md": "06_PLANNING/TECHNICAL_ARCHITECTURE.md",
    "project_planning/04_Project_Plan.md": "06_PLANNING/PROJECT_PLANS/PROJECT_PLAN.md",
    "project_planning/MASTER_DEVELOPMENT_PLAN.md": "06_PLANNING/PROJECT_PLANS/MASTER_DEVELOPMENT_PLAN.md",
    "project_planning/05_Implementation_Specs.md": "06_PLANNING/IMPLEMENTATION/IMPLEMENTATION_SPECS.md",
    "project_planning/06_Full_Technical_Reference.md": "06_PLANNING/IMPLEMENTATION/FULL_TECHNICAL_REFERENCE.md",
    "implementation_plan/implementation_plan.md": "06_PLANNING/IMPLEMENTATION/IMPLEMENTATION_PLAN.md",
    "implementation_plan/task.md": "06_PLANNING/IMPLEMENTATION/task.md",
    "IMPLEMENTATION_PLAN.md": "06_PLANNING/IMPLEMENTATION/IMPLEMENTATION_PLAN.md",
    
    # 08_COMMANDS - Commands & Libraries
    "commands/COMMAND_LIBRARY_DOCUMENTATION.md": "08_COMMANDS/COMMAND_LIBRARY_DOCUMENTATION.md",
    "commands/COMMAND_TESTING_GUIDE.md": "08_COMMANDS/COMMAND_TESTING_GUIDE.md",
    
    # 09_PHASES - Phases & Completion (Root level)
    "PHASE_3_COMPLETION.md": "09_PHASES/PHASE_3/PHASE_3_COMPLETION.md",
    "PHASE_3_MODEL_CHANGES_REVIEW.md": "09_PHASES/PHASE_3/PHASE_3_MODEL_CHANGES_REVIEW.md",
    "PHASE_3_TESTING_GUIDE.md": "09_PHASES/PHASE_3/PHASE_3_TESTING_GUIDE.md",
    "PHASE_4_COMPLETION.md": "09_PHASES/PHASE_4/PHASE_4_COMPLETION.md",
    "PHASE_5_AGENT_TEMPLATES.md": "09_PHASES/PHASE_5/PHASE_5_AGENT_TEMPLATES.md",
    "PHASE_5_COMPLETION.md": "09_PHASES/PHASE_5/PHASE_5_COMPLETION.md",
    "PHASE_6_COMPLETE.md": "09_PHASES/PHASE_6/PHASE_6_COMPLETE.md",
    "PHASE_6_IMPLEMENTATION_PLAN.md": "09_PHASES/PHASE_6/PHASE_6_IMPLEMENTATION_PLAN.md",
    "PHASE_6_INFRASTRUCTURE_COMPLETE.md": "09_PHASES/PHASE_6/PHASE_6_INFRASTRUCTURE_COMPLETE.md",
    "PHASE_6_PROGRESS.md": "09_PHASES/PHASE_6/PHASE_6_PROGRESS.md",
    "PHASE_9B_GUIDE.md": "09_PHASES/PHASE_9/PHASE_9B_GUIDE.md",
    "PHASE_9C_SUMMARY.md": "09_PHASES/PHASE_9/PHASE_9C_SUMMARY.md",
    
    # 09_PHASES - From tracking/ folder (Phase files that should go to 09_PHASES)
    "tracking/PHASE_9_10_AUDIT.md": "09_PHASES/PHASE_9/PHASE_9_10_AUDIT.md",
    "tracking/PHASE_9_10_COMPLETION.md": "09_PHASES/PHASE_9/PHASE_9_10_COMPLETION.md",
    "tracking/PHASE_10_VERIFICATION.md": "09_PHASES/PHASE_10/PHASE_10_VERIFICATION.md",
    "tracking/PHASE_11_12_IMPLEMENTATION_PLAN.md": "09_PHASES/PHASE_11_12/PHASE_11_12_IMPLEMENTATION_PLAN.md",
    "tracking/PHASE_13_14_IMPLEMENTATION_PLAN.md": "09_PHASES/PHASE_13_14/PHASE_13_14_IMPLEMENTATION_PLAN.md",
    "tracking/PHASE_15_16_IMPLEMENTATION_PLAN.md": "09_PHASES/PHASE_15_16/PHASE_15_16_IMPLEMENTATION_PLAN.md",
    "tracking/PHASE_17_18_IMPLEMENTATION_PLAN.md": "09_PHASES/PHASE_17_18/PHASE_17_18_IMPLEMENTATION_PLAN.md",
    "tracking/PHASE_STATUS_SUMMARY.md": "09_PHASES/PHASE_STATUS_SUMMARY.md",
    "tracking/PHASE_9_10_AUDIT.md": "09_PHASES/PHASE_9/PHASE_9_10_AUDIT.md",
    "tracking/PHASE_9_10_COMPLETION.md": "09_PHASES/PHASE_9/PHASE_9_10_COMPLETION.md",
    "tracking/PHASE_10_VERIFICATION.md": "09_PHASES/PHASE_10/PHASE_10_VERIFICATION.md",
    "tracking/PHASE_11_12_IMPLEMENTATION_PLAN.md": "09_PHASES/PHASE_11_12/PHASE_11_12_IMPLEMENTATION_PLAN.md",
    "tracking/PHASE_13_14_IMPLEMENTATION_PLAN.md": "09_PHASES/PHASE_13_14/PHASE_13_14_IMPLEMENTATION_PLAN.md",
    "tracking/PHASE_15_16_IMPLEMENTATION_PLAN.md": "09_PHASES/PHASE_15_16/PHASE_15_16_IMPLEMENTATION_PLAN.md",
    "tracking/PHASE_17_18_IMPLEMENTATION_PLAN.md": "09_PHASES/PHASE_17_18/PHASE_17_18_IMPLEMENTATION_PLAN.md",
    "tracking/PHASE_STATUS_SUMMARY.md": "09_PHASES/PHASE_STATUS_SUMMARY.md",
}

# Category mappings
CATEGORY_MAP = {
    "01_CORE": {"category": "Core", "subcategories": {
        "INDEXES": "Indexes",
        "STATUS": "Status",
        "USER_GUIDES": "User Guides",
        "ADMIN": "Admin",
        "SUMMARIES": "Summaries",
    }},
    "02_DESIGN": {"category": "Design", "subcategories": {
        "ARCHITECTURE": "Architecture",
        "UI": "UI",
        "GAPS": "Gaps",
        "ROADMAP": "Roadmap",
        "PROMPTS": "Prompts",
    }},
    "03_TESTING": {"category": "Testing", "subcategories": {
        "MANUAL_TEST_CHECKLISTS": "Manual Testing",
        "IMPLEMENTATION": "Implementation",
    }},
    "04_DEPLOYMENT": {"category": "Deployment", "subcategories": {}},
    "05_DEVELOPMENT": {"category": "Development", "subcategories": {}},
    "06_PLANNING": {"category": "Planning", "subcategories": {
        "PROJECT_PLANS": "Project Plans",
        "IMPLEMENTATION": "Implementation",
    }},
    "07_TRACKING": {"category": "Tracking", "subcategories": {
        "STATUS": "Status",
        "IMPLEMENTATION": "Implementation",
        "BUGS_FIXES": "Bugs & Fixes",
        "PHASES": "Phases",
    }},
    "08_COMMANDS": {"category": "Commands", "subcategories": {}},
    "09_PHASES": {"category": "Phases", "subcategories": {
        "PHASE_0": "Phase 0",
        "PHASE_1": "Phase 1",
        "PHASE_2": "Phase 2",
        "PHASE_3": "Phase 3",
        "PHASE_3_4_5": "Phase 3-4-5",
        "PHASE_4": "Phase 4",
        "PHASE_5": "Phase 5",
        "PHASE_6": "Phase 6",
        "PHASE_7": "Phase 7",
        "PHASE_8": "Phase 8",
        "PHASE_9": "Phase 9",
        "PHASE_9_16": "Phase 9-16",
        "PHASE_10": "Phase 10",
        "PHASE_11_12": "Phase 11-12",
        "PHASE_13_14": "Phase 13-14",
        "PHASE_15_16": "Phase 15-16",
        "PHASE_17_18": "Phase 17-18",
        "PHASE_17_24": "Phase 17-24",
        "PHASE_25_30": "Phase 25-30",
        "EXPECTED_OUTPUT": "Expected Output",
    }},
}

def extract_title_and_description(content: str) -> Tuple[str, str]:
    """Extract title and description from markdown content."""
    lines = content.split('\n')
    
    # Find title (first # heading or first line)
    title = ""
    description = ""
    
    for i, line in enumerate(lines[:20]):  # Check first 20 lines
        line = line.strip()
        
        # Title from first # heading
        if line.startswith('# ') and not title:
            title = line[2:].strip()
            # Description might be in next non-empty line
            for j in range(i + 1, min(i + 5, len(lines))):
                desc_line = lines[j].strip()
                if desc_line and not desc_line.startswith('#') and not desc_line.startswith('---'):
                    description = desc_line[:200]
                    break
            break
        
        # Description from first paragraph
        if not title and line and not line.startswith('#') and not line.startswith('---') and not line.startswith('**'):
            if not description:
                description = line[:200]
    
    # Fallback title
    if not title:
        title = lines[0].strip().lstrip('#').strip() or "Documentation"
    
    # Fallback description
    if not description:
        description = "Documentation file"
    
    return title, description

def detect_language(content: str) -> str:
    """Detect document language."""
    # Simple heuristic: check for Arabic characters
    if re.search(r'[\u0600-\u06FF]', content[:500]):
        return "ar"
    elif re.search(r'[A-Za-z]', content[:500]):
        return "en"
    return "both"

def generate_tags(file_path: str, category: str, subcategory: str) -> List[str]:
    """Generate tags based on file path and category."""
    tags = []
    filename_lower = Path(file_path).stem.lower()
    
    # Category tags
    tags.append(category.lower())
    if subcategory:
        tags.append(subcategory.lower().replace(" ", "-"))
    
    # Filename-based tags
    if "test" in filename_lower:
        tags.extend(["testing", "test"])
    if "guide" in filename_lower:
        tags.append("guide")
    if "checklist" in filename_lower:
        tags.append("checklist")
    if "phase" in filename_lower:
        tags.append("phase")
        # Extract phase number
        phase_match = re.search(r'phase[_\s]?(\d+)', filename_lower)
        if phase_match:
            tags.append(f"phase-{phase_match.group(1)}")
    if "user" in filename_lower:
        tags.append("user-guide")
    if "admin" in filename_lower:
        tags.append("admin")
    if "command" in filename_lower:
        tags.append("commands")
    if "deployment" in filename_lower:
        tags.append("deployment")
    if "implementation" in filename_lower:
        tags.append("implementation")
    
    return list(set(tags))  # Remove duplicates

def get_roles(category: str, filename: str) -> Dict[str, List[str]]:
    """Determine roles based on category and filename."""
    filename_lower = filename.lower()
    
    role_map = {
        "Core": {
            "primary": ["Project Manager", "CTO / Technical Lead"],
            "secondary": ["All"]
        },
        "Design": {
            "primary": ["UI/UX Designer", "CTO / Technical Lead"],
            "secondary": ["Developer"]
        },
        "Testing": {
            "primary": ["QA / Tester"],
            "secondary": ["Developer"]
        },
        "Deployment": {
            "primary": ["DevOps"],
            "secondary": ["Developer"]
        },
        "Development": {
            "primary": ["Developer"],
            "secondary": ["Technical Lead"]
        },
        "Planning": {
            "primary": ["Project Manager", "Business Analyst"],
            "secondary": ["CTO / Technical Lead"]
        },
        "Tracking": {
            "primary": ["Project Manager"],
            "secondary": ["Developer", "QA / Tester"]
        },
        "Commands": {
            "primary": ["Developer"],
            "secondary": ["QA / Tester"]
        },
        "Phases": {
            "primary": ["Project Manager"],
            "secondary": ["Technical Lead"]
        },
    }
    
    return role_map.get(category, {
        "primary": ["All"],
        "secondary": []
    })

def get_phases(category: str, filename: str) -> Dict[str, List[str]]:
    """Determine applicable phases."""
    filename_lower = filename.lower()
    
    phase_map = {
        "Testing": {
            "primary": ["Testing", "QA"],
            "secondary": ["Development"]
        },
        "Development": {
            "primary": ["Development"],
            "secondary": ["Planning", "Testing"]
        },
        "Planning": {
            "primary": ["Planning", "Business Gathering"],
            "secondary": ["Development"]
        },
        "Deployment": {
            "primary": ["Deployment"],
            "secondary": ["Development", "QA"]
        },
    }
    
    if "test" in filename_lower:
        return {
            "primary": ["Testing", "QA"],
            "secondary": ["Development"]
        }
    
    return phase_map.get(category, {
        "primary": ["Development"],
        "secondary": []
    })

def generate_metadata(file_path: Path, content: str, target_path: str) -> str:
    """Generate YAML frontmatter metadata."""
    # Parse target path
    parts = target_path.split('/')
    category_key = parts[0]  # e.g., "01_CORE"
    subcategory_key = None
    
    if len(parts) > 2:
        subcategory_key = parts[1]  # e.g., "STATUS"
    
    category_info = CATEGORY_MAP.get(category_key, {})
    category = category_info.get("category", "Core")
    subcategory = None
    
    if subcategory_key:
        subcategories = category_info.get("subcategories", {})
        subcategory = subcategories.get(subcategory_key, None)
    
    # Extract info from content
    title, description = extract_title_and_description(content)
    language = detect_language(content)
    tags = generate_tags(str(file_path), category, subcategory or "")
    roles = get_roles(category, file_path.name)
    phases = get_phases(category, file_path.name)
    
    # Generate metadata
    metadata = f"""---
title: "{title}"
description: "{description}"

category: "{category}"
"""
    
    if subcategory:
        metadata += f'subcategory: "{subcategory}"\n'
    
    metadata += f"""language: "{language}"
original_language: "{language}"

purpose: |
  Documentation file for {category.lower()} category.

target_audience:
  primary:
"""
    
    for role in roles["primary"]:
        metadata += f"    - {role}\n"
    
    if roles["secondary"]:
        metadata += "  secondary:\n"
        for role in roles["secondary"]:
            metadata += f"    - {role}\n"
    
    metadata += """
applicable_phases:
  primary:
"""
    
    for phase in phases["primary"]:
        metadata += f"    - {phase}\n"
    
    if phases["secondary"]:
        metadata += "  secondary:\n"
        for phase in phases["secondary"]:
            metadata += f"    - {phase}\n"
    
    metadata += "\ntags:\n"
    for tag in tags[:15]:  # Limit to 15 tags
        metadata += f"  - {tag}\n"
    
    metadata += f"""
status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"

estimated_read_time: "10 minutes"

version: "1.0"
last_updated: "{datetime.now().strftime('%Y-%m-%d')}"
last_reviewed: "{datetime.now().strftime('%Y-%m-%d')}"
review_frequency: "quarterly"

author: "Development Team"
maintainer: "Development Team"

related: []
see_also: []
depends_on: []
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "{datetime.now().strftime('%Y-%m-%d')}"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---
"""
    
    return metadata

def has_metadata(content: str) -> bool:
    """Check if content already has YAML frontmatter."""
    return content.startswith('---\n')

def process_file(source_path: Path, target_path: Path):
    """Process a single file: copy and add metadata."""
    try:
        # Read source file
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if metadata already exists
        if has_metadata(content):
            # Keep existing metadata, just copy
            new_content = content
        else:
            # Generate and prepend metadata
            metadata = generate_metadata(source_path, content, str(target_path.relative_to(TARGET_DIR)))
            new_content = metadata + '\n' + content
        
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to target
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, None
    except Exception as e:
        return False, str(e)

def process_directory(source_dir: Path, target_dir: Path, mapping: Dict[str, str]):
    """Process all markdown files in source directory."""
    stats = {
        "processed": 0,
        "skipped": 0,
        "errors": 0,
        "errors_list": []
    }
    
    # Process mapped files
    for rel_path, target_rel_path in mapping.items():
        source_path = source_dir / rel_path
        target_path = target_dir / target_rel_path
        
        if not source_path.exists():
            print(f"⚠️  Skipping (not found): {rel_path}")
            stats["skipped"] += 1
            continue
        
        if source_path.is_file():
            success, error = process_file(source_path, target_path)
            if success:
                print(f"✅ Processed: {rel_path} → {target_rel_path}")
                stats["processed"] += 1
            else:
                print(f"❌ Error processing {rel_path}: {error}")
                stats["errors"] += 1
                stats["errors_list"].append((rel_path, error))
    
    # Process manual test checklists
    manual_test_dir = source_dir / "testing" / "manual_test_checklist"
    if manual_test_dir.exists():
        target_manual_dir = target_dir / "03_TESTING" / "MANUAL_TEST_CHECKLISTS"
        for file in manual_test_dir.glob("*.md"):
            if file.name != "README.md":
                target_path = target_manual_dir / file.name
                success, error = process_file(file, target_path)
                if success:
                    print(f"✅ Processed: {file.relative_to(source_dir)} → {target_path.relative_to(target_dir)}")
                    stats["processed"] += 1
                else:
                    print(f"❌ Error: {error}")
                    stats["errors"] += 1
    
    # Process tracking files
    tracking_dir = source_dir / "tracking"
    if tracking_dir.exists():
        # Process phase_*_detailed.md files - go to 09_PHASES
        for file in tracking_dir.glob("phase_*_detailed.md"):
            filename_lower = file.name.lower()
            
            # Map phase numbers to directories
            phase_mapping = {
                "phase_0_detailed.md": "09_PHASES/PHASE_0/phase_0_detailed.md",
                "phase_1_detailed.md": "09_PHASES/PHASE_1/phase_1_detailed.md",
                "phase_2_detailed.md": "09_PHASES/PHASE_2/phase_2_detailed.md",
                "phase_3_4_5_detailed.md": "09_PHASES/PHASE_3_4_5/phase_3_4_5_detailed.md",
                "phase_6_detailed.md": "09_PHASES/PHASE_6/phase_6_detailed.md",
                "phase_7_detailed.md": "09_PHASES/PHASE_7/phase_7_detailed.md",
                "phase_8_detailed.md": "09_PHASES/PHASE_8/phase_8_detailed.md",
                "phase_9_16_frontend_detailed.md": "09_PHASES/PHASE_9_16/phase_9_16_frontend_detailed.md",
                "phase_17_24_advanced_detailed.md": "09_PHASES/PHASE_17_24/phase_17_24_advanced_detailed.md",
                "phase_25_30_launch_detailed.md": "09_PHASES/PHASE_25_30/phase_25_30_launch_detailed.md",
            }
            
            target_rel_path = phase_mapping.get(file.name)
            if target_rel_path:
                target_path = target_dir / target_rel_path
                success, error = process_file(file, target_path)
                if success:
                    print(f"✅ Processed: {file.relative_to(source_dir)} → {target_path.relative_to(target_dir)}")
                    stats["processed"] += 1
                else:
                    print(f"❌ Error: {error}")
                    stats["errors"] += 1
        
        # Process expected_output/phase_*_expected.md files - go to 09_PHASES
        expected_output_dir = tracking_dir / "expected_output"
        if expected_output_dir.exists():
            for file in expected_output_dir.glob("phase_*_expected.md"):
                filename_lower = file.name.lower()
                
                # Map phase numbers to directories
                expected_mapping = {
                    "phase_0_expected.md": "09_PHASES/PHASE_0/EXPECTED_OUTPUT/phase_0_expected.md",
                    "phase_1_expected.md": "09_PHASES/PHASE_1/EXPECTED_OUTPUT/phase_1_expected.md",
                    "phase_2_expected.md": "09_PHASES/PHASE_2/EXPECTED_OUTPUT/phase_2_expected.md",
                    "phase_3_4_5_expected.md": "09_PHASES/PHASE_3_4_5/EXPECTED_OUTPUT/phase_3_4_5_expected.md",
                    "phase_6_expected.md": "09_PHASES/PHASE_6/EXPECTED_OUTPUT/phase_6_expected.md",
                    "phase_7_expected.md": "09_PHASES/PHASE_7/EXPECTED_OUTPUT/phase_7_expected.md",
                    "phase_8_expected.md": "09_PHASES/PHASE_8/EXPECTED_OUTPUT/phase_8_expected.md",
                    "phase_9_expected.md": "09_PHASES/PHASE_9/EXPECTED_OUTPUT/phase_9_expected.md",
                    "phase_10_expected.md": "09_PHASES/PHASE_10/EXPECTED_OUTPUT/phase_10_expected.md",
                    "phase_11_expected.md": "09_PHASES/PHASE_11_12/EXPECTED_OUTPUT/phase_11_expected.md",
                    "phase_12_expected.md": "09_PHASES/PHASE_11_12/EXPECTED_OUTPUT/phase_12_expected.md",
                    "phase_13_14_expected.md": "09_PHASES/PHASE_13_14/EXPECTED_OUTPUT/phase_13_14_expected.md",
                    "phase_15_16_expected.md": "09_PHASES/PHASE_15_16/EXPECTED_OUTPUT/phase_15_16_expected.md",
                    "phase_17_18_expected.md": "09_PHASES/PHASE_17_18/EXPECTED_OUTPUT/phase_17_18_expected.md",
                }
                
                target_rel_path = expected_mapping.get(file.name)
                if target_rel_path:
                    target_path = target_dir / target_rel_path
                    success, error = process_file(file, target_path)
                    if success:
                        print(f"✅ Processed: {file.relative_to(source_dir)} → {target_path.relative_to(target_dir)}")
                        stats["processed"] += 1
                    else:
                        print(f"❌ Error: {error}")
                        stats["errors"] += 1
        
        # Map other tracking files to 07_TRACKING
        for file in tracking_dir.glob("*.md"):
            if file.name == "README.md":
                continue
            
            filename_lower = file.name.lower()
            
            # Check if it's already processed (PHASE_* files mapped in FILE_MAPPING or phase_*_detailed.md)
            if (filename_lower.startswith("phase_") and (
                "implementation_plan" in filename_lower or
                "audit" in filename_lower or
                "completion" in filename_lower or
                "verification" in filename_lower or
                "detailed" in filename_lower or
                filename_lower.startswith("phase_9") or
                filename_lower.startswith("phase_10") or
                filename_lower.startswith("phase_11") or
                filename_lower.startswith("phase_13") or
                filename_lower.startswith("phase_15") or
                filename_lower.startswith("phase_17")
            )) or filename_lower.startswith("phase_") and "_detailed" in filename_lower:
                # These go to 09_PHASES (already mapped or processed above)
                continue
            # Determine subcategory for other tracking files
            elif "bug" in filename_lower or "fix" in filename_lower or "websocket" in filename_lower:
                target_path = target_dir / "07_TRACKING" / "BUGS_FIXES" / file.name
            elif "implementation" in filename_lower or "plan" in filename_lower:
                target_path = target_dir / "07_TRACKING" / "IMPLEMENTATION" / file.name
            elif "status" in filename_lower or "roadmap" in filename_lower or "next" in filename_lower:
                target_path = target_dir / "07_TRACKING" / "STATUS" / file.name
            else:
                target_path = target_dir / "07_TRACKING" / file.name
            
            success, error = process_file(file, target_path)
            if success:
                print(f"✅ Processed: {file.relative_to(source_dir)} → {target_path.relative_to(target_dir)}")
                stats["processed"] += 1
            else:
                print(f"❌ Error: {error}")
                stats["errors"] += 1
    
    return stats

def main():
    """Main function."""
    print("🚀 Starting documentation reorganization...")
    print(f"📂 Source: {SOURCE_DIR}")
    print(f"📂 Target: {TARGET_DIR}")
    print()
    
    if not SOURCE_DIR.exists():
        print(f"❌ Source directory not found: {SOURCE_DIR}")
        return
    
    # Process files
    stats = process_directory(SOURCE_DIR, TARGET_DIR, FILE_MAPPING)
    
    # Print summary
    print()
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"✅ Processed: {stats['processed']} files")
    print(f"⚠️  Skipped: {stats['skipped']} files")
    print(f"❌ Errors: {stats['errors']} files")
    
    if stats['errors_list']:
        print("\n❌ Error Details:")
        for file, error in stats['errors_list']:
            print(f"  - {file}: {error}")
    
    print()
    print("✨ Reorganization complete!")

if __name__ == "__main__":
    main()

