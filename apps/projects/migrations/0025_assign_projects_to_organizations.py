"""
Data migration to assign existing projects to organizations.

This migration:
1. Creates organizations for users who own projects but don't have an organization
2. Assigns all existing projects to organizations based on their owners
3. Creates a default organization for orphaned projects
"""

from django.db import migrations


def assign_projects_to_organizations(apps, schema_editor):
    """Assign existing projects to organizations."""
    Organization = apps.get_model('organizations', 'Organization')
    OrganizationMember = apps.get_model('organizations', 'OrganizationMember')
    Project = apps.get_model('projects', 'Project')
    User = apps.get_model('authentication', 'User')
    
    # Get all projects without organizations
    projects_without_org = Project.objects.filter(organization__isnull=True)
    
    if not projects_without_org.exists():
        return
    
    # Create a default organization if none exists
    default_org, created = Organization.objects.get_or_create(
        slug='default-organization',
        defaults={
            'name': 'Default Organization',
            'description': 'Default organization for existing projects',
            'status': 'active',
            'subscription_tier': 'professional',
            'max_users': 100,
            'max_projects': 100,
        }
    )
    
    # Assign projects to organizations based on their owners
    for project in projects_without_org:
        if project.owner_id:
            try:
                owner = User.objects.get(id=project.owner_id)
                
                # Check if owner has an organization
                if owner.organization_id:
                    project.organization_id = owner.organization_id
                else:
                    # Check if owner is a member of any organization
                    org_member = OrganizationMember.objects.filter(user_id=owner.id).first()
                    if org_member:
                        project.organization_id = org_member.organization_id
                        # Also update owner's primary organization
                        owner.organization_id = org_member.organization_id
                        owner.save(update_fields=['organization_id'])
                    else:
                        # Create organization for the owner
                        org_slug = f"{owner.username}-org" if owner.username else f"user-{owner.id}-org"
                        # Ensure slug is unique
                        counter = 1
                        base_slug = org_slug
                        while Organization.objects.filter(slug=org_slug).exists():
                            org_slug = f"{base_slug}-{counter}"
                            counter += 1
                        
                        # Build name from available fields (historical models don't have get_full_name)
                        owner_name = f"{owner.first_name} {owner.last_name}".strip() if (owner.first_name or owner.last_name) else owner.email
                        org = Organization.objects.create(
                            name=f"{owner_name}'s Organization",
                            slug=org_slug,
                            description=f"Organization for {owner_name}",
                            owner_id=owner.id,
                            created_by_id=owner.id,
                            status='active',
                            subscription_tier='professional',
                            max_users=50,
                            max_projects=50,
                        )
                        
                        # Create organization member
                        OrganizationMember.objects.create(
                            organization_id=org.id,
                            user_id=owner.id,
                            role='org_admin',
                            invited_by_id=owner.id
                        )
                        
                        # Update owner's primary organization
                        owner.organization_id = org.id
                        owner.save(update_fields=['organization_id'])
                        
                        project.organization_id = org.id
            except User.DoesNotExist:
                # Project owner doesn't exist, assign to default organization
                project.organization_id = default_org.id
        else:
            # Project has no owner, assign to default organization
            project.organization_id = default_org.id
        
        project.save(update_fields=['organization_id'])


def reverse_assign_projects(apps, schema_editor):
    """Reverse migration - set organization to None."""
    Project = apps.get_model('projects', 'Project')
    Project.objects.all().update(organization_id=None)


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0024_project_organization_alter_project_slug'),
        ('organizations', '__first__'),  # Use __first__ to get the first migration
        ('authentication', '0004_user_organization_alter_user_role'),
    ]

    operations = [
        migrations.RunPython(
            assign_projects_to_organizations,
            reverse_assign_projects
        ),
    ]

