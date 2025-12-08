"""
Output Layer Generator for HishamOS.

Provides standardized output generation from agent/workflow results
with support for multiple formats (JSON, Markdown, HTML, Text, Code).
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import json
import html


class OutputFormat(Enum):
    """Supported output formats."""
    JSON = 'json'
    MARKDOWN = 'markdown'
    HTML = 'html'
    TEXT = 'text'
    CODE = 'code'
    MIXED = 'mixed'


class OutputGenerator:
    """
    Standardized output generator for agent/workflow results.
    
    Provides consistent formatting across different output types
    with support for templates, styling, and metadata.
    """
    
    def __init__(self, result_data: Dict[str, Any]):
        """
        Initialize output generator.
        
        Args:
            result_data: Dictionary containing result data with keys:
                - title: Result title
                - content: Main content
                - format: Output format (json, markdown, text, code, mixed)
                - metadata: Additional metadata
                - critique: Self-critique (optional)
                - action_items: List of action items (optional)
                - quality_score: Quality score 0-100 (optional)
                - confidence_score: Confidence score 0-100 (optional)
                - tags: List of tags (optional)
        """
        self.data = result_data
        self.title = result_data.get('title', 'Untitled Result')
        self.content = result_data.get('content', '')
        self.format = result_data.get('format', 'text')
        self.metadata = result_data.get('metadata', {})
        self.critique = result_data.get('critique', '')
        self.action_items = result_data.get('action_items', [])
        self.quality_score = result_data.get('quality_score')
        self.confidence_score = result_data.get('confidence_score')
        self.tags = result_data.get('tags', [])
    
    def generate(self, output_format: Optional[str] = None) -> str:
        """
        Generate output in specified format.
        
        Args:
            output_format: Desired output format (defaults to result's format)
            
        Returns:
            Formatted output string
        """
        format_type = output_format or self.format
        
        if format_type == 'json':
            return self._generate_json()
        elif format_type == 'markdown':
            return self._generate_markdown()
        elif format_type == 'html':
            return self._generate_html()
        elif format_type == 'code':
            return self._generate_code()
        elif format_type == 'mixed':
            return self._generate_mixed()
        else:  # text
            return self._generate_text()
    
    def _generate_json(self) -> str:
        """Generate JSON output."""
        output = {
            'title': self.title,
            'content': self.content,
            'metadata': self.metadata,
        }
        
        if self.critique:
            output['critique'] = self.critique
        if self.action_items:
            output['action_items'] = self.action_items
        if self.quality_score is not None:
            output['quality_score'] = self.quality_score
        if self.confidence_score is not None:
            output['confidence_score'] = self.confidence_score
        if self.tags:
            output['tags'] = self.tags
        
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    def _generate_markdown(self) -> str:
        """Generate Markdown output."""
        lines = [f"# {self.title}\n"]
        
        # Quality metrics
        if self.quality_score is not None or self.confidence_score is not None:
            lines.append("## Quality Metrics\n")
            if self.quality_score is not None:
                lines.append(f"- **Quality Score:** {self.quality_score:.1f}/100\n")
            if self.confidence_score is not None:
                lines.append(f"- **Confidence Score:** {self.confidence_score:.1f}/100\n")
            lines.append("")
        
        # Main content
        lines.append("## Content\n")
        lines.append(self.content)
        lines.append("")
        
        # Action items
        if self.action_items:
            lines.append("## Action Items\n")
            for i, item in enumerate(self.action_items, 1):
                if isinstance(item, dict):
                    item_text = item.get('text', str(item))
                    priority = item.get('priority', 'medium')
                    lines.append(f"{i}. [{priority.upper()}] {item_text}\n")
                else:
                    lines.append(f"{i}. {item}\n")
            lines.append("")
        
        # Critique
        if self.critique:
            lines.append("## Critique\n")
            lines.append(self.critique)
            lines.append("")
        
        # Tags
        if self.tags:
            lines.append("## Tags\n")
            lines.append(", ".join(f"`{tag}`" for tag in self.tags))
            lines.append("")
        
        # Metadata
        if self.metadata:
            lines.append("## Metadata\n")
            lines.append("```json")
            lines.append(json.dumps(self.metadata, indent=2))
            lines.append("```")
        
        return "\n".join(lines)
    
    def _generate_html(self) -> str:
        """Generate HTML output."""
        html_parts = [f"<h1>{html.escape(self.title)}</h1>"]
        
        # Quality metrics
        if self.quality_score is not None or self.confidence_score is not None:
            html_parts.append("<div class='quality-metrics'>")
            html_parts.append("<h2>Quality Metrics</h2>")
            html_parts.append("<ul>")
            if self.quality_score is not None:
                html_parts.append(f"<li><strong>Quality Score:</strong> {self.quality_score:.1f}/100</li>")
            if self.confidence_score is not None:
                html_parts.append(f"<li><strong>Confidence Score:</strong> {self.confidence_score:.1f}/100</li>")
            html_parts.append("</ul>")
            html_parts.append("</div>")
        
        # Main content
        html_parts.append("<div class='content'>")
        html_parts.append("<h2>Content</h2>")
        # Preserve line breaks
        content_html = html.escape(self.content).replace('\n', '<br>')
        html_parts.append(f"<div>{content_html}</div>")
        html_parts.append("</div>")
        
        # Action items
        if self.action_items:
            html_parts.append("<div class='action-items'>")
            html_parts.append("<h2>Action Items</h2>")
            html_parts.append("<ol>")
            for item in self.action_items:
                if isinstance(item, dict):
                    item_text = html.escape(item.get('text', str(item)))
                    priority = item.get('priority', 'medium')
                    html_parts.append(f"<li class='priority-{priority}'>{item_text}</li>")
                else:
                    html_parts.append(f"<li>{html.escape(str(item))}</li>")
            html_parts.append("</ol>")
            html_parts.append("</div>")
        
        # Critique
        if self.critique:
            html_parts.append("<div class='critique'>")
            html_parts.append("<h2>Critique</h2>")
            critique_html = html.escape(self.critique).replace('\n', '<br>')
            html_parts.append(f"<div>{critique_html}</div>")
            html_parts.append("</div>")
        
        # Tags
        if self.tags:
            html_parts.append("<div class='tags'>")
            html_parts.append("<h2>Tags</h2>")
            tags_html = " ".join(f"<span class='tag'>{html.escape(str(tag))}</span>" for tag in self.tags)
            html_parts.append(f"<div>{tags_html}</div>")
            html_parts.append("</div>")
        
        return "\n".join(html_parts)
    
    def _generate_text(self) -> str:
        """Generate plain text output."""
        lines = [f"{self.title}\n", "=" * len(self.title), "\n"]
        
        # Quality metrics
        if self.quality_score is not None or self.confidence_score is not None:
            lines.append("Quality Metrics:")
            if self.quality_score is not None:
                lines.append(f"  Quality Score: {self.quality_score:.1f}/100")
            if self.confidence_score is not None:
                lines.append(f"  Confidence Score: {self.confidence_score:.1f}/100")
            lines.append("")
        
        # Main content
        lines.append("Content:")
        lines.append(self.content)
        lines.append("")
        
        # Action items
        if self.action_items:
            lines.append("Action Items:")
            for i, item in enumerate(self.action_items, 1):
                if isinstance(item, dict):
                    item_text = item.get('text', str(item))
                    priority = item.get('priority', 'medium')
                    lines.append(f"  {i}. [{priority.upper()}] {item_text}")
                else:
                    lines.append(f"  {i}. {item}")
            lines.append("")
        
        # Critique
        if self.critique:
            lines.append("Critique:")
            lines.append(self.critique)
            lines.append("")
        
        # Tags
        if self.tags:
            lines.append(f"Tags: {', '.join(str(tag) for tag in self.tags)}")
        
        return "\n".join(lines)
    
    def _generate_code(self) -> str:
        """Generate code-formatted output."""
        # For code format, return content as-is with code block markers
        language = self.metadata.get('language', 'text')
        return f"```{language}\n{self.content}\n```"
    
    def _generate_mixed(self) -> str:
        """Generate mixed format output (combines multiple formats)."""
        # Mixed format: Use markdown as base, but include code blocks where appropriate
        lines = [f"# {self.title}\n"]
        
        # Main content (may contain code blocks)
        lines.append(self.content)
        lines.append("")
        
        # Additional sections in markdown
        if self.action_items:
            lines.append("## Action Items\n")
            for i, item in enumerate(self.action_items, 1):
                if isinstance(item, dict):
                    item_text = item.get('text', str(item))
                    priority = item.get('priority', 'medium')
                    lines.append(f"{i}. [{priority.upper()}] {item_text}\n")
                else:
                    lines.append(f"{i}. {item}\n")
            lines.append("")
        
        if self.critique:
            lines.append("## Critique\n")
            lines.append(self.critique)
            lines.append("")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'title': self.title,
            'content': self.content,
            'format': self.format,
            'metadata': self.metadata,
            'critique': self.critique,
            'action_items': self.action_items,
            'quality_score': self.quality_score,
            'confidence_score': self.confidence_score,
            'tags': self.tags,
        }


def generate_output(result_data: Dict[str, Any], output_format: Optional[str] = None) -> str:
    """
    Convenience function to generate output from result data.
    
    Args:
        result_data: Result data dictionary
        output_format: Desired output format (optional)
        
    Returns:
        Formatted output string
    """
    generator = OutputGenerator(result_data)
    return generator.generate(output_format)

