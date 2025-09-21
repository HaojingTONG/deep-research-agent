#!/usr/bin/env python3
"""
Test Recovery/Replan Agent with real data by temporarily lowering threshold
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import RecoveryReplanAgent, ResearcherAgent

def test_real_recovery():
    """Test Recovery Agent with real evaluation data from previous run"""

    # Load the most recent evaluation data
    eval_file = "data/out/evaluation_20250921_184925.json"

    if not os.path.exists(eval_file):
        print(f"Evaluation file not found: {eval_file}")
        print("Please run the main pipeline first with --test-recovery")
        return

    with open(eval_file, 'r') as f:
        evaluation_result = json.load(f)

    print("=== ORIGINAL EVALUATION ===")
    print(json.dumps(evaluation_result, indent=2, ensure_ascii=False))

    # Mock compression result with realistic gaps (since we don't have the real one)
    compression_result = {
        "key_findings": [
            "Potential health benefits of ultra-processed foods are limited and controversial [0,11]",
            "Multiple studies link ultra-processed foods to increased health risks [1,9,10]",
            "Food industry emphasizes processing innovations [3]"
        ],
        "conflicts": [
            {
                "claim": "Ultra-processed foods may have some health benefits",
                "positions": [
                    {"stance": "limited benefits", "evidence_refs": [0,11]},
                    {"stance": "primarily harmful", "evidence_refs": [1,9,10]}
                ],
                "explanation": "Different study methodologies and populations; benefits may be limited to specific contexts"
            },
            {
                "claim": "Systematic reviews provide strongest evidence",
                "positions": [
                    {"stance": "systematic reviews best", "evidence_refs": [1,9]},
                    {"stance": "observational studies sufficient", "evidence_refs": [0,3,11]}
                ],
                "explanation": "Different levels of evidence hierarchy; systematic reviews synthesize multiple studies while observational studies provide specific findings"
            }
        ],
        "gaps": [
            "Need more 2024-2025 research on ultra-processed foods",
            "Need comprehensive systematic review of 2024-2025 evidence",
            "Need research on ultra-processed food effects across different age groups",
            "Need long-term longitudinal studies on health outcomes"
        ],
        "coverage_stats": {
            "domains_covered": ["health", "nutrition", "policy"],
            "source_types": ["academic", "government", "organization"],
            "quality_distribution": {"high": 13, "medium": 2, "low": 0}
        }
    }

    # Temporarily modify evaluation to trigger recovery (simulate poor recency)
    modified_evaluation = evaluation_result.copy()
    modified_evaluation["scores"]["recency"] = 0  # This was already 0
    modified_evaluation["scores"]["coverage"] = 2  # Lower this to trigger recovery
    modified_evaluation["overall_score"] = 3.2  # Recalculate to be below 4.0
    modified_evaluation["evaluation_summary"] = "Report quality below threshold - needs improvement"
    modified_evaluation["priority_fixes"].append("Improve coverage with more systematic reviews and diverse sources")

    print("\n=== MODIFIED EVALUATION (FOR RECOVERY TEST) ===")
    print(json.dumps(modified_evaluation, indent=2, ensure_ascii=False))

    # Test Recovery Agent
    recovery_agent = RecoveryReplanAgent()
    researcher_agent = ResearcherAgent()

    print("\n=== CREATING RECOVERY REPLAN ===")
    replan_spec = recovery_agent.create_replan(
        compression_result,
        modified_evaluation,
        "Compare 2024–2025 evidence on ultra-processed foods and give recommendations."
    )

    print("=== RECOVERY REPLAN SPECIFICATION ===")
    print(json.dumps(replan_spec, indent=2, ensure_ascii=False))

    # Execute a limited recovery (just 1-2 queries for demonstration)
    if replan_spec.get("replan"):
        print(f"\n=== EXECUTING LIMITED RECOVERY ({min(2, len(replan_spec['replan']))} queries) ===")

        limited_replan = {
            "replan": replan_spec["replan"][:2],  # Only first 2 queries
            "expected_gain": replan_spec["expected_gain"],
            "trigger_reason": replan_spec["trigger_reason"]
        }

        try:
            additional_evidence = recovery_agent.execute_replan(limited_replan, researcher_agent)

            print(f"\n=== RECOVERY RESULTS ===")
            print(f"Executed {len(additional_evidence)} recovery queries")

            total_new_evidence = 0
            for i, result in enumerate(additional_evidence):
                findings = result.get("findings", [])
                total_new_evidence += len(findings)
                print(f"Query {i+1}: Found {len(findings)} additional evidence items")

                # Show sample of new evidence
                for j, evidence in enumerate(findings[:2]):  # Show first 2 items
                    print(f"  [{j}] {evidence.get('title', 'No title')[:100]}...")

            print(f"\nTotal new evidence collected: {total_new_evidence} items")

        except Exception as e:
            print(f"Error during recovery execution: {e}")
            print("This is expected in test environment without full search setup")

if __name__ == "__main__":
    test_real_recovery()