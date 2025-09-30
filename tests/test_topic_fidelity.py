#!/usr/bin/env python3
"""
Regression tests for topic fidelity across the research pipeline.

These tests ensure that topic keywords are properly extracted and maintained
throughout the clarify → brief → plan pipeline phases.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from agents.clarify_agent import ClarifyAgent
from agents.research_brief_agent import ResearchBriefAgent
from agents.supervisor_planner_agent import SupervisorPlannerAgent
from utils import extract_topic_keywords


class TestTopicFidelity:
    """Test suite for topic fidelity across pipeline phases."""

    def test_keyword_extraction_ai_education(self):
        """Test keyword extraction for AI education topic."""
        query = "The Applications of Artificial Intelligence in Education: Opportunities and Challenges"
        keywords = extract_topic_keywords(query)

        # Should extract meaningful AI/education terms
        assert len(keywords) > 0, "Should extract at least one keyword"
        keywords_str = ' '.join(keywords).lower()

        # Check for AI/education related terms
        ai_terms = ['artificial', 'intelligence', 'education', 'applications', 'opportunities', 'challenges']
        assert any(term in keywords_str for term in ai_terms), f"Expected AI/education terms, got: {keywords}"

        # Should not contain food-related terms
        food_terms = ['food', 'ultra-processed', 'nutrition', 'diet']
        assert not any(term in keywords_str for term in food_terms), f"Unexpected food terms in: {keywords}"

    def test_keyword_extraction_climate_change(self):
        """Test keyword extraction for climate change topic."""
        query = "Climate Change Impacts on Coastal Communities: Adaptation Strategies"
        keywords = extract_topic_keywords(query)

        assert len(keywords) > 0
        keywords_str = ' '.join(keywords).lower()

        # Should contain climate-related terms
        climate_terms = ['climate', 'change', 'coastal', 'communities', 'adaptation', 'strategies']
        assert any(term in keywords_str for term in climate_terms), f"Expected climate terms, got: {keywords}"

    def test_brief_includes_topic_keywords(self):
        """Test that research brief includes extracted topic keywords."""
        query = "Machine Learning Applications in Healthcare Diagnostics"

        # Phase 1: Clarify
        clarify_agent = ClarifyAgent()
        clarify_result = clarify_agent.clarify_query(query)

        # Phase 2: Brief
        brief_agent = ResearchBriefAgent()
        brief_markdown = brief_agent.create_brief(clarify_result)

        # Check that brief includes topic keywords section
        assert "**Topic Keywords:**" in brief_markdown, "Brief should include topic keywords section"

        # Extract keywords from brief
        lines = brief_markdown.split('\n')
        keywords_line = None
        for line in lines:
            if "**Topic Keywords:**" in line:
                keywords_line = line
                break

        assert keywords_line is not None, "Topic keywords line should be found"

        keywords_str = keywords_line.split("**Topic Keywords:**")[1].strip()
        keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]

        assert len(keywords) > 0, "Should have at least one keyword in brief"

        # Should contain healthcare/ML terms
        keywords_str = ' '.join(keywords).lower()
        expected_terms = ['machine', 'learning', 'healthcare', 'diagnostics', 'applications']
        assert any(term in keywords_str for term in expected_terms), f"Expected ML/healthcare terms, got: {keywords}"

    def test_plan_uses_topic_keywords(self):
        """Test that supervisor planner generates topic-specific subqueries."""
        query = "Renewable Energy Solutions for Urban Development"

        # Get through clarify and brief phases
        clarify_agent = ClarifyAgent()
        clarify_result = clarify_agent.clarify_query(query)

        brief_agent = ResearchBriefAgent()
        brief_markdown = brief_agent.create_brief(clarify_result)

        # Phase 3: Plan
        planner_agent = SupervisorPlannerAgent()
        plan = planner_agent.create_plan(brief_markdown)

        subqueries = plan.get('plan', [])
        assert len(subqueries) > 0, "Should generate at least one subquery"

        # Check that subqueries contain topic-specific terms
        energy_terms = ['renewable', 'energy', 'urban', 'development', 'solutions']
        generic_terms = ['current', 'state', 'research', 'this']

        for subquery in subqueries[:3]:  # Check first 3 subqueries
            query_text = subquery.get('subquery', '').lower()

            # Should contain some energy-related terms
            has_energy_terms = any(term in query_text for term in energy_terms)
            is_mostly_generic = all(word in generic_terms for word in query_text.split() if len(word) > 3)

            # Either should have energy terms OR not be mostly generic
            assert has_energy_terms or not is_mostly_generic, f"Subquery too generic or off-topic: {query_text}"

    def test_no_topic_drift_regression(self):
        """Regression test for the specific AI education topic drift issue."""
        query = "The Applications of Artificial Intelligence in Education: Opportunities and Challenges"

        # Complete pipeline through plan phase
        clarify_agent = ClarifyAgent()
        clarify_result = clarify_agent.clarify_query(query)

        brief_agent = ResearchBriefAgent()
        brief_markdown = brief_agent.create_brief(clarify_result)

        planner_agent = SupervisorPlannerAgent()
        plan = planner_agent.create_plan(brief_markdown)

        subqueries = plan.get('plan', [])
        assert len(subqueries) > 0, "Should generate subqueries"

        # Ensure none of the subqueries are about food
        food_terms = ['food', 'ultra-processed', 'nutrition', 'diet', 'health benefits', 'systematic review']

        for subquery in subqueries:
            query_text = subquery.get('subquery', '').lower()
            has_food_terms = any(term in query_text for term in food_terms)
            assert not has_food_terms, f"Found food-related terms in AI education query: {query_text}"

        # Should contain AI/education related terms
        ai_education_terms = ['artificial', 'intelligence', 'education', 'learning', 'applications', 'opportunities', 'challenges']
        all_queries_text = ' '.join([sq.get('subquery', '') for sq in subqueries]).lower()
        has_ai_terms = any(term in all_queries_text for term in ai_education_terms)
        assert has_ai_terms, f"Expected AI/education terms in subqueries, but got: {[sq.get('subquery') for sq in subqueries]}"

    def test_topic_keywords_flow_consistency(self):
        """Test that topic keywords are consistent across pipeline phases."""
        query = "Blockchain Technology in Supply Chain Management"

        # Phase 1: Extract initial keywords
        initial_keywords = extract_topic_keywords(query)

        # Phase 2: Get keywords from brief
        clarify_agent = ClarifyAgent()
        clarify_result = clarify_agent.clarify_query(query)

        brief_agent = ResearchBriefAgent()
        brief_markdown = brief_agent.create_brief(clarify_result)

        # Extract keywords from brief
        brief_keywords = []
        lines = brief_markdown.split('\n')
        for line in lines:
            if "**Topic Keywords:**" in line:
                keywords_str = line.split("**Topic Keywords:**")[1].strip()
                brief_keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
                break

        # Phase 3: Check that plan uses these keywords
        planner_agent = SupervisorPlannerAgent()
        plan = planner_agent.create_plan(brief_markdown)

        subqueries = plan.get('plan', [])
        all_queries_text = ' '.join([sq.get('subquery', '') for sq in subqueries]).lower()

        # At least some of the brief keywords should appear in the subqueries
        keyword_matches = 0
        for keyword in brief_keywords:
            if keyword.lower() in all_queries_text:
                keyword_matches += 1

        assert keyword_matches > 0, f"Brief keywords {brief_keywords} not found in subqueries: {[sq.get('subquery') for sq in subqueries]}"

    @pytest.mark.parametrize("query,expected_domain", [
        ("Machine Learning in Medical Imaging", ["machine", "learning", "medical", "imaging"]),
        ("Solar Panel Efficiency in Cold Climates", ["solar", "panel", "efficiency", "cold", "climates"]),
        ("Social Media Impact on Teenage Mental Health", ["social", "media", "teenage", "mental", "health"]),
        ("Quantum Computing Applications in Cryptography", ["quantum", "computing", "applications", "cryptography"])
    ])
    def test_domain_specific_extraction(self, query, expected_domain):
        """Test keyword extraction for various domain-specific queries."""
        keywords = extract_topic_keywords(query)
        keywords_str = ' '.join(keywords).lower()

        # Should contain at least one expected domain term
        domain_matches = sum(1 for term in expected_domain if term in keywords_str)
        assert domain_matches > 0, f"Expected domain terms {expected_domain} not found in {keywords}"


if __name__ == "__main__":
    # Run tests directly
    import sys
    test_instance = TestTopicFidelity()

    tests = [
        test_instance.test_keyword_extraction_ai_education,
        test_instance.test_keyword_extraction_climate_change,
        test_instance.test_brief_includes_topic_keywords,
        test_instance.test_plan_uses_topic_keywords,
        test_instance.test_no_topic_drift_regression,
        test_instance.test_topic_keywords_flow_consistency
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(failed)