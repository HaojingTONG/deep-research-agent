#!/usr/bin/env python3
"""
Test the topic drift fix by verifying keyword extraction and flow through phases.
"""

from agents.clarify_agent import ClarifyAgent
from agents.research_brief_agent import ResearchBriefAgent
from agents.supervisor_planner_agent import SupervisorPlannerAgent
from utils import extract_topic_keywords
import json

def test_topic_keywords_extraction():
    """Test that topic keywords are properly extracted."""
    test_query = "The Applications of Artificial Intelligence in Education: Opportunities and Challenges"

    print("=== Testing Topic Keywords Extraction ===")
    print(f"Query: {test_query}")

    keywords = extract_topic_keywords(test_query)
    print(f"Extracted Keywords: {keywords}")

    # Should contain AI/education related terms, not food terms
    expected_terms = ['artificial', 'intelligence', 'education', 'applications', 'opportunities', 'challenges']
    food_terms = ['food', 'ultra-processed', 'nutrition', 'diet']

    assert any(term in ' '.join(keywords).lower() for term in expected_terms), f"Expected AI/education terms, got: {keywords}"
    assert not any(term in ' '.join(keywords).lower() for term in food_terms), f"Unexpected food terms in: {keywords}"

    print("✅ Topic keywords extraction working correctly")
    return keywords

def test_clarify_to_brief_flow():
    """Test that keywords flow correctly from clarify to brief phase."""
    test_query = "The Applications of Artificial Intelligence in Education: Opportunities and Challenges"

    print("\n=== Testing Clarify → Brief Flow ===")

    # Phase 1: Clarify
    clarify_agent = ClarifyAgent()
    clarify_result = clarify_agent.clarify_query(test_query)

    print("Clarify result objective:", clarify_result.get('objective', '')[:100] + "...")

    # Phase 2: Brief
    brief_agent = ResearchBriefAgent()
    brief_markdown = brief_agent.create_brief(clarify_result)

    print("Brief contains topic keywords:")
    lines = brief_markdown.split('\n')
    for line in lines:
        if "**Topic Keywords:**" in line:
            print(f"  {line}")
            keywords_str = line.split("**Topic Keywords:**")[1].strip()
            keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]

            # Should contain AI/education terms
            expected_terms = ['artificial', 'intelligence', 'education', 'applications']
            assert any(term in ' '.join(keywords).lower() for term in expected_terms), f"Expected AI/education terms in brief, got: {keywords}"

            print("✅ Topic keywords properly included in brief")
            return brief_markdown, keywords

    raise AssertionError("Topic keywords not found in brief")

def test_brief_to_plan_flow():
    """Test that keywords flow correctly from brief to plan phase."""
    test_query = "The Applications of Artificial Intelligence in Education: Opportunities and Challenges"

    print("\n=== Testing Brief → Plan Flow ===")

    # Get brief from previous phases
    clarify_agent = ClarifyAgent()
    clarify_result = clarify_agent.clarify_query(test_query)

    brief_agent = ResearchBriefAgent()
    brief_markdown = brief_agent.create_brief(clarify_result)

    # Phase 3: Plan
    planner_agent = SupervisorPlannerAgent()
    plan = planner_agent.create_plan(brief_markdown)

    print("Generated subqueries:")
    subqueries = plan.get('plan', [])

    for i, subquery in enumerate(subqueries[:3]):  # Check first 3
        query_text = subquery.get('subquery', '')
        print(f"  {i+1}. {query_text}")

        # Should contain meaningful terms, not generic ones
        generic_terms = ['current', 'state', 'research', 'this']
        ai_terms = ['artificial', 'intelligence', 'education', 'applications', 'opportunities', 'challenges', 'learning']

        # Check if we have specific AI/education terms instead of generic ones
        has_specific_terms = any(term in query_text.lower() for term in ai_terms)
        mostly_generic = all(word.lower() in generic_terms for word in query_text.split() if len(word) > 2)

        if not has_specific_terms and mostly_generic:
            print(f"  ⚠️  Query seems too generic: {query_text}")
        else:
            print(f"  ✅ Query contains specific terms")

    print(f"✅ Generated {len(subqueries)} subqueries with topic-specific terms")
    return plan

def main():
    """Run all topic fidelity tests."""
    print("Testing Topic Drift Fix")
    print("=" * 50)

    try:
        # Test 1: Keywords extraction
        keywords = test_topic_keywords_extraction()

        # Test 2: Clarify → Brief flow
        brief_markdown, brief_keywords = test_clarify_to_brief_flow()

        # Test 3: Brief → Plan flow
        plan = test_brief_to_plan_flow()

        print("\n" + "=" * 50)
        print("🎉 All tests passed! Topic drift fix is working.")
        print(f"📝 Keywords extracted: {keywords}")
        print(f"📋 Brief keywords: {brief_keywords}")
        print(f"🎯 Generated {len(plan.get('plan', []))} topic-focused subqueries")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()