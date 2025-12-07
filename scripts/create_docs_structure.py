#!/usr/bin/env python3
"""
Script to create the new documentation structure.
"""
import os
from pathlib import Path

# Base directory
base_dir = Path("docs")

# Main directories
main_dirs = [
    "01_CORE",
    "02_DESIGN",
    "03_TESTING",
    "04_DEPLOYMENT",
    "05_DEVELOPMENT",
    "06_PLANNING",
    "07_TRACKING",
    "08_COMMANDS",
    "09_PHASES",
]

# Subdirectories
subdirs = {
    "01_CORE": [
        "INDEXES",
        "STATUS",
        "USER_GUIDES",
        "ADMIN",
        "SUMMARIES",
    ],
    "02_DESIGN": [
        "ARCHITECTURE",
        "UI",
        "GAPS",
        "ROADMAP",
        "PROMPTS",
    ],
    "03_TESTING": [
        "MANUAL_TEST_CHECKLISTS",
        "IMPLEMENTATION",
    ],
    "06_PLANNING": [
        "PROJECT_PLANS",
        "IMPLEMENTATION",
    ],
    "07_TRACKING": [
        "STATUS",
        "IMPLEMENTATION",
        "BUGS_FIXES",
        "PHASES",
    ],
    "09_PHASES": [
        "PHASE_3",
        "PHASE_4",
        "PHASE_5",
        "PHASE_6",
        "PHASE_9",
    ],
}

def create_structure():
    """Create the documentation structure."""
    print("Creating documentation structure...")
    
    # Create base directory
    base_dir.mkdir(exist_ok=True)
    print(f"✓ Created {base_dir}/")
    
    # Create main directories
    for main_dir in main_dirs:
        dir_path = base_dir / main_dir
        dir_path.mkdir(exist_ok=True)
        print(f"✓ Created {dir_path}/")
    
    # Create subdirectories
    for main_dir, subs in subdirs.items():
        for sub_dir in subs:
            dir_path = base_dir / main_dir / sub_dir
            dir_path.mkdir(exist_ok=True)
            print(f"✓ Created {dir_path}/")
    
    print("\n✅ Structure created successfully!")

if __name__ == "__main__":
    create_structure()

