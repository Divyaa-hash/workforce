from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('founder', 'Founder'),
        ('co_founder', 'Co-Founder'),
        ('ceo', 'CEO'),
        ('cfo', 'CFO'),
        ('cto', 'CTO / Tech Lead'),
        ('coo', 'COO'),
        ('project_head', 'Project Head / Team Lead'),
        ('hr_manager', 'HR Manager / People Operations'),
        ('recruiter', 'Recruiter'),
        ('hr_executive', 'HR Executive'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    
    def get_level(self):
        """Get the decision level based on role"""
        level_map = {
            'founder': 1, 'co_founder': 1,
            'ceo': 2, 'cfo': 2,
            'cto': 2, 'coo': 2, 'project_head': 2,
            'hr_manager': 3, 'recruiter': 3, 'hr_executive': 3
        }
        return level_map.get(self.role, 0)
    
    def can_create_job_roles(self):
        """Check if user can create job roles"""
        return self.role in ['founder', 'co_founder']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class JobRole(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    description = models.TextField()
    required_skills = models.TextField()
    experience_level = models.CharField(max_length=50)
    budget_range = models.CharField(max_length=100)
    urgency = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    def __str__(self):
        return self.title
    
    def get_assigned_users(self):
        """Get all users assigned to this job role"""
        return User.objects.filter(assignments__job_role=self)
    
    def get_progress_percentage(self):
        """Calculate completion percentage"""
        total_assignments = RoleAssignment.objects.filter(job_role=self).count()
        if total_assignments == 0:
            return 0
        
        completed_assignments = RoleAssignment.objects.filter(job_role=self, is_completed=True).count()
        return round((completed_assignments / total_assignments) * 100, 1)


class RoleAssignment(models.Model):
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['job_role', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.job_role.title}"
    
    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)


class DiagnosticSubmission(models.Model):
    RISK_CHOICES = [
        ('low', '🟢 Low Risk'),
        ('medium', '🟡 Medium Risk'),
        ('high', '🔴 High Risk'),
    ]
    
    DECISION_CHOICES = [
        ('approve', '✅ Approve'),
        ('decline', '❌ Decline'),
    ]
    
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Level 1 Questions (CFO/Founder/Co-Founder/CEO)
    # Financial Assessment Questions (CFO Specific)
    q0_roi_analysis = models.IntegerField(verbose_name='ROI Projection Score', choices=[(i, str(i)) for i in range(1, 6)], 
                                         help_text='Rate the projected ROI (1=Very Low, 5=Very High)', 
                                         null=True, blank=True)
    q0_cash_flow_impact = models.IntegerField(verbose_name='Cash Flow Impact', choices=[(i, str(i)) for i in range(1, 6)], 
                                            help_text='Rate the impact on cash flow (1=Negative, 5=Positive)', 
                                            null=True, blank=True)
    q0_budget_alignment = models.BooleanField(verbose_name='Aligned with Annual Budget', 
                                            help_text='Is this role accounted for in the current fiscal year budget?', 
                                            null=True, blank=True)
    q0_funding_source = models.CharField(verbose_name='Funding Source', max_length=50, 
                                       choices=[
                                           ('operational', 'Operational Budget'),
                                           ('contingency', 'Contingency Fund'),
                                           ('new_funding', 'Requires New Funding'),
                                           ('cost_center', 'Cost Center Budget')
                                       ], null=True, blank=True)
    
    # Business Alignment Questions (Shared with other Level 1 roles)
    q1_business_alignment = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    q2_financial_risk = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    q3_long_term_impact = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    q4_budget_approval = models.BooleanField(null=True, blank=True)
    q5_strategic_priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')
    ], null=True, blank=True)
    
    # Level 2 Questions (CTO/COO/Project Head)
    q6_skill_availability = models.CharField(max_length=10, choices=[
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')
    ], null=True, blank=True)
    q7_execution_feasibility = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    q8_team_dependency = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    q9_timeline_risk = models.CharField(max_length=10, choices=[
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')
    ], null=True, blank=True)
    q10_mentor_available = models.BooleanField(null=True, blank=True)
    
    # Level 3 Questions (HR Roles)
    q11_talent_availability = models.CharField(max_length=10, choices=[
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')
    ], null=True, blank=True)
    q12_cost_validation = models.BooleanField(null=True, blank=True)
    q13_process_readiness = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    q14_onboarding_capacity = models.BooleanField(null=True, blank=True)
    q15_market_competition = models.CharField(max_length=10, choices=[
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')
    ], null=True, blank=True)
    
    # Decision and Risk
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES)
    decline_reason = models.TextField(blank=True)
    decline_category = models.CharField(max_length=50, blank=True, choices=[
        ('budget_constraint', 'Budget constraint'),
        ('skill_unavailability', 'Skill unavailability'),
        ('timeline_risk', 'Timeline risk'),
        ('team_dependency', 'Team dependency'),
        ('business_misalignment', 'Business misalignment'),
        ('operational_gap', 'Operational readiness gap'),
    ])
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES)
    corrective_guidance = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.job_role.title} - {self.get_decision_display()}"
    
    def save(self, *args, **kwargs):
        """Override save to calculate risk and guidance"""
        # Calculate risk before saving
        self.calculate_risk()
        
        # Generate corrective guidance if declined
        if self.decision == 'decline':
            self.generate_corrective_guidance()
        
        super().save(*args, **kwargs)
    
    def calculate_risk(self):
        """Rule-based risk calculation"""
        user_level = self.user.get_level()
        
        if user_level == 1:  # Level 1 roles
            risk_score = 0
            
            # Common Level 1 Rules
            # Rule 1: Budget approval
            if not self.q4_budget_approval:
                risk_score += 3
            
            # Rule 2: Financial risk
            if self.q2_financial_risk and self.q2_financial_risk >= 4:
                risk_score += 2
            
            # Rule 3: Strategic priority
            if self.q5_strategic_priority == 'low':
                risk_score += 1
            elif self.q5_strategic_priority == 'high':
                risk_score -= 1
            
            # Rule 4: Business alignment
            if self.q1_business_alignment and self.q1_business_alignment <= 2:
                risk_score += 2
            
            # Rule 5: Long-term impact
            if self.q3_long_term_impact and self.q3_long_term_impact <= 2:
                risk_score += 1
            
            # Determine risk level
            if risk_score >= 3:
                self.risk_level = 'high'
            elif risk_score >= 1:
                self.risk_level = 'medium'
            else:
                self.risk_level = 'low'
                
        elif user_level == 2:  # Level 2 roles
            risk_score = 0
            
            # Rule 1: Skill availability
            if self.q6_skill_availability == 'low':
                risk_score += 2
            elif self.q6_skill_availability == 'medium':
                risk_score += 1
            
            # Rule 2: Timeline risk
            if self.q9_timeline_risk == 'high':
                risk_score += 2
            elif self.q9_timeline_risk == 'medium':
                risk_score += 1
            
            # Rule 3: Mentor availability
            if not self.q10_mentor_available:
                risk_score += 1
            
            # Rule 4: Team dependency
            if self.q8_team_dependency and self.q8_team_dependency >= 4:
                risk_score += 1
            
            # Rule 5: Execution feasibility
            if self.q7_execution_feasibility and self.q7_execution_feasibility <= 2:
                risk_score += 1
            
            # Determine risk level
            if risk_score >= 3:
                self.risk_level = 'high'
            elif risk_score >= 1:
                self.risk_level = 'medium'
            else:
                self.risk_level = 'low'
                
        else:  # Level 3 roles
            risk_score = 0
            
            # Rule 1: Talent availability
            if self.q11_talent_availability == 'low':
                risk_score += 2
            elif self.q11_talent_availability == 'medium':
                risk_score += 1
            
            # Rule 2: Cost validation
            if not self.q12_cost_validation:
                risk_score += 2
            
            # Rule 3: Market competition
            if self.q15_market_competition == 'high':
                risk_score += 1
            
            # Rule 4: Process readiness
            if self.q13_process_readiness and self.q13_process_readiness <= 2:
                risk_score += 1
            
            # Rule 5: Onboarding capacity
            if not self.q14_onboarding_capacity:
                risk_score += 1
            
            # Determine risk level
            if risk_score >= 3:
                self.risk_level = 'high'
            elif risk_score >= 1:
                self.risk_level = 'medium'
            else:
                self.risk_level = 'low'
    
    def generate_corrective_guidance(self):
        """Generate corrective guidance based on decline reason"""
        guidance_map = {
            'budget_constraint': 'Consider increasing budget or reducing role scope. Also explore contract-to-hire options.',
            'skill_unavailability': 'Revise skill expectations, provide training, or consider outsourcing specific tasks.',
            'timeline_risk': 'Delay hiring timeline, hire contract resource for immediate needs, or redistribute workload.',
            'team_dependency': 'Assign experienced mentor, restructure team responsibilities, or provide cross-training.',
            'business_misalignment': 'Re-evaluate business strategy, conduct market analysis, or re-align role with business goals.',
            'operational_gap': 'Improve onboarding process, set up necessary infrastructure, or define clear processes first.',
        }
        
        if self.decline_category in guidance_map:
            self.corrective_guidance = guidance_map[self.decline_category]
        else:
            self.corrective_guidance = 'Review and address the specific concerns raised. Consider consulting with other team members.'
    
    def get_risk_color(self):
        """Get CSS color for risk level"""
        if self.risk_level == 'high':
            return '#ef4444'  # Red
        elif self.risk_level == 'medium':
            return '#f59e0b'  # Orange/Yellow
        else:
            return '#10b981'  # Green
    
    def get_risk_icon(self):
        """Get icon for risk level"""
        if self.risk_level == 'high':
            return '🔴'
        elif self.risk_level == 'medium':
            return '🟡'
        else:
            return '🟢'
    
    def is_approved(self):
        """Check if submission is approved"""
        return self.decision == 'approve'
    
    def get_user_level(self):
        """Get user's decision level"""
        return self.user.get_level()
    
    def get_level_display(self):
        """Get display name for user's level"""
        level = self.get_user_level()
        if level == 1:
            return "Strategic / Ownership"
        elif level == 2:
            return "Execution / Delivery"
        else:
            return "HR / Operations Support"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()
    
    def get_time_ago(self):
        """Get human-readable time ago"""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds // 3600 > 0:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds // 60 > 0:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"


# Signal to create notifications when job role is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=JobRole)
def create_job_role_notifications(sender, instance, created, **kwargs):
    """Create notifications when a new job role is created"""
    if created:
        # Get all users who should be notified
        users_to_notify = User.objects.filter(
            models.Q(role__in=['founder', 'co_founder']) |  # Level 1
            models.Q(role__in=['ceo', 'cfo', 'cto', 'coo', 'project_head']) |   # Level 2
            models.Q(role__in=['hr_manager', 'recruiter', 'hr_executive'])  # Level 3
        ).distinct()
        
        for user in users_to_notify:
            Notification.objects.create(
                user=user,
                message=f"New job role created: {instance.title}",
                job_role=instance
            )


@receiver(post_save, sender=DiagnosticSubmission)
def create_submission_notifications(sender, instance, created, **kwargs):
    """Create notifications when a submission is made"""
    if created:
        # Notify Level 1 users if submission is a decline
        if instance.decision == 'decline' and instance.user.get_level() != 1:
            level1_users = User.objects.filter(role__in=['founder', 'co_founder'])
            for user in level1_users:
                Notification.objects.create(
                    user=user,
                    message=f"{instance.user.get_role_display()} declined job role: {instance.job_role.title}",
                    job_role=instance.job_role
                )
        
        # Notify all assigned users when job role is fully assessed
        job_role = instance.job_role
        total_assignments = RoleAssignment.objects.filter(job_role=job_role).count()
        completed_assignments = RoleAssignment.objects.filter(job_role=job_role, is_completed=True).count()
        
        if total_assignments > 0 and completed_assignments == total_assignments:
            # All assessments are complete
            assigned_users = job_role.get_assigned_users()
            for user in assigned_users:
                Notification.objects.create(
                    user=user,
                    message=f"All assessments completed for job role: {job_role.title}",
                    job_role=job_role
                )