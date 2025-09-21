#!/usr/bin/env python3
"""
Test script for Researcher Agent functionality
"""

import json
from main import ResearcherAgent

def test_simple_search():
    """Test with a simple query without complex operators"""

    researcher = ResearcherAgent()

    # Simple test query
    test_subquery = {
        "subquery": "ultra-processed foods health 2024",
        "rationale": "Test basic search functionality",
        "operators": [],  # No operators for initial test
        "freshness": "recent",
        "k": 3
    }

    print("Testing Researcher Agent with simplified query...")
    print(f"Query: {test_subquery['subquery']}")

    result = researcher.research_subquery(test_subquery)

    print("\n=== RESULTS ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_simple_search()