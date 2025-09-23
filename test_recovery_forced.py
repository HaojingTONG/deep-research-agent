#!/usr/bin/env python3
"""
Test script to force Recovery/Replan Agent activation by creating low-quality scenario
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import RecoveryReplanAgent, ResearcherAgent, CompressConflictAgent, ReportAgent, EvaluatorAgent

def test_forced_recovery():
    """Test Recovery Agent with artificially low-quality scores to trigger replan"""

    # Create mock low-quality evaluation result
    low_quality_evaluation = {
        "scores": {
            "coverage": 2,      # Low coverage
            "faithfulness": 3,  # Below threshold
            "balance": 1,       # Very low balance
            "recency": 0,       # No recent sources
            "actionability": 4, # Good
            "readability": 4    # Good
        },
        "priority_fixes": [
            "Add more 2024-2025 sources and highlight recent developments in timeline",
            "Include more diverse perspectives and systematic reviews for better coverage",
            "Address bias toward negative findings - seek evidence of potential benefits"
        ],
        "overall_score": 2.3,   # Below 4.0 threshold
        "evaluation_summary": "Poor report quality requiring significant improvement"
    }

    # Create mock compression result with gaps
    compression_result = {
        "key_findings": [
            "Ultra-processed foods are associated with health risks [0,1]",
            "Limited evidence exists for health benefits [2]",
            "Research gaps exist in long-term studies [3]"
        ],
        "conflicts": [
            {
                "claim": "Ultra-processed foods may have some health benefits",
                "positions": [
                    {"stance": "limited benefits", "evidence_refs": [2]},
                    {"stance": "no benefits", "evidence_refs": [0,1]}
                ],
                "explanation": "Different study methodologies and populations"
            }
        ],
        "gaps": [
            "Need more 2024-2025 research on ultra-processed foods",
            "Need comprehensive systematic review of recent evidence",
            "Need research on ultra-processed food effects across different age groups",
            "Need long-term longitudinal studies on health outcomes"
        ],
        "coverage_stats": {
            "domains_covered": ["health", "nutrition"],
            "source_types": ["academic", "government"],
            "quality_distribution": {"high": 8, "medium": 4, "low": 3}
        }
    }

    # Test Recovery/Replan Agent
    recovery_agent = RecoveryReplanAgent()

    print("=== TESTING FORCED RECOVERY/REPLAN AGENT ===\n")

    # Create replan
    replan_spec = recovery_agent.create_replan(
        compression_result,
        low_quality_evaluation,
        "Compare 2024–2025 evidence on ultra-processed foods and give recommendations."
    )

    print("=== RECOVERY REPLAN SPECIFICATION ===")
    print(json.dumps(replan_spec, indent=2, ensure_ascii=False))
    print(f"\nReplan contains {len(replan_spec.get('replan', []))} targeted queries")

    # Test replan execution (mock)
    print("\n=== TESTING REPLAN EXECUTION (MOCK) ===")

    if replan_spec.get("replan"):
        researcher_agent = ResearcherAgent()

        print(f"Would execute {len(replan_spec['replan'])} recovery queries:")
        for i, query in enumerate(replan_spec["replan"]):
            print(f"\n{i+1}. Query: {query['subquery']}")
            print(f"   Rationale: {query['rationale']}")
            print(f"   Operators: {', '.join(query.get('operators', []))}")
            print(f"   Expected results: {query.get('k', 6)} items")

    # Test improvement evaluation (mock)
    print("\n=== TESTING IMPROVEMENT EVALUATION (MOCK) ===")

    # Simulate improved evaluation after recovery
    improved_evaluation = {
        "scores": {
            "coverage": 4,      # Improved
            "faithfulness": 4,  # Improved
            "balance": 3,       # Improved
            "recency": 3,       # Much improved
            "actionability": 4, # Same
            "readability": 4    # Same
        },
        "priority_fixes": [
            "Minor improvements to balance could further enhance quality"
        ],
        "overall_score": 3.7,   # Improved but still room for growth
        "evaluation_summary": "Moderate report quality with good improvement"
    }

    improvement_analysis = recovery_agent.evaluate_improvement(
        low_quality_evaluation,
        improved_evaluation
    )

    print("=== IMPROVEMENT ANALYSIS ===")
    print(json.dumps(improvement_analysis, indent=2, ensure_ascii=False))

    print(f"\nImprovement Success: {improvement_analysis['success']}")
    print(f"Summary: {improvement_analysis['summary']}")

    # Show detailed improvements
    print("\n=== DETAILED METRIC IMPROVEMENTS ===")
    for metric, improvement in improvement_analysis["metric_improvements"].items():
        print(f"{metric.capitalize()}: {improvement['before']} → {improvement['after']} (+{improvement['improvement']})")

if __name__ == "__main__":
    test_forced_recovery()