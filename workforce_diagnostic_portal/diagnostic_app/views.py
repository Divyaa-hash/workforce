from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.urls import reverse
from django.utils import timezone
from .forms import CustomUserCreationForm, LoginForm, JobRoleForm, DiagnosticForm
from .models import User, JobRole, DiagnosticSubmission, RoleAssignment, Notification, AuditLog

# Homepage View
def home_view(request):
    """Homepage view - displayed before login"""
    # If show_home parameter is explicitly set to true, show homepage regardless of authentication
    if request.GET.get('show_home') == 'true':
        if request.user.is_authenticated:
            return render(request, 'diagnostic_app/home_standalone.html')
        else:
            return render(request, 'diagnostic_app/home_public.html')
    
    # If user is authenticated and not explicitly requesting homepage, redirect to dashboard
    if request.user.is_authenticated:
        level = request.user.get_level()
        dashboard_url = reverse('dashboard')
        return redirect(f'{dashboard_url}?level={level}')
    
    # Show public homepage for non-authenticated users
    return render(request, 'diagnostic_app/home_public.html')

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
        ip_address = request.META.get('REMOTE_ADDR')

        if user is not None:
            print(f"User authenticated: {user.username}, actual role: {user.role}")

            # Check if selected role matches user's actual role
            if user.role == role:
                login(request, user)
                AuditLog.objects.create(
                    event_type='login_success',
                    user=user,
                    metadata={
                        'selected_role': role,
                        'actual_role': user.role,
                        'timestamp': timezone.now().isoformat(),
                    },
                    ip_address=ip_address,
                )
                messages.success(request, f'Welcome, {user.get_role_display()}!')
                level = user.get_level()
                dashboard_url = reverse('dashboard')
                return redirect(f'{dashboard_url}?level={level}')
            else:
                AuditLog.objects.create(
                    event_type='login_failure',
                    user=user,
                    metadata={
                        'username': username,
                        'selected_role': role,
                        'actual_role': user.role,
                        'reason': 'role_mismatch',
                    },
                    ip_address=ip_address,
                )
                messages.error(request, f'Please select correct role: {user.get_role_display()}')
        else:
            AuditLog.objects.create(
                event_type='login_failure',
                user=None,
                metadata={
                    'username': username,
                    'selected_role': role,
                    'reason': 'invalid_credentials',
                },
                ip_address=ip_address,
            )
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

    # Get recent audit logs for admins / Level 1 users
    recent_audit_logs = None
    if request.user.is_superuser or request.user.get_level() == 1:
        recent_audit_logs = AuditLog.objects.select_related('user').order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'jobs': jobs,
        'notifications': notifications,
        'recent_audit_logs': recent_audit_logs,
        'user_level': request.user.get_level(),
    }
    
    return render(request, 'diagnostic_app/dashboard.html', context)


@login_required
def analytics_view(request):
    """
    High-level analytics for Level 1 users (Founder / Co-Founder).
    """
    if request.user.get_level() != 1:
        messages.error(request, 'Only Level 1 users (Founders / Co-Founders) can view analytics.')
        return redirect('dashboard')

    # Job role stats
    total_jobs = JobRole.objects.count()
    jobs_by_status = (
        JobRole.objects
        .values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )

    # Diagnostic submission stats
    total_submissions = DiagnosticSubmission.objects.count()
    submissions_by_decision = (
        DiagnosticSubmission.objects
        .values('decision')
        .annotate(count=Count('id'))
        .order_by('decision')
    )
    submissions_by_risk = (
        DiagnosticSubmission.objects
        .values('risk_level')
        .annotate(count=Count('id'))
        .order_by('risk_level')
    )

    context = {
        'total_jobs': total_jobs,
        'jobs_by_status': jobs_by_status,
        'total_submissions': total_submissions,
        'submissions_by_decision': submissions_by_decision,
        'submissions_by_risk': submissions_by_risk,
    }

    return render(request, 'diagnostic_app/analytics.html', context)

# Job Role Views
@login_required
def create_job_role_view(request):
    # Check if user can create job roles
    if not request.user.can_create_job_roles():
        messages.error(request, 'Only Founders and Co-Founders can create job roles.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        print(f"POST request received from user: {request.user.username} ({request.user.role})")
        try:
            form = JobRoleForm(request.POST, user=request.user)
            print(f"Form is valid: {form.is_valid()}")
            if not form.is_valid():
                print(f"Form errors: {form.errors}")
            
            if form.is_valid():
                print("Form validation passed, proceeding with job creation...")
                # Check for duplicate job title to prevent double submissions
                title = form.cleaned_data['title']
                department = form.cleaned_data['department']
                
                print(f"Creating job: {title} in {department}")
                
                # Check if a job with same title and department already exists in last 5 minutes
                recent_duplicate = JobRole.objects.filter(
                    title__iexact=title.strip(),
                    department__iexact=department.strip(),
                    created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
                ).exists()
                
                if recent_duplicate:
                    print(f"Recent duplicate found for {title} in {department}")
                    messages.warning(request, f'A job role "{title}" in {department} was recently created. Please check the job roles list.')
                    return redirect('job_roles')
                
                # Save the job role
                print("Saving job role...")
                job_role = form.save(commit=False)
                job_role.created_by = request.user
                job_role.status = 'active'
                job_role.save()
                print(f"Job role saved with ID: {job_role.id}")
                
                # Auto-assign roles based on level
                print("Auto-assigning users...")
                auto_assign_users(job_role)
                
                # Create role assignment notifications
                print("Creating role assignment notifications...")
                notify_role_assignment(job_role)
                
                messages.success(request, f'Job role "{job_role.title}" created successfully!')
                print("Job creation completed successfully")
                return redirect('job_roles')
        except Exception as e:
            print(f"Error during job creation: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error creating job role: {str(e)}')
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
            job_role=job_role,
            notification_type='assessment_completed'
        )


@login_required
def job_roles_view(request):
    # Temporary fix: Show all jobs to all users for debugging
    jobs = JobRole.objects.all().order_by('-created_at')
    
    # TODO: Revert this back to level-based filtering after debugging
    # if request.user.get_level() == 1:
    #     # Level 1 sees all jobs
    #     jobs = JobRole.objects.all().order_by('-created_at')
    # else:
    #     # Other levels see only their assigned jobs
    #     assigned_job_ids = RoleAssignment.objects.filter(user=request.user).values_list('job_role_id', flat=True)
    #     jobs = JobRole.objects.filter(id__in=assigned_job_ids).order_by('-created_at')
    
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
            
            # Set role-specific questions based on user role
            user_role = request.user.role
            user_level = request.user.get_level()
            
            if user_role == 'founder':
                # Founder-specific questions
                submission.q_founder_vision_alignment = parse_int(request.POST.get('q_founder_vision_alignment'))
                submission.q_founder_strategic_fit = parse_int(request.POST.get('q_founder_strategic_fit'))
                submission.q_founder_market_positioning = parse_int(request.POST.get('q_founder_market_positioning'))
                submission.q_founder_resource_priority = request.POST.get('q_founder_resource_priority')
                submission.q_founder_equity_consideration = request.POST.get('q_founder_equity_consideration')
            
            elif user_role == 'co_founder':
                # Co-Founder-specific questions
                submission.q_cofounder_partnership_dynamics = parse_int(request.POST.get('q_cofounder_partnership_dynamics'))
                submission.q_cofounder_complementary_skills = parse_int(request.POST.get('q_cofounder_complementary_skills'))
                submission.q_cofounder_team_chemistry = parse_int(request.POST.get('q_cofounder_team_chemistry'))
                submission.q_cofounder_decision_making = request.POST.get('q_cofounder_decision_making')
                submission.q_cofounder_culture_fit = parse_int(request.POST.get('q_cofounder_culture_fit'))
            
            elif user_role == 'cfo':
                # CFO-specific questions
                submission.q0_roi_analysis = parse_int(request.POST.get('q0_roi_analysis'))
                submission.q0_cash_flow_impact = parse_int(request.POST.get('q0_cash_flow_impact'))
                submission.q0_budget_alignment = parse_bool(request.POST.get('q0_budget_alignment'))
                submission.q0_funding_source = request.POST.get('q0_funding_source')
            
            elif user_level == 1:
                # CEO or other Level 1 questions (shared by all Level 1 roles except founder/co_founder/cfo)
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


@login_required
def edit_submission_view(request, submission_id):
    submission = get_object_or_404(DiagnosticSubmission, id=submission_id)
    
    # Check permission - only submission owner can edit
    if submission.user != request.user:
        messages.error(request, 'You can only edit your own submissions.')
        return redirect('submission_detail', submission_id=submission_id)
    
    # Check if submission is recent (within 24 hours)
    from django.utils import timezone
    time_diff = timezone.now() - submission.submitted_at
    if time_diff.total_seconds() > 24 * 60 * 60:  # 24 hours
        messages.error(request, 'You can only edit submissions within 24 hours of submission.')
        return redirect('submission_detail', submission_id=submission_id)
    
    if request.method == 'POST':
        try:
            # Parse boolean values
            def parse_bool(value):
                return value == 'true' if value in ['true', 'false'] else None
            
            # Parse integer values
            def parse_int(value):
                try:
                    return int(value) if value else None
                except (ValueError, TypeError):
                    return None
            
            # Update basic submission data
            submission.decision = request.POST.get('decision')
            submission.decline_reason = request.POST.get('decline_reason', '')
            submission.decline_category = request.POST.get('decline_category', '')
            
            # Update role-specific questions based on user role
            user_role = request.user.role
            user_level = request.user.get_level()
            
            if user_role == 'founder':
                # Founder-specific questions
                submission.q_founder_vision_alignment = parse_int(request.POST.get('q_founder_vision_alignment'))
                submission.q_founder_strategic_fit = parse_int(request.POST.get('q_founder_strategic_fit'))
                submission.q_founder_market_positioning = parse_int(request.POST.get('q_founder_market_positioning'))
                submission.q_founder_resource_priority = request.POST.get('q_founder_resource_priority')
                submission.q_founder_equity_consideration = request.POST.get('q_founder_equity_consideration')
            
            elif user_role == 'co_founder':
                # Co-Founder-specific questions
                submission.q_cofounder_partnership_dynamics = parse_int(request.POST.get('q_cofounder_partnership_dynamics'))
                submission.q_cofounder_complementary_skills = parse_int(request.POST.get('q_cofounder_complementary_skills'))
                submission.q_cofounder_team_chemistry = parse_int(request.POST.get('q_cofounder_team_chemistry'))
                submission.q_cofounder_decision_making = request.POST.get('q_cofounder_decision_making')
                submission.q_cofounder_culture_fit = parse_int(request.POST.get('q_cofounder_culture_fit'))
            
            elif user_role == 'cfo':
                # CFO-specific questions
                submission.q0_roi_analysis = parse_int(request.POST.get('q0_roi_analysis'))
                submission.q0_cash_flow_impact = parse_int(request.POST.get('q0_cash_flow_impact'))
                submission.q0_budget_alignment = parse_bool(request.POST.get('q0_budget_alignment'))
                submission.q0_funding_source = request.POST.get('q0_funding_source')
            
            elif user_level == 1:
                # CEO or other Level 1 questions
                submission.q1_business_alignment = parse_int(request.POST.get('q1_business_alignment'))
                submission.q2_financial_risk = parse_int(request.POST.get('q2_financial_risk'))
                submission.q3_long_term_impact = parse_int(request.POST.get('q3_long_term_impact'))
                submission.q4_budget_approval = parse_bool(request.POST.get('q4_budget_approval'))
                submission.q5_strategic_priority = request.POST.get('q5_strategic_priority')
            
            elif user_level == 2:
                # Level 2 questions - handle new role-specific fields
                if user_role == 'ceo':
                    submission.q_ceo_leadership_impact = parse_int(request.POST.get('q_ceo_leadership_impact'))
                    submission.q_ceo_strategic_priority = request.POST.get('q_ceo_strategic_priority')
                    submission.q_ceo_cross_functional_impact = parse_int(request.POST.get('q_ceo_cross_functional_impact'))
                    submission.q_ceo_board_alignment = request.POST.get('q_ceo_board_alignment')
                    submission.q_ceo_success_metrics = parse_bool(request.POST.get('q_ceo_success_metrics'))
                elif user_role == 'cfo':
                    submission.q_cfo_roi_confidence = parse_int(request.POST.get('q_cfo_roi_confidence'))
                    submission.q_cfo_budget_flexibility = request.POST.get('q_cfo_budget_flexibility')
                    submission.q_cfo_financial_risk = parse_int(request.POST.get('q_cfo_financial_risk'))
                    submission.q_cfo_cash_flow_impact = request.POST.get('q_cfo_cash_flow_impact')
                    submission.q_cfo_compliance = parse_bool(request.POST.get('q_cfo_compliance'))
                elif user_role == 'cto':
                    submission.q_cto_technical_feasibility = parse_int(request.POST.get('q_cto_technical_feasibility'))
                    submission.q_cto_stack_alignment = request.POST.get('q_cto_stack_alignment')
                    submission.q_cto_innovation_impact = parse_int(request.POST.get('q_cto_innovation_impact'))
                    submission.q_cto_tech_debt = request.POST.get('q_cto_tech_debt')
                    submission.q_cto_scalability = parse_bool(request.POST.get('q_cto_scalability'))
                elif user_role == 'coo':
                    submission.q_coo_operational_efficiency = parse_int(request.POST.get('q_coo_operational_efficiency'))
                    submission.q_coo_process_integration = request.POST.get('q_coo_process_integration')
                    submission.q_coo_resource_optimization = parse_int(request.POST.get('q_coo_resource_optimization'))
                    submission.q_coo_workflow_disruption = request.POST.get('q_coo_workflow_disruption')
                    submission.q_coo_standardization = parse_bool(request.POST.get('q_coo_standardization'))
                elif user_role == 'project_head':
                    submission.q_ph_deliverability = parse_int(request.POST.get('q_ph_deliverability'))
                    submission.q_ph_team_capacity = request.POST.get('q_ph_team_capacity')
                    submission.q_ph_timeline_realism = parse_int(request.POST.get('q_ph_timeline_realism'))
                    submission.q_ph_dependency_management = request.POST.get('q_ph_dependency_management')
                    submission.q_ph_resource_clarity = parse_bool(request.POST.get('q_ph_resource_clarity'))
            
            else:  # Level 3
                # Level 3 questions - handle new role-specific fields
                if user_role == 'hr_manager':
                    submission.q_hr_culture_impact = parse_int(request.POST.get('q_hr_culture_impact'))
                    submission.q_hr_development_potential = request.POST.get('q_hr_development_potential')
                    submission.q_hr_retention_risk = parse_int(request.POST.get('q_hr_retention_risk'))
                    submission.q_hr_training_infrastructure = parse_bool(request.POST.get('q_hr_training_infrastructure'))
                    submission.q_hr_performance_integration = request.POST.get('q_hr_performance_integration')
                elif user_role == 'recruiter':
                    submission.q_rec_talent_availability = parse_int(request.POST.get('q_rec_talent_availability'))
                    submission.q_rec_sourcing_strategy = request.POST.get('q_rec_sourcing_strategy')
                    submission.q_rec_time_to_hire = parse_int(request.POST.get('q_rec_time_to_hire'))
                    submission.q_rec_compensation_competitive = request.POST.get('q_rec_compensation_competitive')
                    submission.q_rec_pipeline_ready = parse_bool(request.POST.get('q_rec_pipeline_ready'))
                elif user_role == 'hr_executive':
                    submission.q_hre_onboarding_readiness = parse_int(request.POST.get('q_hre_onboarding_readiness'))
                    submission.q_hre_compliance_status = request.POST.get('q_hre_compliance_status')
                    submission.q_hre_documentation = parse_int(request.POST.get('q_hre_documentation'))
                    submission.q_hre_systems_capacity = request.POST.get('q_hre_systems_capacity')
                    submission.q_hre_reporting_framework = parse_bool(request.POST.get('q_hre_reporting_framework'))
            
            # Update submission time and save
            submission.submitted_at = timezone.now()
            submission.save()
            
            # Create audit log
            AuditLog.objects.create(
                event_type='submission_updated',
                user=request.user,
                entity_type='diagnostic_submission',
                entity_id=submission.id,
                metadata={'original_submission_id': submission.id}
            )
            
            messages.success(request, 'Assessment updated successfully!')
            return redirect('submission_detail', submission_id=submission.id)
            
        except Exception as e:
            messages.error(request, f'Error updating assessment: {str(e)}')
            print(f"Error details: {e}")
            import traceback
            traceback.print_exc()
    
    context = {
        'job': submission.job_role,
        'submission': submission,
        'is_edit': True
    }
    return render(request, 'diagnostic_app/questionnaire.html', context)


@login_required
def delete_submission_view(request, submission_id):
    submission = get_object_or_404(DiagnosticSubmission, id=submission_id)
    
    # Check permission - only submission owner can delete
    if submission.user != request.user:
        messages.error(request, 'You can only delete your own submissions.')
        return redirect('submission_detail', submission_id=submission_id)
    
    # Check if submission is recent (within 24 hours)
    from django.utils import timezone
    time_diff = timezone.now() - submission.submitted_at
    if time_diff.total_seconds() > 24 * 60 * 60:  # 24 hours
        messages.error(request, 'You can only delete submissions within 24 hours of submission.')
        return redirect('submission_detail', submission_id=submission_id)
    
    if request.method == 'POST':
        job_role = submission.job_role
        submission_id = submission.id
        
        # Create audit log before deletion
        AuditLog.objects.create(
            event_type='submission_deleted',
            user=request.user,
            entity_type='diagnostic_submission',
            entity_id=submission_id,
            metadata={
                'job_role_title': job_role.title,
                'decision': submission.decision
            }
        )
        
        submission.delete()
        
        messages.success(request, 'Assessment deleted successfully!')
        return redirect('job_role_detail', job_id=job_role.id)
    
    # For GET request, show confirmation page
    context = {
        'submission': submission,
        'job': submission.job_role
    }
    return render(request, 'diagnostic_app/delete_submission_confirm.html', context)


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
    from .rules_engine import OverallDecisionEngine

    job = get_object_or_404(JobRole, id=job_id)

    submissions = DiagnosticSubmission.objects.filter(job_role=job)

    # Group submissions by level
    level1_subs = submissions.filter(user__role__in=['founder', 'co_founder'])
    level2_subs = submissions.filter(user__role__in=['ceo', 'cfo', 'cto', 'coo', 'project_head'])
    level3_subs = submissions.filter(user__role__in=['hr_manager', 'recruiter', 'hr_executive'])

    # Calculate overall progress
    total_assignments = RoleAssignment.objects.filter(job_role=job).count()
    completed_assignments = RoleAssignment.objects.filter(job_role=job, is_completed=True).count()
    progress = round((completed_assignments / total_assignments * 100) if total_assignments > 0 else 0, 1)

    # Generate and log final decision
    ip_address = request.META.get('REMOTE_ADDR')
    recommendation = OverallDecisionEngine.get_final_recommendation(
        job, user=request.user, ip_address=ip_address
    )

    context = {
        'job': job,
        'level1_subs': level1_subs,
        'level2_subs': level2_subs,
        'level3_subs': level3_subs,
        'progress': progress,
        'final_recommendation': recommendation,
        'recommendation': recommendation,  # Keep for backward compatibility
    }

    return render(request, 'diagnostic_app/results.html', context)


@login_required
def audit_logs_view(request):
    """Simple audit log viewer for admins / founders / co-founders."""
    if not (
        request.user.is_superuser
        or request.user.role in ['founder', 'co_founder']
    ):
        messages.error(request, 'Only admins, founders and co-founders can view audit logs.')
        return redirect('dashboard')

    logs = AuditLog.objects.select_related('user').all()

    event_type = request.GET.get('event_type', '').strip()
    username = request.GET.get('username', '').strip()

    if event_type:
        logs = logs.filter(event_type=event_type)
    if username:
        logs = logs.filter(user__username__icontains=username)

    logs = logs.order_by('-created_at')[:200]

    context = {
        'logs': logs,
        'event_type_filter': event_type,
        'username_filter': username,
    }

    return render(request, 'diagnostic_app/audit_logs.html', context)


@login_required
def audit_log_detail_view(request, log_id):
    """Detailed view for a single audit log entry (admin / founders / co-founders)."""
    if not (
        request.user.is_superuser
        or request.user.role in ['founder', 'co_founder']
    ):
        messages.error(request, 'Only admins, founders and co-founders can view audit logs.')
        return redirect('dashboard')

    log = get_object_or_404(AuditLog.objects.select_related('user'), id=log_id)

    context = {
        'log': log,
    }

    return render(request, 'diagnostic_app/audit_log_detail.html', context)


@login_required
def delete_job_role_view(request, job_id):
    """Delete job role - only Founder can delete"""
    # Only Founder can delete job roles
    if request.user.role != 'founder':
        messages.error(request, 'Only the Founder can delete job roles.')
        return redirect('job_roles')
    
    try:
        job = JobRole.objects.get(id=job_id)
    except JobRole.DoesNotExist:
        messages.error(request, 'Job role not found.')
        return redirect('job_roles')
    except Exception as e:
        messages.error(request, f'Error retrieving job role: {str(e)}')
        return redirect('job_roles')
    
    if request.method == 'POST':
        try:
            job_title = job.title
            
            # Send deletion notifications to all users BEFORE deleting
            all_users = User.objects.all()
            deletion_notifications = []
            for user in all_users:
                if user != request.user:  # Don't notify the founder who deleted it
                    deletion_notifications.append(
                        Notification(
                            user=user,
                            message=f'Job role "{job_title}" has been deleted by {request.user.get_full_name() or request.user.username}',
                            job_role=job,
                            notification_type='job_deleted'
                        )
                    )
            
            # Create all notifications
            Notification.objects.bulk_create(deletion_notifications)
            
            job.delete()
            
            # Log the deletion
            AuditLog.objects.create(
                user=request.user,
                event_type='job_role_deleted',
                entity_type='job_role',
                entity_id=job.id,
                metadata={
                    'job_title': job_title,
                    'action': 'deleted'
                }
            )
            
            messages.success(request, f'Job role "{job_title}" has been deleted successfully.')
            return redirect('job_roles')
        except Exception as e:
            messages.error(request, f'Error deleting job role: {str(e)}')
            return redirect('job_roles')
    
    try:
        context = {
            'job': job,
        }
        return render(request, 'diagnostic_app/delete_job_role_confirm.html', context)
    except Exception as e:
        messages.error(request, f'Error rendering delete confirmation: {str(e)}')
        return redirect('job_roles')