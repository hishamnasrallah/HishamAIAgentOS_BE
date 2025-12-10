"""
AI Story Suggestions Service.
Provides AI-powered suggestions for story creation, improvement, and analysis.
"""

from typing import Dict, List, Optional
from apps.projects.models import UserStory, Project
from django.db.models import Q
import re


class AISuggestionsService:
    """Service for AI-powered story suggestions."""
    
    @staticmethod
    def suggest_story_title(description: str, project_context: Dict = None) -> List[str]:
        """
        Suggest story titles based on description.
        
        Args:
            description: Story description
            project_context: Optional project context (existing stories, patterns)
        
        Returns:
            List of suggested titles
        """
        if not description:
            return []
        
        # Simple keyword extraction and title generation
        # In production, this would use an AI model
        sentences = description.split('.')
        keywords = []
        
        for sentence in sentences[:3]:  # Use first 3 sentences
            words = sentence.split()
            # Extract important words (capitalized, longer words)
            important_words = [w for w in words if len(w) > 4 and w[0].isupper()]
            keywords.extend(important_words[:2])
        
        suggestions = []
        
        # Generate title suggestions
        if keywords:
            # Pattern 1: "As a [user], I want [feature]"
            if len(keywords) >= 2:
                suggestions.append(f"Implement {keywords[0]} {keywords[1]}")
            
            # Pattern 2: Feature-based
            if keywords:
                suggestions.append(f"Add {keywords[0]} Feature")
            
            # Pattern 3: Action-based
            if len(keywords) >= 2:
                suggestions.append(f"Enable {keywords[0]} for {keywords[1]}")
        
        # Fallback: Use first sentence as title
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) < 100:
                suggestions.append(first_sentence)
        
        return suggestions[:5]  # Return top 5
    
    @staticmethod
    def suggest_acceptance_criteria(description: str, story_type: str = 'feature') -> List[str]:
        """
        Suggest acceptance criteria based on description.
        
        Returns:
            List of suggested acceptance criteria
        """
        if not description:
            return []
        
        criteria = []
        
        # Extract action verbs
        action_patterns = [
            r'should\s+(\w+)',
            r'must\s+(\w+)',
            r'need\s+to\s+(\w+)',
            r'able\s+to\s+(\w+)',
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches[:3]:
                criteria.append(f"User should be able to {match}")
        
        # Default criteria based on story type
        if story_type == 'feature':
            criteria.extend([
                "Feature should be accessible and functional",
                "Feature should handle errors gracefully",
                "Feature should be tested and verified"
            ])
        elif story_type == 'bug':
            criteria.extend([
                "Bug should be reproducible",
                "Bug should be fixed without breaking existing functionality",
                "Fix should be tested and verified"
            ])
        
        return criteria[:5]
    
    @staticmethod
    def suggest_story_points(description: str, complexity_indicators: List[str] = None) -> Optional[int]:
        """
        Suggest story points based on description and complexity.
        
        Returns:
            Suggested story points (1-13 Fibonacci scale)
        """
        if not description:
            return None
        
        # Simple heuristic-based estimation
        # In production, this would use ML model
        
        word_count = len(description.split())
        complexity_score = 0
        
        # Word count indicator
        if word_count < 50:
            complexity_score += 1
        elif word_count < 150:
            complexity_score += 2
        else:
            complexity_score += 3
        
        # Complexity keywords
        complexity_keywords = {
            'simple': 1,
            'easy': 1,
            'basic': 1,
            'complex': 3,
            'difficult': 3,
            'advanced': 3,
            'integrate': 2,
            'migration': 3,
            'refactor': 2,
        }
        
        description_lower = description.lower()
        for keyword, score in complexity_keywords.items():
            if keyword in description_lower:
                complexity_score += score
        
        # Fibonacci scale mapping
        fibonacci = [1, 2, 3, 5, 8, 13]
        
        if complexity_score <= 2:
            return fibonacci[0]  # 1
        elif complexity_score <= 4:
            return fibonacci[1]  # 2
        elif complexity_score <= 6:
            return fibonacci[2]  # 3
        elif complexity_score <= 8:
            return fibonacci[3]  # 5
        elif complexity_score <= 10:
            return fibonacci[4]  # 8
        else:
            return fibonacci[5]  # 13
    
    @staticmethod
    def suggest_related_stories(story_id: str, limit: int = 5) -> List[Dict]:
        """
        Suggest related stories based on similarity.
        
        Returns:
            List of related story dictionaries
        """
        try:
            story = UserStory.objects.select_related('project').get(pk=story_id)
        except UserStory.DoesNotExist:
            return []
        
        # Find similar stories in the same project
        candidates = UserStory.objects.filter(
            project=story.project
        ).exclude(pk=story.id)
        
        related = []
        
        # Simple similarity based on title and description
        story_text = f"{story.title} {story.description}".lower()
        story_words = set(story_text.split())
        
        for candidate in candidates:
            candidate_text = f"{candidate.title} {candidate.description}".lower()
            candidate_words = set(candidate_text.split())
            
            # Calculate word overlap
            intersection = story_words.intersection(candidate_words)
            union = story_words.union(candidate_words)
            
            if len(union) > 0:
                similarity = len(intersection) / len(union)
                
                if similarity > 0.2:  # 20% similarity threshold
                    related.append({
                        'id': str(candidate.id),
                        'title': candidate.title,
                        'status': candidate.status,
                        'similarity': round(similarity, 2),
                    })
        
        # Sort by similarity
        related.sort(key=lambda x: x['similarity'], reverse=True)
        
        return related[:limit]
    
    @staticmethod
    def improve_story_description(description: str) -> Dict:
        """
        Suggest improvements to story description.
        
        Returns:
            Dict with improved description and suggestions
        """
        if not description:
            return {
                'improved': '',
                'suggestions': ['Add a description to get improvement suggestions']
            }
        
        suggestions = []
        improved = description
        
        # Check for clarity
        if len(description) < 50:
            suggestions.append("Consider adding more detail about the feature or requirement")
        
        # Check for user perspective
        if 'user' not in description.lower() and 'I' not in description:
            suggestions.append("Consider writing from user perspective (e.g., 'As a user, I want...')")
        
        # Check for acceptance criteria
        if 'should' not in description.lower() and 'must' not in description.lower():
            suggestions.append("Consider adding acceptance criteria or requirements")
        
        # Check for technical details
        technical_keywords = ['api', 'database', 'endpoint', 'service', 'component']
        has_technical = any(keyword in description.lower() for keyword in technical_keywords)
        if not has_technical and len(description) > 100:
            suggestions.append("Consider adding technical implementation details if applicable")
        
        return {
            'improved': improved,
            'suggestions': suggestions,
            'original_length': len(description),
            'improved_length': len(improved)
        }
    
    @staticmethod
    def suggest_tags(description: str, project: Project = None) -> List[str]:
        """
        Suggest tags based on description and project context.
        
        Returns:
            List of suggested tags
        """
        if not description:
            return []
        
        tags = []
        description_lower = description.lower()
        
        # Extract keywords
        words = description_lower.split()
        important_words = [w for w in words if len(w) > 4 and w.isalpha()]
        
        # Common tag patterns
        tag_patterns = {
            'frontend': ['ui', 'interface', 'page', 'component', 'view', 'design'],
            'backend': ['api', 'endpoint', 'service', 'database', 'server'],
            'mobile': ['mobile', 'app', 'ios', 'android'],
            'security': ['security', 'auth', 'permission', 'access', 'encrypt'],
            'performance': ['performance', 'speed', 'optimize', 'cache'],
            'testing': ['test', 'testing', 'qa', 'quality'],
        }
        
        for tag, keywords in tag_patterns.items():
            if any(keyword in description_lower for keyword in keywords):
                tags.append(tag)
        
        # Add project tags if available
        if project and project.tags:
            tags.extend(project.tags[:3])
        
        return list(set(tags))[:10]  # Return unique tags, max 10

