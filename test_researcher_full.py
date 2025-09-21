#!/usr/bin/env python3
"""
Full test script for Researcher Agent functionality
"""

import json
from main import ResearcherAgent

def test_quality_scoring():
    """Test different types of sources to validate quality scoring"""

    researcher = ResearcherAgent()

    test_queries = [
        {
            "subquery": "ultra-processed foods WHO guidelines",
            "rationale": "Test government/official sources (should get quality 5)",
            "operators": ["site:who.int"],
            "freshness": "recent",
            "k": 3
        },
        {
            "subquery": "ultra-processed foods systematic review",
            "rationale": "Test peer-reviewed sources (should get quality 4-5)",
            "operators": ["site:pubmed.ncbi.nlm.nih.gov"],
            "freshness": "recent",
            "k": 3
        },
        {
            "subquery": "ultra-processed foods news",
            "rationale": "Test media sources (should get quality 2-4)",
            "operators": [],
            "freshness": "recent",
            "k": 3
        }
    ]

    for i, test_query in enumerate(test_queries):
        print(f"\n=== TEST {i+1}: {test_query['rationale']} ===")
        print(f"Query: {test_query['subquery']}")

        result = researcher.research_subquery(test_query)

        # Print summary stats
        findings = result.get("findings", [])
        print(f"Found {len(findings)} results")

        if findings:
            quality_scores = [f.get("quality", 0) for f in findings]
            avg_quality = sum(quality_scores) / len(quality_scores)
            print(f"Quality scores: {quality_scores}")
            print(f"Average quality: {avg_quality:.1f}")

            # Show first result details
            first_result = findings[0]
            print(f"Sample result:")
            print(f"  URL: {first_result.get('url', 'N/A')}")
            print(f"  Publisher: {first_result.get('publisher', 'N/A')}")
            print(f"  Quality: {first_result.get('quality', 'N/A')}")
            print(f"  Notes: {first_result.get('notes', 'N/A')}")
            print(f"  Date: {first_result.get('date', 'N/A')}")
            if first_result.get('snippets'):
                print(f"  First snippet: {first_result['snippets'][0][:100]}...")

        print(f"Gaps identified: {result.get('gaps', [])}")

def test_evidence_extraction():
    """Test evidence extraction capabilities"""

    researcher = ResearcherAgent()

    test_query = {
        "subquery": "ultra-processed foods health effects meta-analysis 2024",
        "rationale": "Test comprehensive evidence extraction",
        "operators": [],
        "freshness": "recent",
        "k": 5
    }

    print("\n=== COMPREHENSIVE EVIDENCE EXTRACTION TEST ===")
    result = researcher.research_subquery(test_query)

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print("Testing Researcher Agent Quality Scoring...")
    test_quality_scoring()

    print("\n" + "="*60)
    print("Testing Evidence Extraction...")
    test_evidence_extraction()