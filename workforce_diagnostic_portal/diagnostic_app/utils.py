from django.db.models import Count, Q
from .models import Notification, JobRole, RoleAssignment, DiagnosticSubmission


def create_notification(user, message, job_role=None):
    """Create a notification for a user"""
    Notification.objects.create(
        user=user,
        message=message,
        job_role=job_role
    )


def notify_role_assignment(job_role):
    """Notify all assigned users about a new job role"""
    assigned_users = job_role.assigned_users.all()
    
    for user in assigned_users:
        message = f"You have been assigned to assess the job role: {job_role.title}"
        create_notification(user, message, job_role)


def get_dashboard_stats(user):
    """Get dashboard statistics for a user"""
    if user.get_level() == 1:
        # Level 1 sees all jobs
        total_jobs = JobRole.objects.count()
        assigned_jobs = user.assigned_jobs.count()
    else:
        # Other levels see only their assigned jobs
        total_jobs = user.assigned_jobs.count()
        assigned_jobs = total_jobs
    
    completed = DiagnosticSubmission.objects.filter(user=user).count()
    pending = assigned_jobs - completed
    
    return {
        'total_jobs': total_jobs,
        'assigned_jobs': assigned_jobs,
        'completed': completed,
        'pending': pending,
        'completion_rate': round((completed / assigned_jobs * 100) if assigned_jobs > 0 else 0, 1)
    }


def get_job_progress(job_role):
    """Get progress of a job role assessment"""
    total_assignments = RoleAssignment.objects.filter(job_role=job_role).count()
    completed = RoleAssignment.objects.filter(job_role=job_role, is_completed=True).count()
    
    if total_assignments == 0:
        return 0
    
    return round((completed / total_assignments) * 100, 1)


def get_level_submissions(job_role, level):
    """Get all submissions for a specific level"""
    if level == 1:
        roles = ['founder', 'co_founder', 'ceo', 'cfo']
    elif level == 2:
        roles = ['cto', 'coo', 'project_head']
    else:  # level == 3
        roles = ['hr_manager', 'recruiter', 'hr_executive']
    
    return DiagnosticSubmission.objects.filter(
        job_role=job_role,
        user__role__in=roles
    )


def calculate_role_risk_score(submission):
    """Calculate risk score for a submission"""
    from .rules_engine import RulesEngine
    
    user_level = submission.user.get_level()
    
    if user_level == 1:
        risk_score = RulesEngine.calculate_level_risk(submission)
    elif user_level == 2:
        risk_score = RulesEngine.calculate_level_2_risk(submission)
    else:
        risk_score = RulesEngine.calculate_level_3_risk(submission)
    
    return risk_score