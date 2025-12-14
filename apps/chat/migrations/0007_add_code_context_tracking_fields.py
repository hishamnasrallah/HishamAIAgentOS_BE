# Generated manually on 2025-12-14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0006_conversation_conversation_summary_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="referenced_files",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="List of file paths referenced in conversation (e.g., ['app/models.py', 'frontend/src/Chat.tsx'])",
            ),
        ),
        migrations.AddField(
            model_name="conversation",
            name="referenced_code_blocks",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Code blocks extracted from messages: [{message_id, language, content, tokens, extracted_at}]",
            ),
        ),
        migrations.AddField(
            model_name="conversation",
            name="code_context_metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Code context metadata: {total_blocks: 5, total_code_tokens: 750, last_updated: '...'}",
            ),
        ),
    ]

