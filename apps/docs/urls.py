"""
URL configuration for documentation viewer.
"""

from django.urls import path
from .views import (
    documentation_list_files,
    documentation_get_file,
    documentation_search
)

urlpatterns = [
    path('docs/list_files/', documentation_list_files, name='docs-list-files'),
    path('docs/get_file/', documentation_get_file, name='docs-get-file'),
    path('docs/search/', documentation_search, name='docs-search'),
]

