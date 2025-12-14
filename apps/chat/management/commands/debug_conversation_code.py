"""
Management command to debug code extraction for a specific conversation.

Usage:
    python manage.py debug_conversation_code <conversation_id>
    python manage.py debug_conversation_code --latest
"""

from django.core.management.base import BaseCommand
from apps.chat.models import Conversation, Message
from apps.chat.services.code_context_extractor import CodeContextExtractor


class Command(BaseCommand):
    help = 'Debug code extraction for a conversation'

    def add_arguments(self, parser):
        parser.add_argument(
            'conversation_id',
            nargs='?',
            type=str,
            help='Conversation ID to debug (or use --latest for most recent)'
        )
        parser.add_argument(
            '--latest',
            action='store_true',
            help='Use the most recent conversation'
        )

    def handle(self, *args, **options):
        # Get conversation
        if options['latest']:
            conversation = Conversation.objects.order_by('-created_at').first()
            if not conversation:
                self.stdout.write(self.style.ERROR('No conversations found'))
                return
        else:
            conv_id = options.get('conversation_id')
            if not conv_id:
                self.stdout.write(self.style.ERROR('Please provide conversation_id or use --latest'))
                return
            try:
                conversation = Conversation.objects.get(id=conv_id)
            except Conversation.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Conversation {conv_id} not found'))
                return

        self.stdout.write("=" * 70)
        self.stdout.write(f"Debugging Conversation: {conversation.title}")
        self.stdout.write(f"ID: {conversation.id}")
        self.stdout.write("=" * 70)

        # Check current state
        self.stdout.write("\n📊 Current Code Context State:")
        self.stdout.write(f"  Referenced Files: {conversation.referenced_files or []}")
        self.stdout.write(f"  Code Blocks Count: {len(conversation.referenced_code_blocks or [])}")
        self.stdout.write(f"  Metadata: {conversation.code_context_metadata}")

        # Analyze all messages
        messages = conversation.messages.all().order_by('created_at')
        self.stdout.write(f"\n📝 Analyzing {messages.count()} Messages:")
        self.stdout.write("-" * 70)

        total_blocks_found = 0
        total_files_found = 0

        for i, message in enumerate(messages, 1):
            self.stdout.write(f"\nMessage {i} ({message.role}):")
            content_preview = message.content[:100].replace('\n', '\\n')
            self.stdout.write(f"  Content preview: {content_preview}...")
            
            # Test extraction
            code_blocks = CodeContextExtractor.extract_code_blocks(message.content)
            file_refs = CodeContextExtractor.extract_file_references(message.content)
            
            if code_blocks:
                self.stdout.write(self.style.SUCCESS(f"  ✅ Found {len(code_blocks)} code block(s):"))
                for j, block in enumerate(code_blocks, 1):
                    self.stdout.write(f"    Block {j}: {block.get('language')} ({block.get('tokens')} tokens)")
                    self.stdout.write(f"      Preview: {block.get('content')[:60]}...")
                total_blocks_found += len(code_blocks)
            else:
                # Check if there's a code block pattern that didn't match
                if '```' in message.content:
                    self.stdout.write(self.style.WARNING("  ⚠️  Found ``` but extraction failed!"))
                    # Try to find why
                    import re
                    matches = re.findall(r'```.*?```', message.content, re.DOTALL)
                    if matches:
                        self.stdout.write(f"    Found code block patterns: {len(matches)}")
                        for match in matches[:2]:  # Show first 2
                            self.stdout.write(f"      Pattern: {match[:80]}...")
            
            if file_refs:
                self.stdout.write(self.style.SUCCESS(f"  ✅ Found {len(file_refs)} file reference(s):"))
                for ref in file_refs:
                    self.stdout.write(f"    - {ref}")
                total_files_found += len(file_refs)

        # Summary
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("📈 Summary:")
        self.stdout.write(f"  Total messages analyzed: {messages.count()}")
        self.stdout.write(f"  Code blocks found: {total_blocks_found}")
        self.stdout.write(f"  File references found: {total_files_found}")
        self.stdout.write(f"  Currently stored blocks: {len(conversation.referenced_code_blocks or [])}")
        self.stdout.write(f"  Currently stored files: {len(conversation.referenced_files or [])}")

        # Recommendation
        if total_blocks_found > 0 and len(conversation.referenced_code_blocks or []) == 0:
            self.stdout.write("\n⚠️  ISSUE DETECTED:")
            self.stdout.write("  Code blocks were found in messages but not stored in conversation!")
            self.stdout.write("  This means extraction is working but saving is not.")
            self.stdout.write("\n  To fix, re-run extraction:")
            self.stdout.write(f"  python manage.py re_extract_code_context {conversation.id}")

        self.stdout.write("=" * 70)

