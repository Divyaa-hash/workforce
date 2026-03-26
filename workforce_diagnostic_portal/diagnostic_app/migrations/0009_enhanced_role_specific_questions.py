# Generated migration for enhanced role-specific questions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnostic_app', '0008_alter_auditlog_event_type'),
    ]

    operations = [
        # Enhanced Founder Questions (5 additional questions)
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_founder_market_opportunity',
            field=models.IntegerField(
                verbose_name='Market Opportunity Assessment', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How significant is the market opportunity this role addresses? (1=Limited, 5=Transformative)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_founder_competitive_advantage',
            field=models.IntegerField(
                verbose_name='Competitive Advantage Creation', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How strongly will this role create competitive advantage? (1=Minimal, 5=Significant)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_founder_scalability_impact',
            field=models.CharField(
                verbose_name='Scalability Impact', 
                max_length=15,
                choices=[
                    ('local', 'Local Impact'),
                    ('regional', 'Regional Impact'),
                    ('national', 'National Impact'),
                    ('global', 'Global Impact')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_founder_investment_priority',
            field=models.CharField(
                verbose_name='Investment Priority Level', 
                max_length=12,
                choices=[
                    ('critical', 'Critical Investment'),
                    ('high', 'High Priority'),
                    ('moderate', 'Moderate Priority'),
                    ('optional', 'Optional Investment')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_founder_exit_strategy',
            field=models.BooleanField(
                verbose_name='Exit Strategy Alignment', 
                help_text='Does this role support long-term exit strategy?',
                null=True, 
                blank=True
            ),
        ),

        # Enhanced Co-Founder Questions (5 additional questions)
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cofounder_workload_distribution',
            field=models.IntegerField(
                verbose_name='Workload Distribution Impact', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this role affect founder workload distribution? (1=Increases Burden, 5=Reduces Burden)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cofounder_conflict_resolution',
            field=models.IntegerField(
                verbose_name='Conflict Resolution Capability', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How well will this role support conflict resolution? (1=Hinders, 5=Enhances)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cofounder_innovation_synergy',
            field=models.CharField(
                verbose_name='Innovation Synergy', 
                max_length=12,
                choices=[
                    ('disruptive', 'Disruptive Innovation'),
                    ('incremental', 'Incremental Innovation'),
                    ('supportive', 'Supportive Innovation'),
                    ('maintenance', 'Maintenance Focus')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cofounder_risk_sharing',
            field=models.IntegerField(
                verbose_name='Risk Sharing Balance', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How well does this role distribute business risk? (1=Concentrates Risk, 5=Distributes Risk)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cofounder_growth_acceleration',
            field=models.BooleanField(
                verbose_name='Growth Acceleration Potential', 
                help_text='Will this role significantly accelerate growth?',
                null=True, 
                blank=True
            ),
        ),

        # Enhanced CEO Questions (5 additional questions)
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_ceo_stakeholder_impact',
            field=models.IntegerField(
                verbose_name='Stakeholder Impact Assessment', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this role impact key stakeholders? (1=Negative, 5=Highly Positive)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_ceo_market_positioning',
            field=models.CharField(
                verbose_name='Market Positioning Strategy', 
                max_length=15,
                choices=[
                    ('market_leader', 'Market Leader'),
                    ('market_challenger', 'Market Challenger'),
                    ('niche_player', 'Niche Player'),
                    ('cost_leader', 'Cost Leader')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_ceo_talent_attraction',
            field=models.IntegerField(
                verbose_name='Talent Attraction Power', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this role enhance talent attraction? (1=No Impact, 5=Significant Enhancement)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_ceo_change_management',
            field=models.IntegerField(
                verbose_name='Change Management Complexity', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How complex is the change management required? (1=Simple, 5=Very Complex)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_ceo_customer_experience',
            field=models.BooleanField(
                verbose_name='Customer Experience Enhancement', 
                help_text='Will this role significantly improve customer experience?',
                null=True, 
                blank=True
            ),
        ),

        # Enhanced CFO Questions (5 additional questions)
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cfo_investment_justification',
            field=models.IntegerField(
                verbose_name='Investment Justification Strength', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How strong is the financial justification? (1=Weak, 5=Very Strong)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cfo_cost_reduction',
            field=models.CharField(
                verbose_name='Cost Reduction Potential', 
                max_length=12,
                choices=[
                    ('significant', 'Significant Reduction'),
                    ('moderate', 'Moderate Reduction'),
                    ('minimal', 'Minimal Reduction'),
                    ('increase', 'Cost Increase')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cfo_revenue_impact',
            field=models.IntegerField(
                verbose_name='Revenue Impact Projection', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How strong is the projected revenue impact? (1=Minimal, 5=Transformative)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cfo_financial_controls',
            field=models.IntegerField(
                verbose_name='Financial Controls Impact', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this affect financial controls? (1=Weakens Controls, 5=Strengthens Controls)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cfo_audit_readiness',
            field=models.BooleanField(
                verbose_name='Audit Readiness Support', 
                help_text='Does this role support audit readiness?',
                null=True, 
                blank=True
            ),
        ),

        # Enhanced CTO Questions (5 additional questions)
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cto_architecture_impact',
            field=models.IntegerField(
                verbose_name='Architecture Impact', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this role impact system architecture? (1=Minimal, 5=Transformative)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cto_security_posture',
            field=models.CharField(
                verbose_name='Security Posture Enhancement', 
                max_length=12,
                choices=[
                    ('significant', 'Significant Enhancement'),
                    ('moderate', 'Moderate Enhancement'),
                    ('minimal', 'Minimal Enhancement'),
                    ('risk', 'Security Risk')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cto_team_capability',
            field=models.IntegerField(
                verbose_name='Team Capability Enhancement', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How much will this enhance team capabilities? (1=Minimal, 5=Significant)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cto_delivery_velocity',
            field=models.IntegerField(
                verbose_name='Delivery Velocity Impact', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this affect delivery velocity? (1=Slows Down, 5=Speeds Up)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_cto_quality_assurance',
            field=models.BooleanField(
                verbose_name='Quality Assurance Enhancement', 
                help_text='Will this role significantly improve QA processes?',
                null=True, 
                blank=True
            ),
        ),

        # Enhanced COO Questions (5 additional questions)
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_coo_service_delivery',
            field=models.IntegerField(
                verbose_name='Service Delivery Impact', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this role impact service delivery? (1=Degrades, 5=Significantly Improves)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_coo_cost_optimization',
            field=models.CharField(
                verbose_name='Cost Optimization Opportunity', 
                max_length=15,
                choices=[
                    ('significant', 'Significant Savings'),
                    ('moderate', 'Moderate Savings'),
                    ('minimal', 'Minimal Savings'),
                    ('investment', 'Requires Investment')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_coo_customer_satisfaction',
            field=models.IntegerField(
                verbose_name='Customer Satisfaction Impact', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this affect customer satisfaction? (1=Negative, 5=Highly Positive)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_coo_operational_risk',
            field=models.IntegerField(
                verbose_name='Operational Risk Assessment', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='What is the operational risk level? (1=High Risk, 5=Low Risk)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_coo_continuous_improvement',
            field=models.BooleanField(
                verbose_name='Continuous Improvement Driver', 
                help_text='Will this role drive continuous improvement?',
                null=True, 
                blank=True
            ),
        ),

        # Enhanced Project Head Questions (5 additional questions)
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_ph_stakeholder_management',
            field=models.IntegerField(
                verbose_name='Stakeholder Management Complexity', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How complex is stakeholder management? (1=Simple, 5=Very Complex)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_ph_scope_clarity',
            field=models.CharField(
                verbose_name='Scope Definition Clarity', 
                max_length=12,
                choices=[
                    ('crystal_clear', 'Crystal Clear'),
                    ('well_defined', 'Well Defined'),
                    ('somewhat_clear', 'Somewhat Clear'),
                    ('unclear', 'Unclear')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_ph_success_probability',
            field=models.IntegerField(
                verbose_name='Project Success Probability', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='What is the probability of project success? (1=Low, 5=Very High)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_ph_innovation_potential',
            field=models.IntegerField(
                verbose_name='Innovation Potential', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How innovative is this project? (1=Incremental, 5=Breakthrough)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_ph_business_value',
            field=models.BooleanField(
                verbose_name='Clear Business Value', 
                help_text='Is the business value clearly defined and measurable?',
                null=True, 
                blank=True
            ),
        ),

        # Enhanced HR Manager Questions (5 additional questions)
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_hr_workforce_planning',
            field=models.IntegerField(
                verbose_name='Workforce Planning Alignment', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How well does this align with workforce planning? (1=Misaligned, 5=Perfectly Aligned)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_hr_succession_planning',
            field=models.CharField(
                verbose_name='Succession Planning Impact', 
                max_length=15,
                choices=[
                    ('critical', 'Critical for Succession'),
                    ('important', 'Important for Succession'),
                    ('supportive', 'Supportive to Succession'),
                    ('no_impact', 'No Succession Impact')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_hr_diversity_inclusion',
            field=models.IntegerField(
                verbose_name='Diversity & Inclusion Impact', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this impact D&I initiatives? (1=Negative, 5=Highly Positive)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_hr_employee_engagement',
            field=models.IntegerField(
                verbose_name='Employee Engagement Impact', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this affect employee engagement? (1=Negative, 5=Highly Positive)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_hr_legal_compliance',
            field=models.BooleanField(
                verbose_name='Legal Compliance Support', 
                help_text='Does this role support legal compliance requirements?',
                null=True, 
                blank=True
            ),
        ),

        # Enhanced Recruiter Questions (5 additional questions)
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_rec_employer_brand',
            field=models.IntegerField(
                verbose_name='Employer Brand Impact', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this role impact employer brand? (1=Negative, 5=Highly Positive)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_rec_interview_process',
            field=models.CharField(
                verbose_name='Interview Process Complexity', 
                max_length=12,
                choices=[
                    ('simple', 'Simple Process'),
                    ('moderate', 'Moderate Process'),
                    ('complex', 'Complex Process'),
                    ('specialized', 'Highly Specialized')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_rec_candidate_experience',
            field=models.IntegerField(
                verbose_name='Candidate Experience Enhancement', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this improve candidate experience? (1=No Impact, 5=Significant Enhancement)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_rec_hiring_manager_readiness',
            field=models.IntegerField(
                verbose_name='Hiring Manager Readiness', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How ready are hiring managers? (1=Unprepared, 5=Fully Prepared)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_rec_market_intelligence',
            field=models.BooleanField(
                verbose_name='Market Intelligence Available', 
                help_text='Is sufficient market intelligence available?',
                null=True, 
                blank=True
            ),
        ),

        # Enhanced HR Executive Questions (5 additional questions)
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_hre_policy_impact',
            field=models.IntegerField(
                verbose_name='Policy Development Impact', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How will this role impact policy development? (1=Minimal, 5=Significant)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_hre_data_analytics',
            field=models.CharField(
                verbose_name='HR Analytics Capability', 
                max_length=12,
                choices=[
                    ('advanced', 'Advanced Analytics'),
                    ('intermediate', 'Intermediate Analytics'),
                    ('basic', 'Basic Analytics'),
                    ('none', 'No Analytics')
                ],
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_hre_automation_potential',
            field=models.IntegerField(
                verbose_name='Process Automation Potential', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How much automation potential exists? (1=Minimal, 5=Significant)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_hre_vendor_management',
            field=models.IntegerField(
                verbose_name='Vendor Management Complexity', 
                choices=[(i, str(i)) for i in range(1, 6)],
                help_text='How complex is vendor management? (1=Simple, 5=Very Complex)',
                null=True, 
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='diagnosticsubmission',
            name='q_hre_knowledge_transfer',
            field=models.BooleanField(
                verbose_name='Knowledge Transfer Framework', 
                help_text='Is there a knowledge transfer framework in place?',
                null=True, 
                blank=True
            ),
        ),
    ]
