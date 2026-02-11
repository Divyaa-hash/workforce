from django.db.models import Q
from .models import DiagnosticSubmission, JobRole


class RulesEngine:
    """Rule-based decision engine"""
    
    @staticmethod
    def calculate_level_risk(submission):
        """Calculate risk for Level 1 roles"""
        risk_score = 0
        
        # Rule 1: Budget approval is critical
        if not submission.q4_budget_approval:
            risk_score += 3
            submission.decline_category = 'budget_constraint'
        
        # Rule 2: High financial risk
        if submission.q2_financial_risk and submission.q2_financial_risk >= 4:
            risk_score += 2
        
        # Rule 3: Low strategic priority
        if submission.q5_strategic_priority == 'low':
            risk_score += 1
            submission.decline_category = 'business_misalignment'
        
        # Rule 4: Poor business alignment
        if submission.q1_business_alignment and submission.q1_business_alignment <= 2:
            risk_score += 2
        
        return risk_score
    
    @staticmethod
    def calculate_level_2_risk(submission):
        """Calculate risk for Level 2 roles"""
        risk_score = 0
        
        # Rule 1: Low skill availability
        if submission.q6_skill_availability == 'low':
            risk_score += 2
            submission.decline_category = 'skill_unavailability'
        
        # Rule 2: High timeline risk
        if submission.q9_timeline_risk == 'high':
            risk_score += 2
            submission.decline_category = 'timeline_risk'
        
        # Rule 3: No mentor available
        if not submission.q10_mentor_available:
            risk_score += 1
        
        # Rule 4: High team dependency
        if submission.q8_team_dependency and submission.q8_team_dependency >= 4:
            risk_score += 1
            submission.decline_category = 'team_dependency'
        
        return risk_score
    
    @staticmethod
    def calculate_level_3_risk(submission):
        """Calculate risk for Level 3 roles"""
        risk_score = 0
        
        # Rule 1: Low talent availability
        if submission.q11_talent_availability == 'low':
            risk_score += 2
            submission.decline_category = 'skill_unavailability'
        
        # Rule 2: Cost not validated
        if not submission.q12_cost_validation:
            risk_score += 2
            submission.decline_category = 'budget_constraint'
        
        # Rule 3: High market competition
        if submission.q15_market_competition == 'high':
            risk_score += 1
        
        # Rule 4: Low process readiness
        if submission.q13_process_readiness and submission.q13_process_readiness <= 2:
            risk_score += 1
            submission.decline_category = 'operational_gap'
        
        return risk_score
    
    @staticmethod
    def get_risk_level(risk_score):
        """Convert risk score to risk level"""
        if risk_score >= 3:
            return 'high'
        elif risk_score >= 1:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def get_corrective_guidance(decline_category):
        """Get corrective guidance based on decline category"""
        guidance_map = {
            'budget_constraint': [
                'Increase budget allocation',
                'Reduce role scope or responsibilities',
                'Consider contract or part-time hiring'
            ],
            'skill_unavailability': [
                'Revise skill requirements',
                'Provide training for existing team',
                'Consider outsourcing specific tasks'
            ],
            'timeline_risk': [
                'Delay hiring timeline',
                'Hire contract resource for immediate needs',
                'Redistribute workload temporarily'
            ],
            'team_dependency': [
                'Assign experienced mentor',
                'Restructure team responsibilities',
                'Provide cross-training'
            ],
            'business_misalignment': [
                'Re-evaluate business strategy',
                'Conduct market analysis',
                'Re-align role with business goals'
            ],
            'operational_gap': [
                'Improve onboarding process',
                'Set up necessary infrastructure',
                'Define clear processes first'
            ]
        }
        
        return guidance_map.get(decline_category, ['Review specific concerns'])


class OverallDecisionEngine:
    """Engine for final decision after all submissions"""
    
    @staticmethod
    def calculate_overall_risk(job_role):
        submissions = DiagnosticSubmission.objects.filter(job_role=job_role)
        
        if not submissions.exists():
            return 'unknown'
        
        # Count risk levels
        risk_counts = {'high': 0, 'medium': 0, 'low': 0}
        decline_count = 0
        
        for submission in submissions:
            risk_counts[submission.risk_level] += 1
            if submission.decision == 'decline':
                decline_count += 1
        
        # Rule 1: Any high risk from Level 1 results in high overall risk
        level1_high = submissions.filter(
            user__role__in=['founder', 'co_founder', 'ceo', 'cfo'],
            risk_level='high'
        ).exists()
        
        if level1_high:
            return 'high'
        
        # Rule 2: Majority decline results in high risk
        if decline_count >= len(submissions) / 2:
            return 'high'
        
        # Rule 3: Any medium risk results in medium overall risk
        if risk_counts['medium'] > 0 or risk_counts['high'] > 0:
            return 'medium'
        
        return 'low'
    
    @staticmethod
    def get_final_recommendation(job_role):
        """Generate final hiring recommendation"""
        from .models import DiagnosticSubmission  # Import here to avoid circular import
        
        submissions = DiagnosticSubmission.objects.filter(job_role=job_role)
        overall_risk = OverallDecisionEngine.calculate_overall_risk(job_role)
        
        # Rule-based final decision
        if overall_risk == 'low':
            return {
                'decision': 'Proceed with hiring',
                'risk': 'low',
                'conditions': 'No special conditions required'
            }
        elif overall_risk == 'medium':
            return {
                'decision': 'Proceed with conditions',
                'risk': 'medium',
                'conditions': 'Address medium risk areas before proceeding'
            }
        else:  # high risk
            decline_reasons = submissions.filter(
                decision='decline'
            ).values_list('decline_category', flat=True).distinct()
            
            return {
                'decision': 'Delay or cancel hiring',
                'risk': 'high',
                'conditions': f'Address critical issues: {", ".join(decline_reasons)}'
            }