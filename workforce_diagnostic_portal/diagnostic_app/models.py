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
    
    def can_view_analytics(self):
        """Check if user can view analytics"""
        return self.get_level() <= 2  # Level 1 and 2
    
    def can_view_audit_logs(self):
        """Check if user can view audit logs"""
        return self.role in ['founder', 'co_founder'] or self.is_superuser
    
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role in ['founder', 'co_founder'] or self.is_superuser
    
    def can_access_reports(self):
        """Check if user can access reports"""
        return self.get_level() <= 2  # Level 1 and 2
    
    def can_view_system_settings(self):
        """Check if user can view system settings"""
        return self.role in ['founder', 'co_founder'] or self.is_superuser
    
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
    
    def delete(self, *args, **kwargs):
        """Override delete to clean up deletion notifications"""
        # Clean up deletion notifications for this job role
        try:
            Notification.objects.filter(
                job_role=self,
                notification_type='job_deleted'
            ).delete()
        except Exception as e:
            print(f"Error cleaning up notifications: {e}")
        
        # Call the original delete method
        super().delete(*args, **kwargs)


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
    
    # Business Alignment Questions (Shared with other Level 1 roles - CEO)
    q1_business_alignment = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    q2_financial_risk = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    q3_long_term_impact = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    q4_budget_approval = models.BooleanField(null=True, blank=True)
    q5_strategic_priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')
    ], null=True, blank=True)
    
    # Founder-Specific Questions (10 Strong Strategic Questions)
    q_founder_market_validation = models.IntegerField(verbose_name='Market Opportunity Validation', choices=[(i, str(i)) for i in range(1, 6)],
                                                    help_text='How validated is the market opportunity this role addresses? (1=Unvalidated, 5=Highly Validated with Customer Traction)',
                                                    null=True, blank=True)
    q_founder_competitive_moat = models.IntegerField(verbose_name='Competitive Moat Creation', choices=[(i, str(i)) for i in range(1, 6)],
                                                   help_text='How strongly will this role create or strengthen your competitive moat? (1=No Moat, 5=Significant Defensible Moat)',
                                                   null=True, blank=True)
    q_founder_unit_economics = models.IntegerField(verbose_name='Unit Economics Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                                 help_text='How will this role impact your unit economics and profitability? (1=Negative Impact, 5=Significantly Improves Unit Economics)',
                                                 null=True, blank=True)
    q_founder_talent_amplification = models.IntegerField(verbose_name='Talent Amplification Factor', choices=[(i, str(i)) for i in range(1, 6)],
                                                       help_text='How much will this role amplify the effectiveness of your existing team? (1=No Amplification, 5=10x Team Effectiveness)',
                                                       null=True, blank=True)
    q_founder_capital_efficiency = models.CharField(verbose_name='Capital Efficiency', max_length=20,
                                                  choices=[
                                                      ('immediate', 'Immediate ROI (0-3 months)'),
                                                      ('short_term', 'Short-term ROI (3-6 months)'),
                                                      ('medium_term', 'Medium-term ROI (6-12 months)'),
                                                      ('long_term', 'Long-term ROI (12+ months)'),
                                                      ('strategic', 'Strategic Investment (No direct ROI expected)')
                                                  ], null=True, blank=True)
    q_founder_scalability_leverage = models.IntegerField(verbose_name='Scalability Leverage', choices=[(i, str(i)) for i in range(1, 6)],
                                                       help_text='How well does this role scale with business growth? (1=Doesn\'t Scale, 5=Scales Exponentially)',
                                                       null=True, blank=True)
    q_founder_risk_mitigation = models.IntegerField(verbose_name='Risk Mitigation Value', choices=[(i, str(i)) for i in range(1, 6)],
                                                  help_text='How much does this role mitigate key business risks? (1=No Risk Mitigation, 5=Eliminates Critical Risk)',
                                                  null=True, blank=True)
    q_founder_network_effects = models.BooleanField(verbose_name='Network Effect Creation',
                                                  help_text='Will this role create or strengthen network effects for your business?',
                                                  null=True, blank=True)
    q_founder_strategic_options = models.IntegerField(verbose_name='Strategic Option Value', choices=[(i, str(i)) for i in range(1, 6)],
                                                    help_text='How much strategic option value does this role create for future opportunities? (1=No Option Value, 5=Significant Strategic Options)',
                                                    null=True, blank=True)
    q_founder_time_leverage = models.IntegerField(verbose_name='Founder Time Leverage', choices=[(i, str(i)) for i in range(1, 6)],
                                               help_text='How much will this role leverage your time as founder? (1=Consumes More Time, 5=Frees Up 80%+ of Your Time)',
                                               null=True, blank=True)
    
    # Co-Founder-Specific Questions (Enhanced to 10 questions)
    q_cofounder_partnership_dynamics = models.IntegerField(verbose_name='Partnership Dynamics', choices=[(i, str(i)) for i in range(1, 6)],
                                                           help_text='How well does this role complement partnership dynamics? (1=Poor, 5=Excellent)', 
                                                           null=True, blank=True)
    q_cofounder_complementary_skills = models.IntegerField(verbose_name='Complementary Skills', choices=[(i, str(i)) for i in range(1, 6)],
                                                          help_text='How complementary are the skills to existing team? (1=Overlap, 5=Highly Complementary)', 
                                                          null=True, blank=True)
    q_cofounder_team_chemistry = models.IntegerField(verbose_name='Team Chemistry', choices=[(i, str(i)) for i in range(1, 6)],
                                                     help_text='How well will this role integrate with team chemistry? (1=Poor, 5=Excellent)', 
                                                     null=True, blank=True)
    q_cofounder_decision_making = models.CharField(verbose_name='Decision-Making Alignment', max_length=10,
                                                  choices=[
                                                      ('low', 'Low'),
                                                      ('medium', 'Medium'),
                                                      ('high', 'High')
                                                  ], null=True, blank=True)
    q_cofounder_culture_fit = models.IntegerField(verbose_name='Culture and Values Alignment', choices=[(i, str(i)) for i in range(1, 6)],
                                                 help_text='How well aligned with company culture and values? (1=Poor, 5=Excellent)', 
                                                 null=True, blank=True)
    
    # Additional 5 Enhanced Co-Founder Questions
    q_cofounder_workload_distribution = models.IntegerField(verbose_name='Workload Distribution Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                                           help_text='How will this role affect founder workload distribution? (1=Increases Burden, 5=Reduces Burden)',
                                                           null=True, blank=True)
    q_cofounder_conflict_resolution = models.IntegerField(verbose_name='Conflict Resolution Capability', choices=[(i, str(i)) for i in range(1, 6)],
                                                        help_text='How well will this role support conflict resolution? (1=Hinders, 5=Enhances)',
                                                        null=True, blank=True)
    q_cofounder_innovation_synergy = models.CharField(verbose_name='Innovation Synergy', max_length=12,
                                                   choices=[
                                                       ('disruptive', 'Disruptive Innovation'),
                                                       ('incremental', 'Incremental Innovation'),
                                                       ('supportive', 'Supportive Innovation'),
                                                       ('maintenance', 'Maintenance Focus')
                                                   ], null=True, blank=True)
    q_cofounder_risk_sharing = models.IntegerField(verbose_name='Risk Sharing Balance', choices=[(i, str(i)) for i in range(1, 6)],
                                                  help_text='How well does this role distribute business risk? (1=Concentrates Risk, 5=Distributes Risk)',
                                                  null=True, blank=True)
    q_cofounder_growth_acceleration = models.BooleanField(verbose_name='Growth Acceleration Potential', 
                                                        help_text='Will this role significantly accelerate growth?',
                                                        null=True, blank=True)
    
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
    
    # CEO-Specific Questions (Enhanced to 10 questions)
    q_ceo_leadership_impact = models.IntegerField(verbose_name='Leadership Impact', choices=[(i, str(i)) for i in range(1, 6)], 
                                                help_text='How will this role drive organizational success? (1=Low, 5=High)', 
                                                null=True, blank=True)
    q_ceo_strategic_priority = models.CharField(verbose_name='Strategic Priority Level', max_length=10,
                                           choices=[
                                               ('critical', 'Critical'),
                                               ('high', 'High'),
                                               ('medium', 'Medium')
                                           ], null=True, blank=True)
    q_ceo_cross_functional_impact = models.IntegerField(verbose_name='Cross-functional Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                                     help_text='How will this role affect multiple departments? (1=Low, 5=High)', 
                                                     null=True, blank=True)
    q_ceo_board_alignment = models.CharField(verbose_name='Board/Investor Alignment', max_length=10,
                                        choices=[
                                            ('aligned', 'Aligned'),
                                            ('neutral', 'Neutral'),
                                            ('concern', 'Concern')
                                        ], null=True, blank=True)
    q_ceo_success_metrics = models.BooleanField(verbose_name='Success Metrics Available', 
                                           help_text='Are success metrics clearly defined?', 
                                           null=True, blank=True)
    
    # Additional 5 Enhanced CEO Questions
    q_ceo_stakeholder_impact = models.IntegerField(verbose_name='Stakeholder Impact Assessment', choices=[(i, str(i)) for i in range(1, 6)],
                                                 help_text='How will this role impact key stakeholders? (1=Negative, 5=Highly Positive)',
                                                 null=True, blank=True)
    q_ceo_market_positioning = models.CharField(verbose_name='Market Positioning Strategy', max_length=20,
                                              choices=[
                                                  ('market_leader', 'Market Leader'),
                                                  ('market_challenger', 'Market Challenger'),
                                                  ('niche_player', 'Niche Player'),
                                                  ('cost_leader', 'Cost Leader')
                                              ], null=True, blank=True)
    q_ceo_talent_attraction = models.IntegerField(verbose_name='Talent Attraction Power', choices=[(i, str(i)) for i in range(1, 6)],
                                                help_text='How will this role enhance talent attraction? (1=No Impact, 5=Significant Enhancement)',
                                                null=True, blank=True)
    q_ceo_change_management = models.IntegerField(verbose_name='Change Management Complexity', choices=[(i, str(i)) for i in range(1, 6)],
                                                help_text='How complex is the change management required? (1=Simple, 5=Very Complex)',
                                                null=True, blank=True)
    q_ceo_customer_experience = models.BooleanField(verbose_name='Customer Experience Enhancement', 
                                                  help_text='Will this role significantly improve customer experience?',
                                                  null=True, blank=True)
    
    # CFO-Specific Questions (Enhanced to 10 questions)
    q_cfo_roi_confidence = models.IntegerField(verbose_name='ROI Confidence', choices=[(i, str(i)) for i in range(1, 6)], 
                                           help_text='How confident are you in financial returns? (1=Low, 5=Very High)', 
                                           null=True, blank=True)
    q_cfo_budget_flexibility = models.CharField(verbose_name='Budget Flexibility', max_length=10,
                                           choices=[
                                               ('flexible', 'Flexible'),
                                               ('limited', 'Limited'),
                                               ('fixed', 'Fixed')
                                           ], null=True, blank=True)
    q_cfo_financial_risk = models.IntegerField(verbose_name='Financial Risk Assessment', choices=[(i, str(i)) for i in range(1, 6)],
                                           help_text='How financially sound is this investment? (1=High Risk, 5=Low Risk)', 
                                           null=True, blank=True)
    q_cfo_cash_flow_impact = models.CharField(verbose_name='Cash Flow Impact', max_length=10,
                                           choices=[
                                               ('positive', 'Positive'),
                                               ('neutral', 'Neutral'),
                                               ('negative', 'Negative')
                                           ], null=True, blank=True)
    q_cfo_compliance = models.BooleanField(verbose_name='Compliance Requirements Met', 
                                       help_text='Are compliance requirements satisfied?', 
                                       null=True, blank=True)
    
    # Additional 5 Enhanced CFO Questions
    q_cfo_investment_justification = models.IntegerField(verbose_name='Investment Justification Strength', choices=[(i, str(i)) for i in range(1, 6)],
                                                       help_text='How strong is the financial justification? (1=Weak, 5=Very Strong)',
                                                       null=True, blank=True)
    q_cfo_cost_reduction = models.CharField(verbose_name='Cost Reduction Potential', max_length=12,
                                          choices=[
                                              ('significant', 'Significant Reduction'),
                                              ('moderate', 'Moderate Reduction'),
                                              ('minimal', 'Minimal Reduction'),
                                              ('increase', 'Cost Increase')
                                          ], null=True, blank=True)
    q_cfo_revenue_impact = models.IntegerField(verbose_name='Revenue Impact Projection', choices=[(i, str(i)) for i in range(1, 6)],
                                             help_text='How strong is the projected revenue impact? (1=Minimal, 5=Transformative)',
                                             null=True, blank=True)
    q_cfo_financial_controls = models.IntegerField(verbose_name='Financial Controls Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                                 help_text='How will this affect financial controls? (1=Weakens Controls, 5=Strengthens Controls)',
                                                 null=True, blank=True)
    q_cfo_audit_readiness = models.BooleanField(verbose_name='Audit Readiness Support', 
                                              help_text='Does this role support audit readiness?',
                                              null=True, blank=True)
    
    # CTO-Specific Questions (Enhanced to 10 questions)
    q_cto_technical_feasibility = models.IntegerField(verbose_name='Technical Feasibility', choices=[(i, str(i)) for i in range(1, 6)],
                                                  help_text='How technically achievable are objectives? (1=Low, 5=High)', 
                                                  null=True, blank=True)
    q_cto_stack_alignment = models.CharField(verbose_name='Technology Stack Alignment', max_length=10,
                                       choices=[
                                           ('aligned', 'Aligned'),
                                           ('partial', 'Partial'),
                                           ('misaligned', 'Misaligned')
                                       ], null=True, blank=True)
    q_cto_innovation_impact = models.IntegerField(verbose_name='Innovation Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                             help_text='How much will this role drive innovation? (1=Low, 5=High)', 
                                             null=True, blank=True)
    q_cto_tech_debt = models.CharField(verbose_name='Technical Debt Considerations', max_length=10,
                                    choices=[
                                        ('low', 'Low Impact'),
                                        ('medium', 'Medium Impact'),
                                        ('high', 'High Impact')
                                    ], null=True, blank=True)
    q_cto_scalability = models.BooleanField(verbose_name='Scalability Requirements Met', 
                                        help_text='Are scalability requirements satisfied?', 
                                        null=True, blank=True)
    
    # Additional 5 Enhanced CTO Questions
    q_cto_architecture_impact = models.IntegerField(verbose_name='Architecture Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                                  help_text='How will this role impact system architecture? (1=Minimal, 5=Transformative)',
                                                  null=True, blank=True)
    q_cto_security_posture = models.CharField(verbose_name='Security Posture Enhancement', max_length=12,
                                          choices=[
                                              ('significant', 'Significant Enhancement'),
                                              ('moderate', 'Moderate Enhancement'),
                                              ('minimal', 'Minimal Enhancement'),
                                              ('risk', 'Security Risk')
                                          ], null=True, blank=True)
    q_cto_team_capability = models.IntegerField(verbose_name='Team Capability Enhancement', choices=[(i, str(i)) for i in range(1, 6)],
                                             help_text='How much will this enhance team capabilities? (1=Minimal, 5=Significant)',
                                             null=True, blank=True)
    q_cto_delivery_velocity = models.IntegerField(verbose_name='Delivery Velocity Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                                help_text='How will this affect delivery velocity? (1=Slows Down, 5=Speeds Up)',
                                                null=True, blank=True)
    q_cto_quality_assurance = models.BooleanField(verbose_name='Quality Assurance Enhancement', 
                                               help_text='Will this role significantly improve QA processes?',
                                               null=True, blank=True)
    
    # COO-Specific Questions (Enhanced to 10 questions)
    q_coo_operational_efficiency = models.IntegerField(verbose_name='Operational Efficiency', choices=[(i, str(i)) for i in range(1, 6)],
                                                  help_text='How will this role improve operational efficiency? (1=Low, 5=High)', 
                                                  null=True, blank=True)
    q_coo_process_integration = models.CharField(verbose_name='Process Integration Level', max_length=10,
                                           choices=[
                                               ('seamless', 'Seamless'),
                                               ('moderate', 'Moderate'),
                                               ('complex', 'Complex')
                                           ], null=True, blank=True)
    q_coo_resource_optimization = models.IntegerField(verbose_name='Resource Optimization', choices=[(i, str(i)) for i in range(1, 6)],
                                               help_text='How well will this role optimize resources? (1=Low, 5=High)', 
                                               null=True, blank=True)
    q_coo_workflow_disruption = models.CharField(verbose_name='Workflow Disruption Risk', max_length=10,
                                           choices=[
                                               ('low', 'Low'),
                                               ('medium', 'Medium'),
                                               ('high', 'High')
                                           ], null=True, blank=True)
    q_coo_standardization = models.BooleanField(verbose_name='Standardization Opportunities', 
                                           help_text='Are there standardization opportunities?', 
                                           null=True, blank=True)
    
    # Additional 5 Enhanced COO Questions
    q_coo_service_delivery = models.IntegerField(verbose_name='Service Delivery Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                                help_text='How will this role impact service delivery? (1=Degrades, 5=Significantly Improves)',
                                                null=True, blank=True)
    q_coo_cost_optimization = models.CharField(verbose_name='Cost Optimization Opportunity', max_length=15,
                                            choices=[
                                                ('significant', 'Significant Savings'),
                                                ('moderate', 'Moderate Savings'),
                                                ('minimal', 'Minimal Savings'),
                                                ('investment', 'Requires Investment')
                                            ], null=True, blank=True)
    q_coo_customer_satisfaction = models.IntegerField(verbose_name='Customer Satisfaction Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                                   help_text='How will this affect customer satisfaction? (1=Negative, 5=Highly Positive)',
                                                   null=True, blank=True)
    q_coo_operational_risk = models.IntegerField(verbose_name='Operational Risk Assessment', choices=[(i, str(i)) for i in range(1, 6)],
                                               help_text='What is the operational risk level? (1=High Risk, 5=Low Risk)',
                                               null=True, blank=True)
    q_coo_continuous_improvement = models.BooleanField(verbose_name='Continuous Improvement Driver', 
                                                     help_text='Will this role drive continuous improvement?',
                                                     null=True, blank=True)
    
    # Project Head-Specific Questions (Enhanced to 10 questions)
    q_ph_deliverability = models.IntegerField(verbose_name='Project Deliverability', choices=[(i, str(i)) for i in range(1, 6)],
                                         help_text='How confident are you in delivery? (1=Low, 5=High)', 
                                         null=True, blank=True)
    q_ph_team_capacity = models.CharField(verbose_name='Team Capacity', max_length=10,
                                     choices=[
                                         ('available', 'Available'),
                                         ('stretched', 'Stretched'),
                                         ('overloaded', 'Overloaded')
                                     ], null=True, blank=True)
    q_ph_timeline_realism = models.IntegerField(verbose_name='Timeline Realism', choices=[(i, str(i)) for i in range(1, 6)],
                                         help_text='How realistic are timelines? (1=Unrealistic, 5=Very Realistic)', 
                                         null=True, blank=True)
    q_ph_dependency_management = models.CharField(verbose_name='Dependency Management', max_length=10,
                                           choices=[
                                               ('simple', 'Simple'),
                                               ('moderate', 'Moderate'),
                                               ('complex', 'Complex')
                                           ], null=True, blank=True)
    q_ph_resource_clarity = models.BooleanField(verbose_name='Resource Requirements Clear', 
                                           help_text='Are resource requirements clearly defined?', 
                                           null=True, blank=True)
    
    # Additional 5 Enhanced Project Head Questions
    q_ph_stakeholder_management = models.IntegerField(verbose_name='Stakeholder Management Complexity', choices=[(i, str(i)) for i in range(1, 6)],
                                                   help_text='How complex is stakeholder management? (1=Simple, 5=Very Complex)',
                                                   null=True, blank=True)
    q_ph_scope_clarity = models.CharField(verbose_name='Scope Definition Clarity', max_length=15,
                                        choices=[
                                            ('crystal_clear', 'Crystal Clear'),
                                            ('well_defined', 'Well Defined'),
                                            ('somewhat_clear', 'Somewhat Clear'),
                                            ('unclear', 'Unclear')
                                        ], null=True, blank=True)
    q_ph_success_probability = models.IntegerField(verbose_name='Project Success Probability', choices=[(i, str(i)) for i in range(1, 6)],
                                                help_text='What is the probability of project success? (1=Low, 5=Very High)',
                                                null=True, blank=True)
    q_ph_innovation_potential = models.IntegerField(verbose_name='Innovation Potential', choices=[(i, str(i)) for i in range(1, 6)],
                                                 help_text='How innovative is this project? (1=Incremental, 5=Breakthrough)',
                                                 null=True, blank=True)
    q_ph_business_value = models.BooleanField(verbose_name='Clear Business Value', 
                                           help_text='Is the business value clearly defined and measurable?',
                                           null=True, blank=True)
    
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
    
    # HR Manager-Specific Questions (Enhanced to 10 questions)
    q_hr_culture_impact = models.IntegerField(verbose_name='Team Culture Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                        help_text='How will this role affect team culture and morale? (1=Negative, 5=Positive)', 
                                        null=True, blank=True)
    q_hr_development_potential = models.CharField(verbose_name='Employee Development Potential', max_length=10,
                                           choices=[
                                               ('high', 'High'),
                                               ('moderate', 'Moderate'),
                                               ('low', 'Low')
                                           ], null=True, blank=True)
    q_hr_retention_risk = models.IntegerField(verbose_name='Retention Risk Assessment', choices=[(i, str(i)) for i in range(1, 6)],
                                        help_text='What is the risk of current team members leaving? (1=High Risk, 5=Low Risk)', 
                                        null=True, blank=True)
    q_hr_training_infrastructure = models.BooleanField(verbose_name='Training Infrastructure Available', 
                                           help_text='Is training infrastructure available?', 
                                           null=True, blank=True)
    q_hr_performance_integration = models.CharField(verbose_name='Performance Management Integration', max_length=10,
                                             choices=[
                                                 ('seamless', 'Seamless'),
                                                 ('moderate', 'Moderate'),
                                                 ('complex', 'Complex')
                                             ], null=True, blank=True)
    
    # Additional 5 Enhanced HR Manager Questions
    q_hr_workforce_planning = models.IntegerField(verbose_name='Workforce Planning Alignment', choices=[(i, str(i)) for i in range(1, 6)],
                                                help_text='How well does this align with workforce planning? (1=Misaligned, 5=Perfectly Aligned)',
                                                null=True, blank=True)
    q_hr_succession_planning = models.CharField(verbose_name='Succession Planning Impact', max_length=15,
                                            choices=[
                                                ('critical', 'Critical for Succession'),
                                                ('important', 'Important for Succession'),
                                                ('supportive', 'Supportive to Succession'),
                                                ('no_impact', 'No Succession Impact')
                                            ], null=True, blank=True)
    q_hr_diversity_inclusion = models.IntegerField(verbose_name='Diversity & Inclusion Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                               help_text='How will this impact D&I initiatives? (1=Negative, 5=Highly Positive)',
                                               null=True, blank=True)
    q_hr_employee_engagement = models.IntegerField(verbose_name='Employee Engagement Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                                help_text='How will this affect employee engagement? (1=Negative, 5=Highly Positive)',
                                                null=True, blank=True)
    q_hr_legal_compliance = models.BooleanField(verbose_name='Legal Compliance Support', 
                                             help_text='Does this role support legal compliance requirements?',
                                             null=True, blank=True)
    
    # Recruiter-Specific Questions (Enhanced to 10 questions)
    q_rec_talent_availability = models.IntegerField(verbose_name='Market Talent Availability', choices=[(i, str(i)) for i in range(1, 6)],
                                           help_text='How available is qualified talent in the market? (1=Scarce, 5=Abundant)', 
                                           null=True, blank=True)
    q_rec_sourcing_strategy = models.CharField(verbose_name='Sourcing Strategy Effectiveness', max_length=10,
                                         choices=[
                                             ('strong', 'Strong'),
                                             ('moderate', 'Moderate'),
                                             ('weak', 'Weak')
                                         ], null=True, blank=True)
    q_rec_time_to_hire = models.IntegerField(verbose_name='Time-to-Hire Estimate', choices=[(i, str(i)) for i in range(1, 6)],
                                       help_text='How quickly can we fill this position? (1=Very Slow, 5=Very Fast)', 
                                       null=True, blank=True)
    q_rec_compensation_competitive = models.CharField(verbose_name='Compensation Competitiveness', max_length=15,
                                               choices=[
                                                   ('competitive', 'Competitive'),
                                                   ('average', 'Average'),
                                                   ('below', 'Below Market')
                                               ], null=True, blank=True)
    q_rec_pipeline_ready = models.BooleanField(verbose_name='Candidate Pipeline Ready', 
                                         help_text='Is there a ready candidate pipeline?', 
                                         null=True, blank=True)
    
    # Additional 5 Enhanced Recruiter Questions
    q_rec_employer_brand = models.IntegerField(verbose_name='Employer Brand Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                            help_text='How will this role impact employer brand? (1=Negative, 5=Highly Positive)',
                                            null=True, blank=True)
    q_rec_interview_process = models.CharField(verbose_name='Interview Process Complexity', max_length=12,
                                          choices=[
                                              ('simple', 'Simple Process'),
                                              ('moderate', 'Moderate Process'),
                                              ('complex', 'Complex Process'),
                                              ('specialized', 'Highly Specialized')
                                          ], null=True, blank=True)
    q_rec_candidate_experience = models.IntegerField(verbose_name='Candidate Experience Enhancement', choices=[(i, str(i)) for i in range(1, 6)],
                                                 help_text='How will this improve candidate experience? (1=No Impact, 5=Significant Enhancement)',
                                                 null=True, blank=True)
    q_rec_hiring_manager_readiness = models.IntegerField(verbose_name='Hiring Manager Readiness', choices=[(i, str(i)) for i in range(1, 6)],
                                                     help_text='How ready are hiring managers? (1=Unprepared, 5=Fully Prepared)',
                                                     null=True, blank=True)
    q_rec_market_intelligence = models.BooleanField(verbose_name='Market Intelligence Available', 
                                                 help_text='Is sufficient market intelligence available?',
                                                 null=True, blank=True)
    
    # HR Executive-Specific Questions (Enhanced to 10 questions)
    q_hre_onboarding_readiness = models.IntegerField(verbose_name='Onboarding Process Readiness', choices=[(i, str(i)) for i in range(1, 6)],
                                              help_text='How prepared are our onboarding processes? (1=Not Ready, 5=Fully Ready)', 
                                              null=True, blank=True)
    q_hre_compliance_status = models.CharField(verbose_name='Compliance Requirements Status', max_length=15,
                                          choices=[
                                              ('compliant', 'Compliant'),
                                              ('partial', 'Partial'),
                                              ('non_compliant', 'Non-Compliant')
                                          ], null=True, blank=True)
    q_hre_documentation = models.IntegerField(verbose_name='Documentation Completeness', choices=[(i, str(i)) for i in range(1, 6)],
                                        help_text='How complete is our role documentation? (1=Incomplete, 5=Complete)', 
                                        null=True, blank=True)
    q_hre_systems_capacity = models.CharField(verbose_name='HR Systems Capacity', max_length=12,
                                         choices=[
                                             ('sufficient', 'Sufficient'),
                                             ('limited', 'Limited'),
                                             ('insufficient', 'Insufficient')
                                         ], null=True, blank=True)
    q_hre_reporting_framework = models.BooleanField(verbose_name='Reporting Framework Available', 
                                             help_text='Is there a reporting framework in place?', 
                                             null=True, blank=True)
    
    # Additional 5 Enhanced HR Executive Questions
    q_hre_policy_impact = models.IntegerField(verbose_name='Policy Development Impact', choices=[(i, str(i)) for i in range(1, 6)],
                                           help_text='How will this role impact policy development? (1=Minimal, 5=Significant)',
                                           null=True, blank=True)
    q_hre_data_analytics = models.CharField(verbose_name='HR Analytics Capability', max_length=12,
                                        choices=[
                                            ('advanced', 'Advanced Analytics'),
                                            ('intermediate', 'Intermediate Analytics'),
                                            ('basic', 'Basic Analytics'),
                                            ('none', 'No Analytics')
                                        ], null=True, blank=True)
    q_hre_automation_potential = models.IntegerField(verbose_name='Process Automation Potential', choices=[(i, str(i)) for i in range(1, 6)],
                                                  help_text='How much automation potential exists? (1=Minimal, 5=Significant)',
                                                  null=True, blank=True)
    q_hre_vendor_management = models.IntegerField(verbose_name='Vendor Management Complexity', choices=[(i, str(i)) for i in range(1, 6)],
                                                help_text='How complex is vendor management? (1=Simple, 5=Very Complex)',
                                                null=True, blank=True)
    q_hre_knowledge_transfer = models.BooleanField(verbose_name='Knowledge Transfer Framework', 
                                                help_text='Is there a knowledge transfer framework in place?',
                                                null=True, blank=True)
    
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
        is_new = self.pk is None

        # Calculate risk before saving
        self.calculate_risk()
        
        # Generate corrective guidance if declined
        if self.decision == 'decline':
            self.generate_corrective_guidance()
        
        super().save(*args, **kwargs)

        # Audit only on initial creation, not every update
        if is_new:
            # Simple readiness score derived inversely from risk level
            readiness_map = {
                'low': 100,
                'medium': 60,
                'high': 30,
            }
            readiness_score = readiness_map.get(self.risk_level)

            # Numeric representation of risk level (higher is riskier)
            risk_score_from_level = {
                'low': 0,
                'medium': 1,
                'high': 2,
            }.get(self.risk_level)

            AuditLog.objects.create(
                event_type='diagnostic_submitted',
                user=self.user,
                entity_type='diagnostic_submission',
                entity_id=self.id,
                metadata={
                    'job_role_id': self.job_role_id,
                    'job_role_title': self.job_role.title if self.job_role_id else None,
                    'decision': self.decision,
                    'risk_level': self.risk_level,
                    'risk_score_from_level': risk_score_from_level,
                    'readiness_score': readiness_score,
                    'user_level': self.user.get_level(),
                    'user_role': self.user.role,
                },
            )
    
    def calculate_risk(self):
        """Rule-based risk calculation"""
        user_role = self.user.role
        user_level = self.user.get_level()
        
        if user_level == 1:  # Level 1 roles
            risk_score = 0
            
            # Role-specific risk calculation
            if user_role == 'founder':
                # Founder-specific risk rules
                # Rule 1: Vision alignment
                if self.q_founder_vision_alignment and self.q_founder_vision_alignment <= 2:
                    risk_score += 3
                elif self.q_founder_vision_alignment and self.q_founder_vision_alignment >= 4:
                    risk_score -= 1
                
                # Rule 2: Strategic fit
                if self.q_founder_strategic_fit and self.q_founder_strategic_fit <= 2:
                    risk_score += 2
                elif self.q_founder_strategic_fit and self.q_founder_strategic_fit >= 4:
                    risk_score -= 1
                
                # Rule 3: Market positioning
                if self.q_founder_market_positioning and self.q_founder_market_positioning <= 2:
                    risk_score += 2
                
                # Rule 4: Resource priority
                if self.q_founder_resource_priority == 'low':
                    risk_score += 1
                elif self.q_founder_resource_priority == 'high':
                    risk_score -= 1
                
                # Rule 5: Equity consideration (if equity required but not feasible)
                if self.q_founder_equity_consideration == 'equity_required':
                    risk_score += 1
            
            elif user_role == 'co_founder':
                # Co-Founder-specific risk rules
                # Rule 1: Partnership dynamics
                if self.q_cofounder_partnership_dynamics and self.q_cofounder_partnership_dynamics <= 2:
                    risk_score += 3
                elif self.q_cofounder_partnership_dynamics and self.q_cofounder_partnership_dynamics >= 4:
                    risk_score -= 1
                
                # Rule 2: Complementary skills
                if self.q_cofounder_complementary_skills and self.q_cofounder_complementary_skills <= 2:
                    risk_score += 2
                elif self.q_cofounder_complementary_skills and self.q_cofounder_complementary_skills >= 4:
                    risk_score -= 1
                
                # Rule 3: Team chemistry
                if self.q_cofounder_team_chemistry and self.q_cofounder_team_chemistry <= 2:
                    risk_score += 2
                
                # Rule 4: Decision-making alignment
                if self.q_cofounder_decision_making == 'low':
                    risk_score += 1
                elif self.q_cofounder_decision_making == 'high':
                    risk_score -= 1
                
                # Rule 5: Culture fit
                if self.q_cofounder_culture_fit and self.q_cofounder_culture_fit <= 2:
                    risk_score += 1
            
            elif user_role == 'cfo':
                # CFO-specific risk rules (using q0_* fields)
                # Rule 1: Budget alignment
                if not self.q0_budget_alignment:
                    risk_score += 3
                
                # Rule 2: ROI analysis
                if self.q0_roi_analysis and self.q0_roi_analysis <= 2:
                    risk_score += 2
                
                # Rule 3: Cash flow impact
                if self.q0_cash_flow_impact and self.q0_cash_flow_impact <= 2:
                    risk_score += 2
                
                # Rule 4: Funding source
                if self.q0_funding_source == 'new_funding':
                    risk_score += 1
            
            else:  # CEO or other Level 1 roles - use common Level 1 rules
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


class AuditLog(models.Model):
    """Generic audit log for key system events"""
    EVENT_TYPES = [
        ('login_success', 'Login Success'),
        ('login_failure', 'Login Failure'),
        ('diagnostic_submitted', 'Diagnostic Submitted'),
        ('final_decision_generated', 'Final Decision Generated'),
        ('job_role_deleted', 'Job Role Deleted'),
    ]
    
    ENTITY_TYPES = [
        ('job_role', 'Job Role'),
        ('diagnostic_submission', 'Diagnostic Submission'),
    ]
    
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES, blank=True)
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        user_str = self.user.username if self.user else 'anonymous'
        return f"{self.event_type} - {user_str} @ {self.created_at}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('job_created', 'Job Role Created'),
        ('job_deleted', 'Job Role Deleted'),
        ('assessment_completed', 'Assessment Completed'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='other')
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
        # Get all users who should be notified, except the creator
        users_to_notify = User.objects.filter(
            models.Q(role__in=['founder', 'co_founder']) |  # Level 1
            models.Q(role__in=['ceo', 'cfo', 'cto', 'coo', 'project_head']) |   # Level 2
            models.Q(role__in=['hr_manager', 'recruiter', 'hr_executive'])  # Level 3
        ).exclude(id=instance.created_by.id).distinct()  # Exclude the creator
        
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