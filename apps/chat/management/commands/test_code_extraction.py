"""
Management command to test code extraction from a sample message.

Usage:
    python manage.py test_code_extraction
"""

from django.core.management.base import BaseCommand
from apps.chat.services.code_context_extractor import CodeContextExtractor


class Command(BaseCommand):
    help = 'Test code extraction from sample messages'

    def handle(self, *args, **options):
        self.stdout.write("Testing Code Extraction...\n")
        
        # Test case 1: Properly formatted markdown code block
        test_message_1 = """I'm working on a Python project. Here's my user model:

```python
class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
```
"""
        
        self.stdout.write("=" * 70)
        self.stdout.write("Test 1: Markdown Code Block")
        self.stdout.write("=" * 70)
        self.stdout.write(f"Input: {test_message_1[:100]}...\n")
        
        code_blocks_1 = CodeContextExtractor.extract_code_blocks(test_message_1)
        file_refs_1 = CodeContextExtractor.extract_file_references(test_message_1)
        
        self.stdout.write(f"Code blocks extracted: {len(code_blocks_1)}")
        if code_blocks_1:
            for i, block in enumerate(code_blocks_1, 1):
                self.stdout.write(f"  Block {i}:")
                self.stdout.write(f"    Language: {block.get('language')}")
                self.stdout.write(f"    Content preview: {block.get('content')[:50]}...")
                self.stdout.write(f"    Tokens: {block.get('tokens')}")
        else:
            self.stdout.write(self.style.WARNING("  ❌ No code blocks extracted!"))
        
        self.stdout.write(f"\nFile references extracted: {len(file_refs_1)}")
        if file_refs_1:
            for ref in file_refs_1:
                self.stdout.write(f"  - {ref}")
        
        # Test case 2: Code block without language
        test_message_2 = """Here's some code:

```
def hello():
    print("Hello")
```
"""
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("Test 2: Code Block Without Language")
        self.stdout.write("=" * 70)
        
        code_blocks_2 = CodeContextExtractor.extract_code_blocks(test_message_2)
        self.stdout.write(f"Code blocks extracted: {len(code_blocks_2)}")
        if code_blocks_2:
            for block in code_blocks_2:
                self.stdout.write(f"  Language: {block.get('language')}")
        
        # Test case 3: File references
        test_message_3 = """I'm working on:
- backend/apps/auth/models.py
- frontend/src/components/Login.tsx
"""
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("Test 3: File References")
        self.stdout.write("=" * 70)
        
        file_refs_3 = CodeContextExtractor.extract_file_references(test_message_3)
        self.stdout.write(f"File references extracted: {len(file_refs_3)}")
        for ref in file_refs_3:
            self.stdout.write(f"  - {ref}")
        
        # Test case 4: Mixed content
        test_message_4 = """Check my code in app/models.py:

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
```
"""
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("Test 4: Mixed (Code + File Reference)")
        self.stdout.write("=" * 70)
        
        code_blocks_4 = CodeContextExtractor.extract_code_blocks(test_message_4)
        file_refs_4 = CodeContextExtractor.extract_file_references(test_message_4)
        
        self.stdout.write(f"Code blocks: {len(code_blocks_4)}")
        self.stdout.write(f"File references: {len(file_refs_4)}")
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("✅ Testing Complete!"))
        self.stdout.write("=" * 70)

