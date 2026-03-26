from .models import User

def navigation_context(request):
    """
    Context processor to provide role-based navigation items
    """
    if not request.user.is_authenticated:
        return {}
    
    user = request.user
    navigation_items = []
    
    # Core navigation items (always visible)
    navigation_items.extend([
        {
            'name': 'Dashboard',
            'url': 'dashboard',
            'icon': '📊',
            'active': request.path == '/dashboard/'
        },
        {
            'name': 'Job Roles',
            'url': 'job_roles',
            'icon': '👥',
            'active': '/job-roles' in request.path and request.path != '/job-roles/create/'
        },
        {
            'name': 'Notifications',
            'url': 'notifications',
            'icon': '🔔',
            'active': '/notifications' in request.path
        }
    ])
    
    # Role-based navigation items
    if user.can_create_job_roles():
        navigation_items.append({
            'name': 'Create Job Role',
            'url': 'create_job_role',
            'icon': '➕',
            'active': request.path == '/job-roles/create/'
        })
    
    if user.can_view_analytics():
        navigation_items.append({
            'name': 'Analytics',
            'url': 'analytics',
            'icon': '📈',
            'active': '/analytics' in request.path
        })
    
    if user.can_access_reports():
        navigation_items.append({
            'name': 'Reports',
            'url': 'reports',
            'icon': '📊',
            'active': '/reports' in request.path
        })
    
    if user.can_manage_users():
        navigation_items.append({
            'name': 'User Management',
            'url': 'user_management',
            'icon': '👤',
            'active': '/users' in request.path
        })
    
    if user.can_view_audit_logs():
        navigation_items.append({
            'name': 'Audit Logs',
            'url': 'audit_logs',
            'icon': '🧾',
            'active': '/audit-logs' in request.path
        })
    
    if user.can_view_system_settings():
        navigation_items.append({
            'name': 'Settings',
            'url': 'settings',
            'icon': '⚙️',
            'active': '/settings' in request.path
        })
    
    # HR-specific items
    if user.role in ['hr_manager', 'recruiter', 'hr_executive']:
        navigation_items.append({
            'name': 'Candidates',
            'url': 'candidates',
            'icon': '🎯',
            'active': '/candidates' in request.path
        })
    
    # Technical leadership items
    if user.role in ['cto', 'coo', 'project_head']:
        navigation_items.append({
            'name': 'Projects',
            'url': 'projects',
            'icon': '🚀',
            'active': '/projects' in request.path
        })
    
    # Executive items
    if user.role in ['ceo', 'cfo']:
        navigation_items.append({
            'name': 'Executive Dashboard',
            'url': 'executive_dashboard',
            'icon': '💼',
            'active': '/executive' in request.path
        })
    
    return {
        'navigation_items': navigation_items,
        'user_permissions': {
            'can_create_job_roles': user.can_create_job_roles(),
            'can_view_analytics': user.can_view_analytics(),
            'can_view_audit_logs': user.can_view_audit_logs(),
            'can_manage_users': user.can_manage_users(),
            'can_access_reports': user.can_access_reports(),
            'can_view_system_settings': user.can_view_system_settings(),
        }
    }
