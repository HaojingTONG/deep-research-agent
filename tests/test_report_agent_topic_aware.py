#!/usr/bin/env python3
"""
Unit tests for topic-aware report generation in ReportAgent.

Tests ensure that Executive Summary and Key Insights align with the actual query topic
and do not contain hard-coded food-related language.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from agents.report_agent import ReportAgent


class TestReportAgentTopicAware:
    """Test suite for topic-aware report generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.report_agent = ReportAgent()

        # Sample evidence list for testing
        self.sample_evidence = [
            {
                "title": "AI in Education Research 2024",
                "url": "https://example.com/ai-education",
                "publisher": "Education Technology Journal",
                "date": "2024-01-15",
                "quality": 4.5,
                "snippets": ["AI tools show promising results in personalized learning"]
            },
            {
                "title": "Machine Learning Applications in Classrooms",
                "url": "https://example.com/ml-classrooms",
                "publisher": "IEEE Education",
                "date": "2024-02-20",
                "quality": 4.0,
                "snippets": ["Adaptive learning systems improve student outcomes"]
            }
        ]

        # Sample compressed JSON with food-related findings (simulating the bug)
        self.sample_compressed_ai_with_food_bias = {
            "key_findings": [
                "Multiple studies link ultra-processed foods to increased health risks including cardiovascular disease and metabolic disorders [0,1]",
                "Research methodologies vary significantly across studies, affecting result comparability [0,1]"
            ],
            "clusters": [
                {
                    "label": "Health Risks",
                    "items": [0, 1]
                },
                {
                    "label": "Methodology",
                    "items": [0, 1]
                }
            ],
            "conflicts": [],
            "gaps": ["Need more research on long-term effects"],
            "coverage_stats": {
                "unique_sources": 2,
                "domains": 2,
                "total_evidence": 2,
                "high_quality_sources": 2
            }
        }

    def test_ai_education_query_executive_summary(self):
        """Test that AI education query produces topic-appropriate executive summary."""
        ai_query = "The Applications of Artificial Intelligence in Education: Opportunities and Challenges"

        summary = self.report_agent._generate_executive_summary(
            self.sample_compressed_ai_with_food_bias["key_findings"],
            [],
            "consumer",
            ai_query
        )

        # Should contain AI/education terms
        assert "AI in education" in summary or "artificial intelligence" in summary.lower()
        assert "educational technology" in summary or "education" in summary

        # Should NOT contain food-related terms
        banned_phrases = ["ultra-processed foods", "dietary", "nutrition", "health organization recommendations"]
        for phrase in banned_phrases:
            assert phrase not in summary, f"Found banned phrase '{phrase}' in summary: {summary}"

        # Should use appropriate terminology for AI domain
        assert "opportunities" in summary.lower()
        assert "challenges" in summary.lower() or "risks" in summary.lower()

    def test_ai_education_query_key_insights(self):
        """Test that AI education query produces topic-appropriate key insights."""
        ai_query = "The Applications of Artificial Intelligence in Education: Opportunities and Challenges"

        insights = self.report_agent._generate_key_insights(
            self.sample_compressed_ai_with_food_bias["key_findings"],
            self.sample_compressed_ai_with_food_bias["clusters"],
            self.sample_evidence,
            "consumer",
            ai_query
        )

        # Should contain adapted text, not original food text
        assert "ultra-processed foods" not in insights
        assert "AI in education" in insights or "artificial intelligence" in insights.lower()

        # Should contain confidence indicators
        assert "CONFIDENCE" in insights or "UNCERTAIN" in insights

    def test_climate_change_query_context(self):
        """Test that climate change query produces appropriate context."""
        climate_query = "Climate Change Impacts on Coastal Communities: Adaptation Strategies"

        topic_context = self.report_agent._get_topic_context(climate_query)

        assert topic_context['domain'] == 'climate'
        assert topic_context['main_topic'] == 'climate and environment'
        assert topic_context['opportunities_term'] == 'solutions'
        assert topic_context['risks_term'] == 'risks'
        assert topic_context['guidance_term'] == 'policy recommendations'

    def test_health_query_preserves_health_terminology(self):
        """Test that health queries still use appropriate health terminology."""
        health_query = "Benefits and Risks of Mediterranean Diet: Evidence Review"

        topic_context = self.report_agent._get_topic_context(health_query)

        assert topic_context['domain'] == 'health'
        assert topic_context['opportunities_term'] == 'benefits'
        assert topic_context['guidance_term'] == 'health recommendations'

        # Test executive summary
        summary = self.report_agent._generate_executive_summary(
            ["Mediterranean diet shows health benefits [0]"],
            [],
            "consumer",
            health_query
        )

        assert "health organization recommendations" in summary  # Should keep this for health topics

    def test_generic_query_handling(self):
        """Test that generic queries get appropriate topic-neutral context."""
        generic_query = "Blockchain Technology in Supply Chain Management"

        topic_context = self.report_agent._get_topic_context(generic_query)

        assert topic_context['domain'] == 'general'
        assert topic_context['opportunities_term'] == 'opportunities'
        assert topic_context['risks_term'] == 'challenges'

    def test_adapt_finding_to_topic_method(self):
        """Test the _adapt_finding_to_topic helper method."""
        ai_context = {
            'main_topic': 'AI in education',
            'subject_area': 'educational technology',
            'risks_term': 'challenges',
            'opportunities_term': 'opportunities'
        }

        # Test adaptation of food-specific text
        food_text = "Ultra-processed foods show health risks in dietary studies"
        adapted = self.report_agent._adapt_finding_to_topic(food_text, ai_context)

        assert "ultra-processed foods" not in adapted
        assert "AI in education" in adapted
        assert "educational technology" in adapted

    def test_executive_summary_bullet_structure(self):
        """Test that executive summary maintains proper bullet structure."""
        ai_query = "Machine Learning Applications in Healthcare Diagnostics"

        summary = self.report_agent._generate_executive_summary(
            ["AI shows promising results in diagnostic accuracy [0]"],
            [],
            "executive",
            ai_query
        )

        # Should have 5 bullets
        bullets = [line for line in summary.split('\n') if line.strip().startswith('•')]
        assert len(bullets) == 5

        # Each bullet should have a bold title
        for bullet in bullets:
            assert '**' in bullet and '**:' in bullet

    def test_different_audiences_get_appropriate_language(self):
        """Test that different audiences get appropriate language."""
        ai_query = "AI Applications in Education"
        findings = ["AI tools improve learning outcomes [0]"]

        # Consumer audience
        consumer_summary = self.report_agent._generate_executive_summary(
            findings, [], "consumer", ai_query
        )
        assert "implementation guidance" in consumer_summary.lower()

        # Executive audience
        exec_summary = self.report_agent._generate_executive_summary(
            findings, [], "executive", ai_query
        )
        assert "strategic direction" in exec_summary.lower()

        # Researcher audience
        researcher_summary = self.report_agent._generate_executive_summary(
            findings, [], "researcher", ai_query
        )
        assert "research priorities" in researcher_summary.lower()

    def test_key_insights_cluster_processing(self):
        """Test that key insights properly process cluster data."""
        ai_query = "AI in Education Research"

        clusters = [
            {"label": "Methodology", "items": [0]},
            {"label": "Health Risks", "items": [1]}  # This should be adapted for AI context
        ]

        findings = [
            "Research methodologies vary significantly [0]",
            "Multiple health risks identified [1]"
        ]

        insights = self.report_agent._generate_key_insights(
            findings, clusters, self.sample_evidence, "researcher", ai_query
        )

        # Should adapt "Health Risks" to be appropriate for AI context
        assert "Methodological Considerations" in insights
        assert "Health Risks" not in insights or "AI in education" in insights

    def test_no_food_terms_in_ai_report(self):
        """Integration test ensuring no food terms appear in AI education report."""
        ai_query = "The Applications of Artificial Intelligence in Education: Opportunities and Challenges"

        report = self.report_agent.generate_report(
            self.sample_compressed_ai_with_food_bias,
            self.sample_evidence,
            ai_query,
            "consumer"
        )

        # Check for banned food-related terms in the full report
        banned_terms = [
            "ultra-processed foods",
            "dietary decisions",
            "nutritional",
            "health organization recommendations"
        ]

        for term in banned_terms:
            assert term not in report, f"Found banned term '{term}' in report"

        # Should contain appropriate AI/education terms
        assert "AI in education" in report or "artificial intelligence" in report.lower()
        assert "educational technology" in report or "education" in report


if __name__ == "__main__":
    # Run tests directly
    test_instance = TestReportAgentTopicAware()
    test_instance.setup_method()

    tests = [
        test_instance.test_ai_education_query_executive_summary,
        test_instance.test_ai_education_query_key_insights,
        test_instance.test_climate_change_query_context,
        test_instance.test_health_query_preserves_health_terminology,
        test_instance.test_generic_query_handling,
        test_instance.test_adapt_finding_to_topic_method,
        test_instance.test_executive_summary_bullet_structure,
        test_instance.test_different_audiences_get_appropriate_language,
        test_instance.test_key_insights_cluster_processing,
        test_instance.test_no_food_terms_in_ai_report
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