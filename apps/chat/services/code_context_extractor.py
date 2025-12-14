"""
Code Context Extractor Service.

Extracts code blocks and file references from messages for Cursor-style context management.
"""

import re
from typing import List, Dict, Set, Optional
from datetime import datetime
import logging

from django.utils import timezone
from apps.chat.models import Conversation, Message

logger = logging.getLogger(__name__)


class CodeContextExtractor:
    """
    Service for extracting code-related context from messages.
    
    Similar to how Cursor IDE tracks code blocks and file references
    to maintain context in large codebases.
    """
    
    # File extension patterns for common languages
    FILE_EXTENSIONS = [
        'py', 'js', 'ts', 'tsx', 'jsx', 'java', 'cpp', 'c', 'h', 'hpp',
        'go', 'rs', 'rb', 'php', 'swift', 'kt', 'cs', 'dart', 'r', 'm',
        'mm', 'vue', 'svelte', 'html', 'css', 'scss', 'sass', 'less',
        'sql', 'sh', 'bash', 'zsh', 'fish', 'ps1', 'bat', 'cmd',
        'json', 'xml', 'yaml', 'yml', 'toml', 'ini', 'cfg', 'conf',
        'md', 'txt', 'log', 'env', 'dockerfile', 'makefile'
    ]
    
    # File path patterns (common structures)
    FILE_PATH_PATTERNS = [
        r'([a-zA-Z0-9_\-\./]+\.(?:' + '|'.join(FILE_EXTENSIONS) + r'))',  # Files with extensions
        r'([a-zA-Z0-9_\-\./]+/[a-zA-Z0-9_\-\./]+)',  # Directory paths
        r'(\./[a-zA-Z0-9_\-\./]+)',  # Relative paths starting with ./
        r'(\.\.[a-zA-Z0-9_\-\./]+)',  # Relative paths starting with ../
    ]
    
    @staticmethod
    def extract_code_blocks(content: str) -> List[Dict[str, any]]:
        """
        Extract code blocks from message content.
        
        Supports:
        - Markdown code blocks: ```language\ncode```
        - Inline code: `code`
        
        Args:
            content: Message content text
            
        Returns:
            List of code block dicts with language, content, tokens
        """
        code_blocks = []
        
        # Extract markdown code blocks (```language\ncode```)
        markdown_pattern = r'```(\w+)?\n([\s\S]*?)```'
        for match in re.finditer(markdown_pattern, content):
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            
            if code:  # Only add non-empty blocks
                tokens = CodeContextExtractor._estimate_tokens(code)
                code_blocks.append({
                    'language': language.lower(),
                    'content': code,
                    'line_count': len(code.split('\n')),
                    'char_count': len(code),
                    'tokens': tokens,
                    'type': 'markdown_block'
                })
        
        # Extract inline code blocks (if significant, > 20 chars)
        inline_pattern = r'`([^`]+)`'
        for match in re.finditer(inline_pattern, content):
            code = match.group(1).strip()
            # Only extract inline code if it looks like actual code (has structure)
            if len(code) > 20 and CodeContextExtractor._looks_like_code(code):
                tokens = CodeContextExtractor._estimate_tokens(code)
                code_blocks.append({
                    'language': 'text',  # Inline code language is hard to detect
                    'content': code,
                    'line_count': len(code.split('\n')),
                    'char_count': len(code),
                    'tokens': tokens,
                    'type': 'inline_code'
                })
        
        # Fallback: Detect unformatted code blocks (when markdown formatting is missing)
        # This catches cases where user sends code without backticks but it clearly looks like code
        if not code_blocks:
            unformatted_code = CodeContextExtractor._extract_unformatted_code(content)
            if unformatted_code:
                for code_snippet in unformatted_code:
                    tokens = CodeContextExtractor._estimate_tokens(code_snippet['content'])
                    code_blocks.append({
                        'language': code_snippet.get('language', 'text').lower(),
                        'content': code_snippet['content'],
                        'line_count': len(code_snippet['content'].split('\n')),
                        'char_count': len(code_snippet['content']),
                        'tokens': tokens,
                        'type': 'unformatted_code'  # Mark as unformatted for debugging
                    })
        
        return code_blocks
    
    @staticmethod
    def extract_file_references(content: str) -> Set[str]:
        """
        Extract file path references from message content.
        
        Detects:
        - File paths with extensions (e.g., app/models.py)
        - Directory paths (e.g., src/components/)
        - Relative paths (./file.py, ../parent/file.py)
        
        Args:
            content: Message content text
            
        Returns:
            Set of unique file paths found
        """
        file_references = set()
        
        # Combine all file path patterns
        combined_pattern = '|'.join(CodeContextExtractor.FILE_PATH_PATTERNS)
        
        for match in re.finditer(combined_pattern, content):
            file_path = match.group(1) or match.group(0)
            
            # Filter out common false positives
            if CodeContextExtractor._is_valid_file_reference(file_path):
                # Normalize path
                normalized = file_path.strip().strip('"').strip("'")
                file_references.add(normalized)
        
        # Also check for file references in code blocks (more reliable)
        code_blocks = CodeContextExtractor.extract_code_blocks(content)
        for block in code_blocks:
            block_content = block['content']
            for match in re.finditer(combined_pattern, block_content):
                file_path = match.group(1) or match.group(0)
                if CodeContextExtractor._is_valid_file_reference(file_path):
                    normalized = file_path.strip().strip('"').strip("'")
                    file_references.add(normalized)
        
        return file_references
    
    @staticmethod
    def update_conversation_code_context(conversation: Conversation, message: Message) -> Dict[str, any]:
        """
        Update conversation's code context with new message.
        
        Extracts code blocks and file references from the message
        and updates the conversation's stored context.
        
        Args:
            conversation: Conversation instance
            message: Message instance to extract from
            
        Returns:
            Dict with extraction results
        """
        # Extract code blocks
        code_blocks = CodeContextExtractor.extract_code_blocks(message.content)
        
        # Extract file references
        file_references = CodeContextExtractor.extract_file_references(message.content)
        
        # Get existing context
        existing_files = set(conversation.referenced_files or [])
        existing_blocks = conversation.referenced_code_blocks or []
        metadata = conversation.code_context_metadata or {}
        
        # Add new file references
        updated_files = list(existing_files | file_references)
        
        # Add new code blocks with message ID
        new_blocks = []
        for block in code_blocks:
            block_entry = {
                'message_id': str(message.id),
                'message_role': message.role,
                'extracted_at': timezone.now().isoformat(),
                **block
            }
            new_blocks.append(block_entry)
        
        # Merge with existing blocks (keep recent ones)
        # Limit to last 50 code blocks to prevent unbounded growth
        all_blocks = existing_blocks + new_blocks
        if len(all_blocks) > 50:
            # Keep most recent blocks
            all_blocks = sorted(all_blocks, key=lambda x: x.get('extracted_at', ''), reverse=True)[:50]
        
        # Update metadata
        total_blocks = len(all_blocks)
        total_code_tokens = sum(block.get('tokens', 0) for block in all_blocks)
        
        metadata.update({
            'total_blocks': total_blocks,
            'total_code_tokens': total_code_tokens,
            'last_updated': timezone.now().isoformat(),
            'unique_files_count': len(updated_files)
        })
        
        # Save to conversation
        conversation.referenced_files = updated_files
        conversation.referenced_code_blocks = all_blocks
        conversation.code_context_metadata = metadata
        conversation.save(update_fields=['referenced_files', 'referenced_code_blocks', 'code_context_metadata'])
        
        logger.info(
            f"[CodeContextExtractor] Updated code context for conversation {conversation.id}: "
            f"{len(new_blocks)} new blocks, {len(file_references)} new files"
        )
        
        return {
            'code_blocks_extracted': len(new_blocks),
            'files_extracted': len(file_references),
            'total_blocks': total_blocks,
            'total_files': len(updated_files)
        }
    
    @staticmethod
    def get_code_context_for_conversation(
        conversation: Conversation,
        max_tokens: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Get code context for a conversation, optionally limited by token budget.
        
        Args:
            conversation: Conversation instance
            max_tokens: Optional maximum tokens to include
            
        Returns:
            Dict with code blocks and file references, filtered by token budget if provided
        """
        code_blocks = conversation.referenced_code_blocks or []
        files = conversation.referenced_files or []
        
        # If token budget specified, prioritize blocks
        if max_tokens and code_blocks:
            code_blocks = CodeContextExtractor._prioritize_code_blocks(code_blocks, max_tokens)
        
        return {
            'code_blocks': code_blocks,
            'referenced_files': files,
            'metadata': conversation.code_context_metadata or {}
        }
    
    @staticmethod
    def _prioritize_code_blocks(blocks: List[Dict], max_tokens: int) -> List[Dict]:
        """
        Prioritize code blocks by recency and size, respecting token budget.
        
        Args:
            blocks: List of code block dicts
            max_tokens: Maximum tokens to include
            
        Returns:
            Filtered and prioritized list of blocks
        """
        # Sort by extracted_at (most recent first)
        sorted_blocks = sorted(
            blocks,
            key=lambda x: x.get('extracted_at', ''),
            reverse=True
        )
        
        selected = []
        token_count = 0
        
        for block in sorted_blocks:
            block_tokens = block.get('tokens', 0)
            if token_count + block_tokens <= max_tokens:
                selected.append(block)
                token_count += block_tokens
            else:
                break  # Stop when budget is exceeded
        
        return selected
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Estimate token count for text (approximation).
        
        Uses a simple heuristic: ~4 characters per token on average.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 4 chars per token
        # More accurate would require actual tokenizer, but this is faster
        char_count = len(text)
        return max(1, char_count // 4)
    
    @staticmethod
    def _extract_unformatted_code(content: str) -> List[Dict[str, str]]:
        """
        Fallback method to extract code blocks that weren't properly formatted with markdown.
        
        Looks for code-like patterns that appear after certain trigger phrases or have
        strong code indicators (class/def keywords, indentation patterns, etc.).
        
        This is a fallback for cases where markdown formatting is missing but code is clearly present.
        
        Args:
            content: Message content text
            
        Returns:
            List of detected code snippets with inferred language
        """
        code_snippets = []
        
        # Patterns that suggest code follows (case-insensitive)
        code_intro_patterns = [
            r"(?:here'?s?\s+(?:my|the|a)\s+(?:code|model|class|function|script|file|snippet))",
            r"(?:here'?s?\s+(?:my|the|a)\s+.*?\s*(?:code|model|class))",
            r"(?:code|model|class|function).*?:",
            r"(?:```?)?\s*(?:python|javascript|typescript|java|go|rust|c\+\+|c\#|php|ruby|swift|kotlin)\s*class",
            r"(?:```?)?\s*(?:python|javascript|typescript|java|go|rust|c\+\+|c\#|php|ruby|swift|kotlin)\s*def",
            r"(?:```?)?\s*(?:python|javascript|typescript|java|go|rust|c\+\+|c\#|php|ruby|swift|kotlin)\s*function",
            r"(?:```?)?\s*(?:python|javascript|typescript|java|go|rust|c\+\+|c\#|php|ruby|swift|kotlin)\s*interface",
        ]
        
        # Strong code indicators (must match multiple)
        code_indicators = [
            r'\bclass\s+\w+\s*[\(:]',  # class Name( or class Name:
            r'\bdef\s+\w+\s*\(',  # def name(
            r'\bfunction\s+\w+\s*\(',  # function name(
            r'\binterface\s+\w+',  # interface Name
            r'\bstruct\s+\w+',  # struct Name
            r'\bimport\s+',  # import statements
            r'\bfrom\s+\w+\s+import',  # from x import
            r'\bpublic\s+(?:class|interface|static)',  # Java/C# patterns
            r'\bprivate\s+(?:class|interface|static)',  # Java/C# patterns
            r'->\s*\w+',  # Type hints (-> return_type)
            r':\s*\w+\s*=',  # Type annotations (: Type =)
            r'\w+\s*=\s*models\.',  # Django model fields
            r'\w+\s*=\s*\[',  # List assignments
            r'\w+\s*=\s*\{',  # Dict/object assignments
            r'auto_now_add=True',  # Django-specific
            r'max_length=\d+',  # Django model fields
        ]
        
        # Look for patterns that suggest code starts
        for intro_pattern in code_intro_patterns:
            intro_match = re.search(intro_pattern, content, re.IGNORECASE)
            if intro_match:
                # Extract text after the intro pattern
                start_pos = intro_match.end()
                remaining_text = content[start_pos:].strip()
                
                # Look for code-like content (multiple lines with structure)
                # Try to find where code block might end (next sentence, double newline, etc.)
                # Take up to 50 lines or until we hit a pattern that suggests end of code
                lines = remaining_text.split('\n')
                code_lines = []
                
                for i, line in enumerate(lines[:50]):  # Limit to 50 lines
                    line_stripped = line.strip()
                    
                    # Stop if we hit something that looks like end of code block
                    if not line_stripped:
                        if code_lines:  # Empty line after code might be end
                            break
                        continue
                    
                    # Stop if we hit plain English text (sentence with period, question mark)
                    if re.match(r'^[A-Z][^.]{50,}', line_stripped) and i > 5:
                        # Likely prose after code block
                        break
                    
                    # Accumulate lines that look like code
                    if CodeContextExtractor._looks_like_code_line(line_stripped):
                        code_lines.append(line)
                    elif code_lines:  # We have code lines but this doesn't look like code
                        # Might be a comment or end of block
                        if not line_stripped.startswith('#') and not line_stripped.startswith('//'):
                            break
                        code_lines.append(line)
                
                # Only accept if we found substantial code (multiple indicators)
                if code_lines:
                    code_text = '\n'.join(code_lines).strip()
                    
                    # Check if it has strong code indicators
                    indicator_count = sum(1 for pattern in code_indicators if re.search(pattern, code_text, re.IGNORECASE))
                    
                    if indicator_count >= 2 and len(code_text) > 30:  # At least 2 indicators and substantial length
                        # Try to infer language BEFORE adding to snippets
                        language = CodeContextExtractor._infer_language(code_text)
                        
                        code_snippets.append({
                            'content': code_text,
                            'language': language,
                            'confidence': 'medium',  # Lower confidence for unformatted
                            'detected_by': 'fallback_pattern_matching'
                        })
                        break  # Only extract one block per message to avoid false positives
        
        return code_snippets
    
    @staticmethod
    def _looks_like_code_line(line: str) -> bool:
        """
        Check if a single line looks like code.
        
        Args:
            line: Single line of text
            
        Returns:
            True if line appears to be code
        """
        # Must have some code-like features
        code_features = [
            r'\b(class|def|function|import|from|return|if|for|while|try|except|catch|public|private|static|const|let|var)\b',
            r'[{}();,=]',  # Code punctuation
            r'\w+\s*=\s*',  # Assignments
            r'->',  # Type hints
            r'::',  # Scope resolution
        ]
        
        # Check for code features
        has_code_features = any(re.search(pattern, line, re.IGNORECASE) for pattern in code_features)
        
        # Should not be plain prose (avoid false positives)
        is_prose = re.match(r'^[A-Z][a-z]+\s+[a-z]+\s', line)  # "The user model"
        
        return has_code_features and not is_prose
    
    @staticmethod
    def _infer_language(code_text: str) -> str:
        """
        Try to infer programming language from code text.
        
        Args:
            code_text: Code content
            
        Returns:
            Inferred language name or 'text' if uncertain
        """
        code_lower = code_text.lower()
        # Normalize whitespace for matching
        code_normalized = ' '.join(code_text.split())
        code_normalized_lower = code_normalized.lower()
        
        # Python indicators (check for Django models, Python keywords, etc.)
        python_indicators = [
            r'\bdef\s+\w+\s*\(',  # Python function definition
            r'models\.(EmailField|CharField|DateTimeField|IntegerField|ForeignKey|TextField|BooleanField)',  # Django model fields
            r'models\.model',  # Django Model base class
            r'class\s+\w+.*models\.model',  # Django model class (works with whitespace)
            r'class\s+\w+\s*\(.*models\.model',  # Django model class with parens
            r'\bclass\s+\w+\s*\(',  # Python class definition
            r'auto_now_add',  # Django-specific
            r'__str__|__repr__|__init__',  # Python magic methods
            r'from\s+django|import\s+django',  # Django imports
            r'from\s+.*\s+import\s+models',  # Django models import
        ]
        
        # Check both original and normalized code
        if any(re.search(pattern, code_normalized_lower, re.DOTALL) for pattern in python_indicators):
            return 'python'
        
        # Also check original lowercase (for cases where normalization might break patterns)
        if any(re.search(pattern, code_lower, re.DOTALL) for pattern in python_indicators):
            return 'python'
        
        # JavaScript/TypeScript indicators
        if re.search(r'\bfunction\s+\w+\s*\(|const\s+\w+\s*=|let\s+\w+\s*=|export\s+(default\s+)?(function|class)', code_lower):
            return 'javascript'
        
        # Java indicators
        if re.search(r'\bpublic\s+(static\s+)?(class|interface)|@Override|System\.out\.print', code_lower):
            return 'java'
        
        # C/C++ indicators
        if re.search(r'#include\s*<|std::|namespace\s+\w+', code_lower):
            return 'cpp'
        
        # Go indicators
        if re.search(r'func\s+\w+\s*\(|package\s+\w+|:=', code_lower):
            return 'go'
        
        # Rust indicators
        if re.search(r'fn\s+\w+\s*\(|impl\s+\w+|use\s+\w+::', code_lower):
            return 'rust'
        
        return 'text'  # Default fallback
    
    @staticmethod
    def _looks_like_code(text: str) -> bool:
        """
        Heuristic to determine if text looks like code.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be code
        """
        # Simple heuristics
        code_indicators = [
            r'[{}]',  # Braces
            r'[()]',  # Parentheses in patterns
            r'function\s+\w+',  # Function definitions
            r'class\s+\w+',  # Class definitions
            r'def\s+\w+',  # Python functions
            r'import\s+',  # Imports
            r'=\s*[({]',  # Assignments with structures
            r'->\s*\w+',  # Type hints
        ]
        
        text_lower = text.lower()
        matches = sum(1 for pattern in code_indicators if re.search(pattern, text_lower))
        return matches >= 2  # At least 2 code indicators
    
    @staticmethod
    def _is_valid_file_reference(path: str) -> bool:
        """
        Filter out false positives from file path detection.
        
        Args:
            path: Potential file path
            
        Returns:
            True if path looks like a valid file reference
        """
        # Filter out common false positives
        invalid_patterns = [
            r'^http',  # URLs
            r'^www\.',  # URLs
            r'^mailto:',  # Email
            r'^\d+$',  # Pure numbers
            r'^[a-z]://',  # Protocols
            r'^[a-z]\.[a-z]',  # Domain-like patterns
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, path, re.IGNORECASE):
                return False
        
        # Must have reasonable length
        if len(path) < 3 or len(path) > 200:
            return False
        
        # Should contain path separators or extensions for most cases
        if '/' in path or '\\' in path or '.' in path:
            return True
        
        return False

