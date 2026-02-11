from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Job Roles
    path('job-roles/create/', views.create_job_role_view, name='create_job_role'),
    path('job-roles/', views.job_roles_view, name='job_roles'),
    path('job-roles/<int:job_id>/', views.job_role_detail_view, name='job_role_detail'),
    
    # Diagnostic
    path('diagnostic/<int:job_id>/', views.diagnostic_view, name='diagnostic'),
    path('submission/<int:submission_id>/', views.submission_detail_view, name='submission_detail'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    
    # Results
    path('results/<int:job_id>/', views.results_view, name='results'),
]