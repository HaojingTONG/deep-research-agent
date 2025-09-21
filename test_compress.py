#!/usr/bin/env python3
"""
Test script for Compress + Conflict Agent functionality
"""

import json
from main import CompressConflictAgent

def test_compress_conflict():
    """Test Compress + Conflict Agent with mock evidence data"""

    # Mock evidence data from multiple subqueries
    mock_evidence = [
        # Subquery 1: Health Benefits
        {
            "subquery": "ultra-processed foods health benefits",
            "findings": [
                {
                    "url": "https://example-nutrition.com/benefits",
                    "title": "Potential Nutritional Advantages of Some Ultra-Processed Foods",
                    "publisher": "Nutrition Journal",
                    "date": "2024-03-15",
                    "snippets": ["Some ultra-processed foods provide essential nutrients and convenience"],
                    "quality": 4,
                    "notes": "Reputable nutrition source with research data"
                },
                {
                    "url": "https://food-industry.com/advantages",
                    "title": "Food Industry Perspective on Processing Benefits",
                    "publisher": "Food Industry",
                    "date": "2024-01-20",
                    "snippets": ["Processing can enhance food safety and shelf life"],
                    "quality": 3,
                    "notes": "Industry perspective with some data"
                }
            ]
        },
        # Subquery 2: Health Risks
        {
            "subquery": "ultra-processed foods health risks systematic review",
            "findings": [
                {
                    "url": "https://pubmed.ncbi.nlm.nih.gov/12345",
                    "title": "Ultra-processed Food Consumption and Cardiovascular Disease Risk: Systematic Review",
                    "publisher": "PubMed",
                    "date": "2024-06-10",
                    "snippets": ["Systematic review shows increased cardiovascular disease risk with ultra-processed food consumption"],
                    "quality": 5,
                    "notes": "High-quality PubMed systematic review"
                },
                {
                    "url": "https://bmj.com/upf-cancer-study",
                    "title": "Association Between Ultra-processed Food and Cancer Risk",
                    "publisher": "BMJ",
                    "date": "2024-02-28",
                    "snippets": ["Observational study links ultra-processed foods to increased cancer mortality"],
                    "quality": 5,
                    "notes": "High-quality BMJ research with methodology"
                }
            ]
        },
        # Subquery 3: WHO Recommendations
        {
            "subquery": "WHO ultra-processed foods recommendations",
            "findings": [
                {
                    "url": "https://who.int/nutrition/upf-guidelines",
                    "title": "WHO Guidelines on Ultra-processed Food Consumption",
                    "publisher": "World Health Organization",
                    "date": "2024-04-05",
                    "snippets": ["WHO recommends limiting ultra-processed food consumption as part of healthy dietary recommendations"],
                    "quality": 5,
                    "notes": "High-quality WHO official guidelines"
                },
                {
                    "url": "https://fda.gov/dietary-guidelines",
                    "title": "FDA Dietary Recommendations for Processed Foods",
                    "publisher": "FDA",
                    "date": "2024-01-15",
                    "snippets": ["FDA advises reading nutrition labels and choosing minimally processed options"],
                    "quality": 5,
                    "notes": "High-quality FDA official guidance"
                }
            ]
        }
    ]

    # Test the Compress + Conflict Agent
    compress_agent = CompressConflictAgent()
    result = compress_agent.compress_and_align(mock_evidence)

    print("=== COMPRESS + CONFLICT AGENT TEST ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Validate results
    print("\n=== VALIDATION ===")
    print(f"Number of clusters: {len(result['clusters'])}")
    print(f"Number of key findings: {len(result['key_findings'])}")
    print(f"Number of conflicts identified: {len(result['conflicts'])}")
    print(f"Number of gaps identified: {len(result['gaps'])}")
    print(f"Coverage stats: {result['coverage_stats']}")

    # Check if conflicts were properly identified
    if result['conflicts']:
        print("\n=== CONFLICT ANALYSIS ===")
        for i, conflict in enumerate(result['conflicts']):
            print(f"Conflict {i+1}: {conflict['claim']}")
            print(f"  Support: {conflict['support']}")
            print(f"  Counter: {conflict['counter']}")
            print(f"  Reason: {conflict['reason']}")

if __name__ == "__main__":
    test_compress_conflict()