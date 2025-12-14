"""
Management command to update language detection for existing code blocks.

This command re-runs language inference on existing code blocks to fix
language detection issues (e.g., blocks marked as 'text' that should be 'python').

Usage:
    python manage.py update_code_block_languages <conversation_id>
    python manage.py update_code_block_languages --all
"""

from django.core.management.base import BaseCommand
from apps.chat.models import Conversation
from apps.chat.services.code_context_extractor import CodeContextExtractor
from django.utils import timezone


class Command(BaseCommand):
    help = 'Update language detection for existing code blocks'

    def add_arguments(self, parser):
        parser.add_argument(
            'conversation_id',
            nargs='?',
            type=str,
            help='Conversation ID (or use --all for all conversations)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all conversations'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )

    def handle(self, *args, **options):
        if options['all']:
            conversations = Conversation.objects.exclude(referenced_code_blocks__isnull=True).exclude(referenced_code_blocks=[])
            self.stdout.write(f"Processing {conversations.count()} conversations with code blocks...\n")
        else:
            conv_id = options.get('conversation_id')
            if not conv_id:
                self.stdout.write(self.style.ERROR('Please provide conversation_id or use --all'))
                return
            try:
                conversations = [Conversation.objects.get(id=conv_id)]
            except Conversation.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Conversation {conv_id} not found'))
                return

        dry_run = options.get('dry_run', False)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved\n'))

        total_updated = 0
        total_fixed = 0
        total_blocks_processed = 0

        for conversation in conversations:
            code_blocks = conversation.referenced_code_blocks or []
            if not code_blocks:
                continue

            self.stdout.write(f"\nProcessing: {conversation.title} ({conversation.id})")
            self.stdout.write(f"  Found {len(code_blocks)} code blocks")

            updated_blocks = []
            fixed_count = 0

            for block in code_blocks:
                total_blocks_processed += 1
                original_language = block.get('language', 'text')
                code_content = block.get('content', '')

                if not code_content:
                    # Keep block as-is if no content
                    updated_blocks.append(block)
                    continue

                # Re-run language inference
                inferred_language = CodeContextExtractor._infer_language(code_content)
                
                # Update language if it changed
                if inferred_language != original_language:
                    block['language'] = inferred_language
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✅ Fixed: {original_language} → {inferred_language}"
                        )
                    )
                    if code_content:
                        preview = code_content[:60].replace('\n', ' ')
                        self.stdout.write(f"     Preview: {preview}...")

                updated_blocks.append(block)

            if fixed_count > 0:
                total_fixed += fixed_count
                
                if not dry_run:
                    # Update metadata
                    metadata = conversation.code_context_metadata or {}
                    metadata.update({
                        'last_updated': timezone.now().isoformat(),
                        'language_updated_at': timezone.now().isoformat()
                    })
                    
                    # Save updated blocks
                    conversation.referenced_code_blocks = updated_blocks
                    conversation.code_context_metadata = metadata
                    conversation.save(update_fields=['referenced_code_blocks', 'code_context_metadata'])
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  💾 Saved {fixed_count} language updates"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  [DRY RUN] Would update {fixed_count} blocks"
                        )
                    )
            else:
                self.stdout.write("  ✓ No language updates needed")

            total_updated += 1

        self.stdout.write("\n" + "=" * 70)
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN COMPLETE - No changes were saved"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ Language Update Complete!"))
        self.stdout.write(f"  Conversations processed: {total_updated}")
        self.stdout.write(f"  Total blocks processed: {total_blocks_processed}")
        self.stdout.write(f"  Language fixes applied: {total_fixed}")
        self.stdout.write("=" * 70)

