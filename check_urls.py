import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from django.urls import get_resolver
from django.conf import settings

# Get all URL patterns
resolver = get_resolver()

def list_urls(lis, acc=None):
    if acc is None:
        acc = []
    if not lis:
        return
    l = lis[0]
    if hasattr(l, 'url_patterns'):
        list_urls(l.url_patterns, acc)
        list_urls(lis[1:], acc)
    else:
        acc.append(l)
        list_urls(lis[1:], acc)
    return acc

all_urls = list_urls(resolver.url_patterns)

# Filter for stories-related URLs
print("=== URLs containing 'stories' ===")
stories_urls = [url for url in all_urls if 'stories' in str(url.pattern)]
if stories_urls:
    for url in stories_urls:
        print(f"  {url.pattern}")
else:
    print("  No 'stories' URLs found!")

print("\n=== URLs containing 'projects' ===")
project_urls = [url for url in all_urls if 'project' in str(url.pattern)]
for url in project_urls[:10]:  # First 10
    print(f"  {url.pattern}")
