from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, JobRole, DiagnosticSubmission

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )
    role = forms.ChoiceField(
        choices=[('', 'Select role')] + User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class JobRoleForm(forms.ModelForm):
    class Meta:
        model = JobRole
        fields = ['title', 'department', 'description', 'required_skills', 
                 'experience_level', 'budget_range', 'urgency']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'required_skills': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class DiagnosticForm(forms.ModelForm):
    class Meta:
        model = DiagnosticSubmission
        fields = []
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            user_role = user.role
            user_level = user.get_level()
            
            if user_role == 'founder':
                # Founder-specific questions
                self.fields['q_founder_vision_alignment'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='1. Vision Alignment (1-5, where 5 is excellent alignment)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q_founder_strategic_fit'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='2. Strategic Fit (1-5, where 5 is perfect fit)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q_founder_market_positioning'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='3. Market Positioning Impact (1-5, where 5 is strong impact)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q_founder_resource_priority'] = forms.ChoiceField(
                    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                    label='4. Resource Allocation Priority',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q_founder_equity_consideration'] = forms.ChoiceField(
                    choices=[
                        ('not_applicable', 'Not Applicable'),
                        ('equity_required', 'Equity Required'),
                        ('cash_only', 'Cash Only'),
                        ('hybrid', 'Hybrid (Cash + Equity)')
                    ],
                    label='5. Equity Consideration',
                    widget=forms.RadioSelect,
                    required=True
                )
            
            elif user_role == 'co_founder':
                # Co-Founder-specific questions
                self.fields['q_cofounder_partnership_dynamics'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='1. Partnership Dynamics (1-5, where 5 is excellent)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q_cofounder_complementary_skills'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='2. Complementary Skills (1-5, where 5 is highly complementary)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q_cofounder_team_chemistry'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='3. Team Chemistry (1-5, where 5 is excellent)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q_cofounder_decision_making'] = forms.ChoiceField(
                    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                    label='4. Decision-Making Alignment',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q_cofounder_culture_fit'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='5. Culture and Values Alignment (1-5, where 5 is excellent)',
                    widget=forms.RadioSelect,
                    required=True
                )
            
            elif user_role == 'cfo':
                # CFO-specific questions
                self.fields['q0_roi_analysis'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='1. ROI Projection Score (1-5, where 5 is Very High)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q0_cash_flow_impact'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='2. Cash Flow Impact (1-5, where 5 is Positive)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q0_budget_alignment'] = forms.ChoiceField(
                    choices=[(True, 'Yes'), (False, 'No')],
                    label='3. Aligned with Annual Budget?',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q0_funding_source'] = forms.ChoiceField(
                    choices=[
                        ('operational', 'Operational Budget'),
                        ('contingency', 'Contingency Fund'),
                        ('new_funding', 'Requires New Funding'),
                        ('cost_center', 'Cost Center Budget')
                    ],
                    label='4. Funding Source',
                    widget=forms.RadioSelect,
                    required=True
                )
            
            elif user_level == 1:
                # CEO or other Level 1 questions (shared by all Level 1 roles except founder/co_founder/cfo)
                self.fields['q1_business_alignment'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='1. Business Alignment (1-5)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q2_financial_risk'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='2. Financial Risk Assessment (1-5)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q3_long_term_impact'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='3. Long-term Impact (1-5)',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q4_budget_approval'] = forms.ChoiceField(
                    choices=[(True, 'Yes'), (False, 'No')],
                    label='4. Budget Approved?',
                    widget=forms.RadioSelect,
                    required=True
                )
                self.fields['q5_strategic_priority'] = forms.ChoiceField(
                    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                    label='5. Strategic Priority',
                    widget=forms.RadioSelect,
                    required=True
                )
                
            elif user_level == 2:
                # Level 2 questions
                self.fields['q6_skill_availability'] = forms.ChoiceField(
                    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                    label='1. Skill Availability in Market',
                    widget=forms.RadioSelect
                )
                self.fields['q7_execution_feasibility'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='2. Execution Feasibility (1-5)',
                    widget=forms.RadioSelect
                )
                self.fields['q8_team_dependency'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='3. Team Dependency Level (1-5)',
                    widget=forms.RadioSelect
                )
                self.fields['q9_timeline_risk'] = forms.ChoiceField(
                    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                    label='4. Timeline Risk',
                    widget=forms.RadioSelect
                )
                self.fields['q10_mentor_available'] = forms.ChoiceField(
                    choices=[(True, 'Yes'), (False, 'No')],
                    label='5. Mentor/Trainer Available?',
                    widget=forms.RadioSelect
                )
                
            else:  # Level 3
                # Level 3 questions
                self.fields['q11_talent_availability'] = forms.ChoiceField(
                    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                    label='1. Talent Availability',
                    widget=forms.RadioSelect
                )
                self.fields['q12_cost_validation'] = forms.ChoiceField(
                    choices=[(True, 'Yes'), (False, 'No')],
                    label='2. Cost Validated with Market?',
                    widget=forms.RadioSelect
                )
                self.fields['q13_process_readiness'] = forms.ChoiceField(
                    choices=[(i, str(i)) for i in range(1, 6)],
                    label='3. Process Readiness (1-5)',
                    widget=forms.RadioSelect
                )
                self.fields['q14_onboarding_capacity'] = forms.ChoiceField(
                    choices=[(True, 'Yes'), (False, 'No')],
                    label='4. Onboarding Capacity Available?',
                    widget=forms.RadioSelect
                )
                self.fields['q15_market_competition'] = forms.ChoiceField(
                    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                    label='5. Market Competition Level',
                    widget=forms.RadioSelect
                )
        
        # Common decision fields
        self.fields['decision'] = forms.ChoiceField(
            choices=DiagnosticSubmission.DECISION_CHOICES,
            widget=forms.RadioSelect
        )
        self.fields['decline_reason'] = forms.CharField(
            required=False,
            widget=forms.Textarea(attrs={'rows': 3}),
            label='Decline Reason (if declining)'
        )
        self.fields['decline_category'] = forms.ChoiceField(
            required=False,
            choices=[
                ('', 'Select category'),
                ('budget_constraint', 'Budget constraint'),
                ('skill_unavailability', 'Skill unavailability'),
                ('timeline_risk', 'Timeline risk'),
                ('team_dependency', 'Team dependency'),
                ('business_misalignment', 'Business misalignment'),
                ('operational_gap', 'Operational readiness gap'),
            ],
            label='Decline Category'
        )