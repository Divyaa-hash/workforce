from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.urls import reverse
from .forms import CustomUserCreationForm, LoginForm, JobRoleForm, DiagnosticForm
from .models import User, JobRole, DiagnosticSubmission, RoleAssignment, Notification

# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        level = request.user.get_level()
        dashboard_url = reverse('dashboard')
        return redirect(f'{dashboard_url}?level={level}')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        print(f"Login attempt: {username}, role: {role}")
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"User authenticated: {user.username}, actual role: {user.role}")
            
            # Check if selected role matches user's actual role
            if user.role == role:
                login(request, user)
                messages.success(request, f'Welcome, {user.get_role_display()}!')
                level = user.get_level()
                dashboard_url = reverse('dashboard')
                return redirect(f'{dashboard_url}?level={level}')
            else:
                messages.error(request, f'Please select correct role: {user.get_role_display()}')
        else:
            print("Authentication failed")
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'diagnostic_app/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    # Get statistics
    if request.user.get_level() == 1:
        # Level 1 sees all jobs
        total_jobs = JobRole.objects.count()
        assigned_jobs = RoleAssignment.objects.filter(user=request.user).count()
    else:
        # Other levels see only their assigned jobs
        assigned_jobs = RoleAssignment.objects.filter(user=request.user).count()
        total_jobs = assigned_jobs
    
    completed = DiagnosticSubmission.objects.filter(user=request.user).count()
    pending = assigned_jobs - completed
    
    stats = {
        'total_jobs': total_jobs,
        'assigned_jobs': assigned_jobs,
        'completed': completed,
        'pending': pending,
        'completion_rate': round((completed / assigned_jobs * 100) if assigned_jobs > 0 else 0, 1)
    }
    
    # Get assigned jobs for display
    if request.user.get_level() == 1:
        # Level 1 sees all jobs
        jobs = JobRole.objects.all().order_by('-created_at')[:6]
    else:
        # Other levels see only their assigned jobs
        assigned_job_ids = RoleAssignment.objects.filter(user=request.user).values_list('job_role_id', flat=True)
        jobs = JobRole.objects.filter(id__in=assigned_job_ids).order_by('-created_at')[:6]
    
    # Get recent notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'jobs': jobs,
        'notifications': notifications,
        'user_level': request.user.get_level(),
    }
    
    return render(request, 'diagnostic_app/dashboard.html', context)

# Job Role Views
@login_required
def create_job_role_view(request):
    # Check if user can create job roles
    if not request.user.can_create_job_roles():
        messages.error(request, 'Only Founders and Co-Founders can create job roles.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = JobRoleForm(request.POST, user=request.user)
        if form.is_valid():
            # Save the job role
            job_role = form.save(commit=False)
            job_role.created_by = request.user
            job_role.status = 'active'
            job_role.save()
            
            # Auto-assign roles based on level
            auto_assign_users(job_role)
            
            # Create notifications
            notify_role_assignment(job_role)
            
            messages.success(request, f'Job role "{job_role.title}" created successfully!')
            return redirect('job_roles')
    else:
        form = JobRoleForm(user=request.user)
    
    return render(request, 'diagnostic_app/create_job_role.html', {'form': form})


def auto_assign_users(job_role):
    """Automatically assign relevant users to the job role"""
    # Get all users
    all_users = User.objects.all()
    
    for user in all_users:
        # Always assign the creator (Founder/Co-Founder)
        if user == job_role.created_by:
            RoleAssignment.objects.get_or_create(job_role=job_role, user=user)
            print(f"✅ Assigned creator: {user.username}")
        
        # Assign ALL Level 1 users (Founder, Co-Founder, CEO, CFO)
        elif user.get_level() == 1:
            RoleAssignment.objects.get_or_create(job_role=job_role, user=user)
            print(f"✅ Assigned Level 1: {user.username} ({user.get_role_display()})")
        
        # Assign Level 2 users (CTO, COO, Project Head)
        elif user.get_level() == 2:
            RoleAssignment.objects.get_or_create(job_role=job_role, user=user)
            print(f"✅ Assigned Level 2: {user.username}")
        
        # Assign Level 3 users (HR roles)
        elif user.get_level() == 3:
            RoleAssignment.objects.get_or_create(job_role=job_role, user=user)
            print(f"✅ Assigned Level 3: {user.username}")

def notify_role_assignment(job_role):
    """Notify all assigned users about a new job role"""
    assigned_users = User.objects.filter(assignments__job_role=job_role)
    
    for user in assigned_users:
        message = f"You have been assigned to assess the job role: {job_role.title}"
        Notification.objects.create(
            user=user,
            message=message,
            job_role=job_role
        )


@login_required
def job_roles_view(request):
    if request.user.get_level() == 1:
        # Level 1 sees all jobs
        jobs = JobRole.objects.all().order_by('-created_at')
    else:
        # Other levels see only their assigned jobs
        assigned_job_ids = RoleAssignment.objects.filter(user=request.user).values_list('job_role_id', flat=True)
        jobs = JobRole.objects.filter(id__in=assigned_job_ids).order_by('-created_at')
    
    # Get submission status for each job for the current user only
    for job in jobs:
        try:
            assignment = RoleAssignment.objects.get(job_role=job, user=request.user)
            if assignment.is_completed:
                job.user_status = 'completed'
            else:
                job.user_status = 'in_progress'
            job.can_assess = not assignment.is_completed
        except RoleAssignment.DoesNotExist:
            # User has not started / is not assigned to this job
            job.user_status = 'not_started'
            job.can_assess = False
    
    context = {'jobs': jobs}
    return render(request, 'diagnostic_app/job_roles.html', context)

@login_required
def job_role_detail_view(request, job_id):
    job = get_object_or_404(JobRole, id=job_id)
    
    # Check if user can access this job
    if request.user.get_level() != 1:
        if not RoleAssignment.objects.filter(job_role=job, user=request.user).exists():
            messages.error(request, 'You are not assigned to this job role.')
            return redirect('dashboard')
    
    # Check if user has already submitted
    user_submission = DiagnosticSubmission.objects.filter(job_role=job, user=request.user).first()
    
    # Get all assignments for this job
    assignments = RoleAssignment.objects.filter(job_role=job)
    
    # Calculate progress
    total_assignments = assignments.count()
    completed_assignments = assignments.filter(is_completed=True).count()
    progress = round((completed_assignments / total_assignments * 100) if total_assignments > 0 else 0, 1)
    
    # Get all submissions for this job
    submissions = DiagnosticSubmission.objects.filter(job_role=job)
    
    # Group by level for display
    level1_subs = submissions.filter(user__role__in=['founder', 'co_founder'])
    level2_subs = submissions.filter(user__role__in=['ceo', 'cfo', 'cto', 'coo', 'project_head'])
    level3_subs = submissions.filter(user__role__in=['hr_manager', 'recruiter', 'hr_executive'])
    
    # Get all users for display
    all_users = User.objects.all()
    
    context = {
        'job': job,
        'user_submission': user_submission,
        'assignments': assignments,
        'submissions': submissions,
        'level1_subs': level1_subs,
        'level2_subs': level2_subs,
        'level3_subs': level3_subs,
        'progress': progress,
        'total_assignments': total_assignments,
        'completed_assignments': completed_assignments,
        'all_users': all_users,  # Add this line
    }
    
    return render(request, 'diagnostic_app/job_role_detail.html', context)
@login_required
def diagnostic_view(request, job_id):
    job = get_object_or_404(JobRole, id=job_id)
    
    # Check if user is assigned to this job
    if not RoleAssignment.objects.filter(job_role=job, user=request.user).exists():
        messages.error(request, 'You are not assigned to this job role.')
        return redirect('dashboard')
    
    # Check if already submitted
    existing = DiagnosticSubmission.objects.filter(job_role=job, user=request.user).first()
    if existing:
        messages.info(request, 'You have already submitted your assessment.')
        return redirect('submission_detail', submission_id=existing.id)
    
    if request.method == 'POST':
        try:
            print("Form submitted with POST data:", request.POST)
            
            # Parse boolean values
            def parse_bool(value):
                return value == 'true' if value in ['true', 'false'] else None
            
            # Parse integer values
            def parse_int(value):
                try:
                    return int(value) if value else None
                except (ValueError, TypeError):
                    return None
            
            # Create submission with basic data first
            submission = DiagnosticSubmission(
                job_role=job,
                user=request.user,
                decision=request.POST.get('decision'),
                decline_reason=request.POST.get('decline_reason', ''),
                decline_category=request.POST.get('decline_category', ''),
            )
            
            # Set role-specific questions based on user level
            user_level = request.user.get_level()
            
            if user_level == 1:
                # Level 1 questions (shared by all Level 1 roles)
                submission.q1_business_alignment = parse_int(request.POST.get('q1_business_alignment'))
                submission.q2_financial_risk = parse_int(request.POST.get('q2_financial_risk'))
                submission.q3_long_term_impact = parse_int(request.POST.get('q3_long_term_impact'))
                submission.q4_budget_approval = parse_bool(request.POST.get('q4_budget_approval'))
                submission.q5_strategic_priority = request.POST.get('q5_strategic_priority')
            
            elif user_level == 2:
                # Level 2 questions
                submission.q6_skill_availability = request.POST.get('q6_skill_availability')
                submission.q7_execution_feasibility = parse_int(request.POST.get('q7_execution_feasibility'))
                submission.q8_team_dependency = parse_int(request.POST.get('q8_team_dependency'))
                submission.q9_timeline_risk = request.POST.get('q9_timeline_risk')
                submission.q10_mentor_available = parse_bool(request.POST.get('q10_mentor_available'))
            
            else:  # Level 3
                # Level 3 questions
                submission.q11_talent_availability = request.POST.get('q11_talent_availability')
                submission.q12_cost_validation = parse_bool(request.POST.get('q12_cost_validation'))
                submission.q13_process_readiness = parse_int(request.POST.get('q13_process_readiness'))
                submission.q14_onboarding_capacity = parse_bool(request.POST.get('q14_onboarding_capacity'))
                submission.q15_market_competition = request.POST.get('q15_market_competition')
            
            # Save the submission (this will trigger calculate_risk() and generate_corrective_guidance())
            submission.save()
            
            # Update role assignment
            assignment = RoleAssignment.objects.get(job_role=job, user=request.user)
            assignment.is_completed = True
            assignment.save()
            
            messages.success(request, 'Assessment submitted successfully!')
            return redirect('submission_detail', submission_id=submission.id)
            
        except Exception as e:
            messages.error(request, f'Error submitting assessment: {str(e)}')
            print(f"Error details: {e}")
            import traceback
            traceback.print_exc()
    
    return render(request, 'diagnostic_app/questionnaire.html', {'job': job})

@login_required
def submission_detail_view(request, submission_id):
    submission = get_object_or_404(DiagnosticSubmission, id=submission_id)
    
    # Check permission
    if submission.user != request.user and request.user.get_level() != 1:
        messages.error(request, 'You can only view your own submissions.')
        return redirect('dashboard')
    
    context = {'submission': submission}
    return render(request, 'diagnostic_app/submission_detail.html', context)


# Notification Views
@login_required
def notifications_view(request):
    # Show only unread notifications for the current user.
    # The dashboard already shows up to 5 unread items; this page
    # is the full unread inbox so that "Mark All as Read" visibly clears it.
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')
    context = {'notifications': notifications}
    return render(request, 'diagnostic_app/notifications.html', context)


@login_required
def mark_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
    
    return redirect('notifications')


# Results View
@login_required
def results_view(request, job_id):
    job = get_object_or_404(JobRole, id=job_id)
    
    # Check if user is Level 1
    if request.user.get_level() != 1:
        messages.error(request, 'Only Level 1 users can view results.')
        return redirect('dashboard')
    
    submissions = DiagnosticSubmission.objects.filter(job_role=job)
    
    # Group submissions by level
    level1_subs = submissions.filter(user__role__in=['founder', 'co_founder'])
    level2_subs = submissions.filter(user__role__in=['ceo', 'cfo', 'cto', 'coo', 'project_head'])
    level3_subs = submissions.filter(user__role__in=['hr_manager', 'recruiter', 'hr_executive'])
    
    # Calculate overall progress
    total_assignments = RoleAssignment.objects.filter(job_role=job).count()
    completed_assignments = RoleAssignment.objects.filter(job_role=job, is_completed=True).count()
    progress = round((completed_assignments / total_assignments * 100) if total_assignments > 0 else 0, 1)
    
    context = {
        'job': job,
        'level1_subs': level1_subs,
        'level2_subs': level2_subs,
        'level3_subs': level3_subs,
        'progress': progress,
    }
    
    return render(request, 'diagnostic_app/results.html', context)