from django.urls import path
from . import views

urlpatterns = [
    # Homepage (default route)
    path('', views.home_view, name='home'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & analytics
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Job Roles
    path('job-roles/create/', views.create_job_role_view, name='create_job_role'),
    path('job-roles/', views.job_roles_view, name='job_roles'),
    path('job-roles/<int:job_id>/', views.job_role_detail_view, name='job_role_detail'),
    path('job-roles/<int:job_id>/delete/', views.delete_job_role_view, name='delete_job_role'),
    
    # Diagnostic
    path('diagnostic/<int:job_id>/', views.diagnostic_view, name='diagnostic'),
    path('submission/<int:submission_id>/', views.submission_detail_view, name='submission_detail'),
    path('submission/<int:submission_id>/edit/', views.edit_submission_view, name='edit_submission'),
    path('submission/<int:submission_id>/delete/', views.delete_submission_view, name='delete_submission'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    
    # Results
    path('results/<int:job_id>/', views.results_view, name='results'),

    # Audit logs (admin-only)
    path('audit-logs/', views.audit_logs_view, name='audit_logs'),
    path('audit-logs/<int:log_id>/', views.audit_log_detail_view, name='audit_log_detail'),
]