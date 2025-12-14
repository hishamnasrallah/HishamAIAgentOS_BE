"""
Management command to re-extract code context from all messages in a conversation.

Usage:
    python manage.py re_extract_code_context <conversation_id>
    python manage.py re_extract_code_context --all
"""

from django.core.management.base import BaseCommand
from apps.chat.models import Conversation, Message
from apps.chat.services.code_context_extractor import CodeContextExtractor
from django.utils import timezone


class Command(BaseCommand):
    help = 'Re-extract code context from conversation messages'

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

    def handle(self, *args, **options):
        if options['all']:
            conversations = Conversation.objects.all()
            self.stdout.write(f"Processing {conversations.count()} conversations...\n")
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

        total_processed = 0
        total_blocks = 0
        total_files = 0

        for conversation in conversations:
            self.stdout.write(f"\nProcessing: {conversation.title} ({conversation.id})")
            
            # Collect all code blocks and file references from all messages
            all_code_blocks = []
            all_file_refs = set()
            
            messages = conversation.messages.all().order_by('created_at')
            
            for message in messages:
                # Extract code blocks
                code_blocks = CodeContextExtractor.extract_code_blocks(message.content)
                for block in code_blocks:
                    block_entry = {
                        'message_id': str(message.id),
                        'message_role': message.role,
                        'extracted_at': message.created_at.isoformat(),
                        **block
                    }
                    all_code_blocks.append(block_entry)
                
                # Extract file references
                file_refs = CodeContextExtractor.extract_file_references(message.content)
                all_file_refs.update(file_refs)
            
            # Limit to 50 most recent blocks
            if len(all_code_blocks) > 50:
                all_code_blocks = sorted(
                    all_code_blocks,
                    key=lambda x: x.get('extracted_at', ''),
                    reverse=True
                )[:50]
            
            # Update metadata
            total_code_tokens = sum(block.get('tokens', 0) for block in all_code_blocks)
            metadata = {
                'total_blocks': len(all_code_blocks),
                'total_code_tokens': total_code_tokens,
                'last_updated': timezone.now().isoformat(),
                'unique_files_count': len(all_file_refs),
                're_extracted_at': timezone.now().isoformat()
            }
            
            # Save to conversation
            conversation.referenced_files = list(all_file_refs)
            conversation.referenced_code_blocks = all_code_blocks
            conversation.code_context_metadata = metadata
            conversation.save(update_fields=['referenced_files', 'referenced_code_blocks', 'code_context_metadata'])
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✅ Extracted {len(all_code_blocks)} blocks, {len(all_file_refs)} files"
                )
            )
            
            total_processed += 1
            total_blocks += len(all_code_blocks)
            total_files += len(all_file_refs)

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS(f"✅ Processing Complete!"))
        self.stdout.write(f"  Conversations processed: {total_processed}")
        self.stdout.write(f"  Total code blocks: {total_blocks}")
        self.stdout.write(f"  Total file references: {total_files}")
        self.stdout.write("=" * 70)

