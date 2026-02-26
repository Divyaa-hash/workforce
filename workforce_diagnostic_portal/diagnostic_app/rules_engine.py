from django.db.models import Q
from .models import DiagnosticSubmission, JobRole, AuditLog


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
    """Enhanced engine for accurate final decision after all submissions"""
    
    @staticmethod
    def calculate_overall_risk(job_role):
        """Calculate comprehensive risk assessment with weighted factors"""
        submissions = DiagnosticSubmission.objects.filter(job_role=job_role)
        
        if not submissions.exists():
            return 'unknown'
        
        # Weight factors by level importance
        level_weights = {
            1: 0.5,  # Strategic level (Founder, Co-founder, CEO, CFO) - 50% weight
            2: 0.3,  # Execution level (CTO, COO, Project Head) - 30% weight  
            3: 0.2   # HR level (HR Manager, Recruiter, HR Executive) - 20% weight
        }
        
        # Calculate weighted risk score
        total_weighted_score = 0
        total_weight = 0
        decline_count = 0
        critical_issues = []
        
        for submission in submissions:
            user_level = submission.user.get_level()
            weight = level_weights.get(user_level, 0.1)
            
            # Convert risk levels to numeric scores
            risk_scores = {'low': 1, 'medium': 3, 'high': 5}
            risk_score = risk_scores.get(submission.risk_level, 3)
            
            # Apply decision factor (decline = higher risk)
            if submission.decision == 'decline':
                risk_score *= 1.5  # 50% penalty for decline
                decline_count += 1
                if submission.decline_category:
                    critical_issues.append(submission.decline_category)
            
            total_weighted_score += risk_score * weight
            total_weight += weight
        
        # Normalize score
        if total_weight > 0:
            final_score = total_weighted_score / total_weight
        else:
            final_score = 3
        
        # Critical issue override
        level1_decline = submissions.filter(
            user__role__in=['founder', 'co_founder'],
            decision='decline'
        ).exists()
        
        if level1_decline:
            return 'high'
        
        # Determine risk based on comprehensive scoring
        if final_score >= 4.0:
            return 'high'
        elif final_score >= 2.5:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def get_final_recommendation(job_role, user=None, ip_address=None):
        """Generate accurate final hiring recommendation with detailed analysis"""
        submissions = DiagnosticSubmission.objects.filter(job_role=job_role)
        overall_risk = OverallDecisionEngine.calculate_overall_risk(job_role)
        
        # Detailed analysis
        total_submissions = submissions.count()
        approve_count = submissions.filter(decision='approve').count()
        decline_count = submissions.filter(decision='decline').count()
        
        # Level-specific analysis
        level1_subs = submissions.filter(user__role__in=['founder', 'co_founder', 'ceo', 'cfo'])
        level2_subs = submissions.filter(user__role__in=['cto', 'coo', 'project_head']) 
        level3_subs = submissions.filter(user__role__in=['hr_manager', 'recruiter', 'hr_executive'])
        
        # Critical decline categories
        decline_categories = list(submissions.filter(
            decision='decline'
        ).values_list('decline_category', flat=True).distinct())
        
        # Total expected submissions: 4 (Level 1) + 3 (Level 2) + 3 (Level 3) = 10
        expected_submissions = 10.0
        completion_rate = min(total_submissions / expected_submissions, 1.0)  # Cap at 100%
        consensus_strength = abs(approve_count - decline_count) / total_submissions if total_submissions > 0 else 0
        
        # Enhanced decision logic
        if overall_risk == 'low':
            if completion_rate >= 0.8 and consensus_strength >= 0.6:
                decision = 'Proceed with hiring - High Confidence'
                conditions = 'All assessments aligned positively'
                confidence = 'High'
            else:
                decision = 'Proceed with hiring - Moderate Confidence'
                conditions = 'Most assessments positive, consider remaining inputs'
                confidence = 'Medium'
                
        elif overall_risk == 'medium':
            if decline_count <= total_submissions * 0.3:
                decision = 'Proceed with conditions - Manageable Risk'
                conditions = f'Address specific concerns: {", ".join(set(decline_categories[:3]))}'
                confidence = 'Medium'
            else:
                decision = 'Proceed with caution - Significant Concerns'
                conditions = f'Major issues to resolve: {", ".join(set(decline_categories))}'
                confidence = 'Low'
                
        else:  # high risk
            level1_decline = level1_subs.filter(decision='decline').exists()
            if level1_decline:
                decision = 'Do not proceed - Strategic Opposition'
                conditions = 'Founders/Co-founders or CFO oppose this hiring'
                confidence = 'High'
            elif decline_count >= total_submissions * 0.6:
                decision = 'Do not proceed - Widespread Opposition'
                conditions = f'Majority oppose: {", ".join(set(decline_categories))}'
                confidence = 'High'
            else:
                decision = 'Delay hiring - Critical Issues Identified'
                conditions = f'Resolve critical issues: {", ".join(set(decline_categories))}'
                confidence = 'Medium'
        
        # Generate key findings
        key_findings = []
        
        # Strategic alignment
        level1_approve = level1_subs.filter(decision='approve').count()
        if level1_approve > 0:
            key_findings.append(f"Strategic level: {level1_approve}/{level1_subs.count()} approve")
        
        # Execution readiness  
        level2_approve = level2_subs.filter(decision='approve').count()
        if level2_approve > 0:
            key_findings.append(f"Execution level: {level2_approve}/{level2_subs.count()} approve")
        
        # HR feasibility
        level3_approve = level3_subs.filter(decision='approve').count()
        if level3_approve > 0:
            key_findings.append(f"HR level: {level3_approve}/{level3_subs.count()} approve")
        
        # Risk factors
        if decline_categories:
            key_findings.append(f"Primary concerns: {', '.join(set(decline_categories[:2]))}")
        
        # Completion status
        key_findings.append(f"Assessment completion: {total_submissions}/10 ({int(completion_rate*100)}%)")
        
        recommendation = {
            'decision': decision,
            'risk': overall_risk,
            'conditions': conditions,
            'confidence': confidence,
            'completion_rate': int(completion_rate * 100),
            'approve_count': approve_count,
            'decline_count': decline_count,
            'total_assessments': total_submissions,
            'key_findings': key_findings,
            'decision_display': decision,
            'risk_level_display': overall_risk.title() + ' Risk'
        }

        # Log final decision to audit
        AuditLog.objects.create(
            event_type='final_decision_generated',
            user=user,
            entity_type='job_role',
            entity_id=job_role.id,
            metadata={
                'final_decision': recommendation['decision'],
                'overall_risk': recommendation['risk'],
                'conditions': recommendation['conditions'],
                'decline_categories': decline_categories,
            },
            ip_address=ip_address,
        )

        return recommendation