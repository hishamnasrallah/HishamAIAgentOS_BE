"""
Prepare fixtures for deployment - removes user conflicts and cleans references.
This script processes existing fixtures to make them ready for direct loading.
"""

import sys
import os
import json
import django
from pathlib import Path
from typing import Dict, List, Any, Set

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.authentication.models import User


class FixturePreparer:
    """Prepare fixtures for safe deployment."""
    
    # Fields that reference users (field_name: can_be_null)
    USER_REFERENCE_FIELDS = {
        'owner': True,
        'owner_id': True,
        'created_by': True,
        'created_by_id': True,
        'assigned_to': True,
        'assigned_to_id': True,
        'user': True,
        'user_id': True,
        'members': True,  # ManyToMany - will be set to empty list
    }
    
    # Models that require user field (cannot be null) - these records will be excluded
    MODELS_REQUIRING_USER = {
        'chat.conversation',  # user field is required (NOT NULL)
    }
    
    # Models that depend on excluded models - these will also be excluded
    # Format: {model_name: [list of foreign key fields that point to excluded models]}
    DEPENDENT_MODELS = {
        'chat.message': ['conversation', 'conversation_id'],  # Depends on Conversation
    }
    
    def __init__(self, source_dir: Path, output_dir: Path):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Track excluded primary keys by model to filter dependent records
        self.excluded_pks: Dict[str, Set[str]] = {}
        self.stats = {
            'files_processed': 0,
            'records_processed': 0,
            'user_references_cleaned': 0,
            'files_skipped': 0,
            'records_excluded': 0,  # Records excluded because they require user
        }
    
    def prepare_all(self) -> Dict[str, Any]:
        """Prepare all fixtures in source directory."""
        print("=" * 70)
        print("  HISHAMOS - PREPARE FIXTURES FOR DEPLOYMENT")
        print("=" * 70)
        print()
        print(f"Source: {self.source_dir}")
        print(f"Output: {self.output_dir}")
        print()
        
        # Get all JSON fixture files
        fixture_files = list(self.source_dir.glob("*.json"))
        
        if not fixture_files:
            print(f"❌ No fixture files found in {self.source_dir}")
            return self.stats
        
        # Process each fixture file
        for fixture_file in sorted(fixture_files):
            self._process_fixture_file(fixture_file)
        
        # Print summary
        print()
        print("=" * 70)
        print("  SUMMARY")
        print("=" * 70)
        print(f"✅ Files processed: {self.stats['files_processed']}")
        print(f"📦 Records processed: {self.stats['records_processed']}")
        print(f"🧹 User references cleaned: {self.stats['user_references_cleaned']}")
        if self.stats['records_excluded'] > 0:
            print(f"🚫 Records excluded: {self.stats['records_excluded']} (require user or depend on excluded records)")
        print(f"⏭️  Files skipped: {self.stats['files_skipped']}")
        print(f"💾 Output directory: {self.output_dir.absolute()}")
        print("=" * 70)
        print()
        print("✅ Fixtures are now ready for deployment!")
        print("   You can load them using:")
        print(f"   python manage.py loaddata {self.output_dir}/*.json")
        print()
        
        return self.stats
    
    def _process_fixture_file(self, fixture_file: Path):
        """Process a single fixture file."""
        file_name = fixture_file.name
        
        # Skip authentication.json - we don't want user data in deployment fixtures
        if file_name == 'authentication.json':
            print(f"⏭️  {file_name}: Skipped (user data excluded)")
            self.stats['files_skipped'] += 1
            return
        
        print(f"📥 Processing {file_name}...", end=' ')
        
        try:
            # Read fixture file
            with open(fixture_file, 'r', encoding='utf-8') as f:
                fixture_data = json.load(f)
            
            if not isinstance(fixture_data, list):
                print(f"❌ Invalid format (expected list)")
                return
            
            # Process records in two passes:
            # Pass 1: Identify and track excluded records that require user
            # Pass 2: Exclude dependent records and clean remaining records
            
            # Pass 1: Identify excluded records (for tracking)
            file_excluded_pks = {}  # Track excluded PKs in this file only
            for record in fixture_data:
                model_key = f"{record.get('model', '')}"
                if model_key in self.MODELS_REQUIRING_USER:
                    fields = record.get('fields', {})
                    has_user_ref = any(
                        field_name in fields and fields[field_name] is not None
                        for field_name in ['user', 'user_id']
                    )
                    if has_user_ref:
                        record_pk = record.get('pk')
                        # Track excluded PK for dependent models in this file
                        if model_key not in file_excluded_pks:
                            file_excluded_pks[model_key] = set()
                        if record_pk:
                            file_excluded_pks[model_key].add(str(record_pk))
            
            # Pass 2: Process all records
            cleaned_data = []
            user_refs_cleaned = 0
            records_excluded = 0
            
            for record in fixture_data:
                model_key = f"{record.get('model', '')}"
                fields = record.get('fields', {})
                record_pk = record.get('pk')
                
                # Check if this model requires user and record has user reference
                if model_key in self.MODELS_REQUIRING_USER:
                    has_user_ref = any(
                        field_name in fields and fields[field_name] is not None
                        for field_name in ['user', 'user_id']
                    )
                    if has_user_ref:
                        # Exclude this record - it requires user but we can't provide one
                        records_excluded += 1
                        continue
                
                # Check if this record depends on an excluded model
                if model_key in self.DEPENDENT_MODELS:
                    fk_fields = self.DEPENDENT_MODELS[model_key]
                    should_exclude = False
                    
                    for fk_field in fk_fields:
                        fk_value = fields.get(fk_field)
                        if fk_value:
                            # Check if this FK points to an excluded record in this file
                            for excluded_model, excluded_pks_set in file_excluded_pks.items():
                                if str(fk_value) in excluded_pks_set:
                                    should_exclude = True
                                    break
                            if should_exclude:
                                break
                    
                    if should_exclude:
                        records_excluded += 1
                        continue
                
                cleaned_record = self._clean_record(record)
                if cleaned_record:
                    cleaned_data.append(cleaned_record)
                    # Count cleaned user references
                    user_refs_cleaned += self._count_cleaned_references(record, cleaned_record)
            
            # Save cleaned fixture
            output_file = self.output_dir / file_name
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
            
            self.stats['files_processed'] += 1
            self.stats['records_processed'] += len(cleaned_data)
            self.stats['user_references_cleaned'] += user_refs_cleaned
            self.stats['records_excluded'] += records_excluded
            
            status_msg = f"✅ ({len(cleaned_data)} records"
            if user_refs_cleaned > 0:
                status_msg += f", {user_refs_cleaned} user refs cleaned"
            if records_excluded > 0:
                status_msg += f", {records_excluded} excluded (require user)"
            status_msg += ")"
            print(status_msg)
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a single fixture record."""
        if not isinstance(record, dict) or 'fields' not in record:
            return record
        
        cleaned_record = record.copy()
        cleaned_fields = cleaned_record['fields'].copy()
        
        # Clean user references
        for field_name, can_be_null in self.USER_REFERENCE_FIELDS.items():
            if field_name in cleaned_fields:
                if field_name == 'members':
                    # ManyToMany - set to empty list
                    cleaned_fields[field_name] = []
                elif can_be_null:
                    # ForeignKey - set to null
                    cleaned_fields[field_name] = None
                # If can't be null, leave as is (shouldn't happen for user refs)
        
        cleaned_record['fields'] = cleaned_fields
        return cleaned_record
    
    def _count_cleaned_references(self, original: Dict[str, Any], cleaned: Dict[str, Any]) -> int:
        """Count how many user references were cleaned."""
        count = 0
        
        if 'fields' not in original or 'fields' not in cleaned:
            return 0
        
        original_fields = original['fields']
        cleaned_fields = cleaned['fields']
        
        for field_name in self.USER_REFERENCE_FIELDS.keys():
            if field_name in original_fields:
                original_value = original_fields[field_name]
                cleaned_value = cleaned_fields[field_name]
                
                # Count if value was changed
                if field_name == 'members':
                    if original_value and len(original_value) > 0 and cleaned_value == []:
                        count += 1
                else:
                    if original_value is not None and cleaned_value is None:
                        count += 1
        
        return count


def main():
    """Main entry point."""
    # Default paths
    source_dir = backend_dir / 'initial_data' / 'fixtures'
    output_dir = backend_dir / 'initial_data' / 'fixtures' / 'deployment'
    
    # Check if source directory exists
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        print("   Please run 'python manage.py export_initial_data' first")
        sys.exit(1)
    
    # Create preparer and process
    preparer = FixturePreparer(source_dir, output_dir)
    stats = preparer.prepare_all()
    
    if stats['files_processed'] == 0:
        print("⚠️  No files were processed. Check source directory.")
        sys.exit(1)


if __name__ == '__main__':
    main()

