"""
Test script to verify that Founder and Co-Founder users see different questions.
This script verifies:
1. Template shows role-specific questions
2. Forms include role-specific fields
3. Risk calculation handles role-specific logic
"""

import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from diagnostic_app.models import User, JobRole, DiagnosticSubmission, RoleAssignment
from diagnostic_app.forms import DiagnosticForm
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def test_template_rendering():
    """Test that template renders different questions for Founder vs Co-Founder"""
    print("=" * 60)
    print("TEST 1: Template Rendering - Role-Specific Questions")
    print("=" * 60)
    
    # Create test users if they don't exist
    founder, _ = User.objects.get_or_create(
        username='test_founder',
        defaults={'email': 'test_founder@test.com', 'role': 'founder'}
    )
    founder.set_password('test123')
    founder.save()
    
    co_founder, _ = User.objects.get_or_create(
        username='test_cofounder',
        defaults={'email': 'test_cofounder@test.com', 'role': 'co_founder'}
    )
    co_founder.set_password('test123')
    co_founder.save()
    
    # Create a test job role
    job_role, _ = JobRole.objects.get_or_create(
        title='Test Software Engineer',
        defaults={
            'department': 'Engineering',
            'description': 'Test role',
            'required_skills': 'Python, Django',
            'experience_level': 'Mid-level',
            'budget_range': '$80k-$100k',
            'urgency': 'medium',
            'created_by': founder,
            'status': 'active'
        }
    )
    
    # Test Founder template rendering
    print("\n1. Testing Founder template...")
    founder_context = {
        'user': founder,
        'job': job_role
    }
    founder_html = render_to_string('diagnostic_app/questionnaire.html', founder_context)
    
    # Check for Founder-specific questions
    founder_questions = [
        'q_founder_vision_alignment',
        'q_founder_strategic_fit',
        'q_founder_market_positioning',
        'q_founder_resource_priority',
        'q_founder_equity_consideration'
    ]
    
    founder_found = []
    founder_missing = []
    for q in founder_questions:
        if q in founder_html:
            founder_found.append(q)
            print(f"   [OK] Found: {q}")
        else:
            founder_missing.append(q)
            print(f"   [FAIL] Missing: {q}")
    
    # Check that Co-Founder questions are NOT in Founder template
    cofounder_questions = [
        'q_cofounder_partnership_dynamics',
        'q_cofounder_complementary_skills',
        'q_cofounder_team_chemistry',
        'q_cofounder_decision_making',
        'q_cofounder_culture_fit'
    ]
    
    print("\n   Checking that Co-Founder questions are NOT present...")
    for q in cofounder_questions:
        if q not in founder_html:
            print(f"   [OK] Correctly excluded: {q}")
        else:
            print(f"   [FAIL] Should not be present: {q}")
    
    # Test Co-Founder template rendering
    print("\n2. Testing Co-Founder template...")
    cofounder_context = {
        'user': co_founder,
        'job': job_role
    }
    cofounder_html = render_to_string('diagnostic_app/questionnaire.html', cofounder_context)
    
    # Check for Co-Founder-specific questions
    cofounder_found = []
    cofounder_missing = []
    for q in cofounder_questions:
        if q in cofounder_html:
            cofounder_found.append(q)
            print(f"   [OK] Found: {q}")
        else:
            cofounder_missing.append(q)
            print(f"   [FAIL] Missing: {q}")
    
    # Check that Founder questions are NOT in Co-Founder template
    print("\n   Checking that Founder questions are NOT present...")
    for q in founder_questions:
        if q not in cofounder_html:
            print(f"   [OK] Correctly excluded: {q}")
        else:
            print(f"   [FAIL] Should not be present: {q}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Template Test Summary:")
    print(f"Founder questions found: {len(founder_found)}/{len(founder_questions)}")
    print(f"Co-Founder questions found: {len(cofounder_found)}/{len(cofounder_questions)}")
    
    if len(founder_found) == len(founder_questions) and len(cofounder_found) == len(cofounder_questions):
        print("[PASS] Template test PASSED")
        return True
    else:
        print("[FAIL] Template test FAILED")
        return False


def test_form_fields():
    """Test that forms include role-specific fields"""
    print("\n" + "=" * 60)
    print("TEST 2: Form Fields - Role-Specific Fields")
    print("=" * 60)
    
    founder, _ = User.objects.get_or_create(
        username='test_founder',
        defaults={'email': 'test_founder@test.com', 'role': 'founder'}
    )
    
    co_founder, _ = User.objects.get_or_create(
        username='test_cofounder',
        defaults={'email': 'test_cofounder@test.com', 'role': 'co_founder'}
    )
    
    # Test Founder form
    print("\n1. Testing Founder form fields...")
    founder_form = DiagnosticForm(user=founder)
    founder_fields = list(founder_form.fields.keys())
    
    founder_expected_fields = [
        'q_founder_vision_alignment',
        'q_founder_strategic_fit',
        'q_founder_market_positioning',
        'q_founder_resource_priority',
        'q_founder_equity_consideration',
        'decision'
    ]
    
    founder_found = []
    for field in founder_expected_fields:
        if field in founder_fields:
            founder_found.append(field)
            print(f"   [OK] Found field: {field}")
        else:
            print(f"   [FAIL] Missing field: {field}")
    
    # Test Co-Founder form
    print("\n2. Testing Co-Founder form fields...")
    cofounder_form = DiagnosticForm(user=co_founder)
    cofounder_fields = list(cofounder_form.fields.keys())
    
    cofounder_expected_fields = [
        'q_cofounder_partnership_dynamics',
        'q_cofounder_complementary_skills',
        'q_cofounder_team_chemistry',
        'q_cofounder_decision_making',
        'q_cofounder_culture_fit',
        'decision'
    ]
    
    cofounder_found = []
    for field in cofounder_expected_fields:
        if field in cofounder_fields:
            cofounder_found.append(field)
            print(f"   [OK] Found field: {field}")
        else:
            print(f"   [FAIL] Missing field: {field}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Form Test Summary:")
    print(f"Founder fields found: {len(founder_found)}/{len(founder_expected_fields)}")
    print(f"Co-Founder fields found: {len(cofounder_found)}/{len(cofounder_expected_fields)}")
    
    if len(founder_found) == len(founder_expected_fields) and len(cofounder_found) == len(cofounder_expected_fields):
        print("[PASS] Form test PASSED")
        return True
    else:
        print("[FAIL] Form test FAILED")
        return False


def test_risk_calculation():
    """Test that risk calculation handles role-specific logic"""
    print("\n" + "=" * 60)
    print("TEST 3: Risk Calculation - Role-Specific Logic")
    print("=" * 60)
    
    founder, _ = User.objects.get_or_create(
        username='test_founder',
        defaults={'email': 'test_founder@test.com', 'role': 'founder'}
    )
    
    co_founder, _ = User.objects.get_or_create(
        username='test_cofounder',
        defaults={'email': 'test_cofounder@test.com', 'role': 'co_founder'}
    )
    
    # Create a test job role
    job_role, _ = JobRole.objects.get_or_create(
        title='Test Software Engineer',
        defaults={
            'department': 'Engineering',
            'description': 'Test role',
            'required_skills': 'Python, Django',
            'experience_level': 'Mid-level',
            'budget_range': '$80k-$100k',
            'urgency': 'medium',
            'created_by': founder,
            'status': 'active'
        }
    )
    
    # Test Founder risk calculation with low scores (should be high risk)
    print("\n1. Testing Founder risk calculation (low scores = high risk)...")
    founder_submission = DiagnosticSubmission(
        job_role=job_role,
        user=founder,
        decision='approve',
        q_founder_vision_alignment=1,  # Low score
        q_founder_strategic_fit=1,  # Low score
        q_founder_market_positioning=1,  # Low score
        q_founder_resource_priority='low',
        q_founder_equity_consideration='equity_required'
    )
    founder_submission.calculate_risk()
    print(f"   Founder risk level: {founder_submission.risk_level}")
    print(f"   Expected: high (due to multiple low scores)")
    
    # Test Co-Founder risk calculation with low scores (should be high risk)
    print("\n2. Testing Co-Founder risk calculation (low scores = high risk)...")
    cofounder_submission = DiagnosticSubmission(
        job_role=job_role,
        user=co_founder,
        decision='approve',
        q_cofounder_partnership_dynamics=1,  # Low score
        q_cofounder_complementary_skills=1,  # Low score
        q_cofounder_team_chemistry=1,  # Low score
        q_cofounder_decision_making='low',
        q_cofounder_culture_fit=1  # Low score
    )
    cofounder_submission.calculate_risk()
    print(f"   Co-Founder risk level: {cofounder_submission.risk_level}")
    print(f"   Expected: high (due to multiple low scores)")
    
    # Test Founder risk calculation with high scores (should be low risk)
    print("\n3. Testing Founder risk calculation (high scores = low risk)...")
    founder_submission_high = DiagnosticSubmission(
        job_role=job_role,
        user=founder,
        decision='approve',
        q_founder_vision_alignment=5,  # High score
        q_founder_strategic_fit=5,  # High score
        q_founder_market_positioning=5,  # High score
        q_founder_resource_priority='high',
        q_founder_equity_consideration='cash_only'
    )
    founder_submission_high.calculate_risk()
    print(f"   Founder risk level: {founder_submission_high.risk_level}")
    print(f"   Expected: low (due to multiple high scores)")
    
    # Test Co-Founder risk calculation with high scores (should be low risk)
    print("\n4. Testing Co-Founder risk calculation (high scores = low risk)...")
    cofounder_submission_high = DiagnosticSubmission(
        job_role=job_role,
        user=co_founder,
        decision='approve',
        q_cofounder_partnership_dynamics=5,  # High score
        q_cofounder_complementary_skills=5,  # High score
        q_cofounder_team_chemistry=5,  # High score
        q_cofounder_decision_making='high',
        q_cofounder_culture_fit=5  # High score
    )
    cofounder_submission_high.calculate_risk()
    print(f"   Co-Founder risk level: {cofounder_submission_high.risk_level}")
    print(f"   Expected: low (due to multiple high scores)")
    
    # Summary
    print("\n" + "=" * 60)
    print("Risk Calculation Test Summary:")
    print(f"Founder low scores -> risk: {founder_submission.risk_level}")
    print(f"Co-Founder low scores -> risk: {cofounder_submission.risk_level}")
    print(f"Founder high scores -> risk: {founder_submission_high.risk_level}")
    print(f"Co-Founder high scores -> risk: {cofounder_submission_high.risk_level}")
    
    if (founder_submission.risk_level == 'high' and 
        cofounder_submission.risk_level == 'high' and
        founder_submission_high.risk_level == 'low' and
        cofounder_submission_high.risk_level == 'low'):
        print("[PASS] Risk calculation test PASSED")
        return True
    else:
        print("[FAIL] Risk calculation test FAILED")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ROLE-SPECIFIC QUESTIONS IMPLEMENTATION TEST")
    print("=" * 60)
    print("\nThis test verifies that Founder and Co-Founder users see")
    print("different questions and have different risk calculations.\n")
    
    results = []
    
    # Run tests
    results.append(("Template Rendering", test_template_rendering()))
    results.append(("Form Fields", test_form_fields()))
    results.append(("Risk Calculation", test_risk_calculation()))
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "[PASS] PASSED" if passed else "[FAIL] FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED!")
        print("Founder and Co-Founder users correctly see different questions.")
    else:
        print("[WARNING] SOME TESTS FAILED")
        print("Please review the implementation.")
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    main()
