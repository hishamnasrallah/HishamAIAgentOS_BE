import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from apps.projects.models import Story, UserStory, Project

# Check if Story and UserStory are the same
print(f"Story is UserStory: {Story is UserStory}")

# Count stories
story_count = Story.objects.count()
print(f"\nTotal User Stories in database: {story_count}")

# Check project
project_id = 'cb3dd7f3-a16c-4c59-a81e-a6484b45149c'
try:
    project = Project.objects.get(id=project_id)
    print(f"\nProject found: {project.name}")
    
   # Get stories for this project
    stories = Story.objects.filter(project=project)
    print(f"\nStories for this project: {stories.count()}")
    
    for story in stories:
        print(f"  - {story.title} ({story.status})")
        
except Project.DoesNotExist:
    print(f"\nProject {project_id} not found!")

# Test the filter with query param
filtered = Story.objects.filter(project__id=project_id)
print(f"\nStories filtered by project__id: {filtered.count()}")
