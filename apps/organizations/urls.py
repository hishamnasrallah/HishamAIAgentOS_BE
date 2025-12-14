"""
URL configuration for organizations app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, OrganizationMemberViewSet

router = DefaultRouter()
# Register organization members at root level (for direct access)
router.register(r'organization-members', OrganizationMemberViewSet, basename='organization-member')
# Also register with nested path for RESTful nested access
router.register(r'(?P<organization_pk>[^/.]+)/members', OrganizationMemberViewSet, basename='organization-member-nested')

urlpatterns = [
    # Organization CRUD endpoints (explicit to avoid double 'organizations' in path)
    path('', OrganizationViewSet.as_view({'get': 'list', 'post': 'create'}), name='organization-list'),
    path('<uuid:pk>/', OrganizationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='organization-detail'),
    path('<uuid:pk>/members/', OrganizationViewSet.as_view({'get': 'members'}), name='organization-members'),
    path('<uuid:pk>/members/add/', OrganizationViewSet.as_view({'post': 'add_member'}), name='organization-add-member'),
    path('<uuid:pk>/members/remove/', OrganizationViewSet.as_view({'post': 'remove_member'}), name='organization-remove-member'),
    path('<uuid:pk>/members/<uuid:member_id>/update-role/', OrganizationViewSet.as_view({'patch': 'update_member_role'}), name='organization-update-member-role'),
    # Router URLs for nested resources (organization members)
    path('', include(router.urls)),
]

