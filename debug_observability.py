#!/usr/bin/env python3
"""
Debug script for Observability Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import ObservabilityAgent
from datetime import datetime

def debug_observability():
    """Debug observability agent output"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    complete_logs = f"""2025-09-21 19:00:01 Deep Research Agent initialized
2025-09-21 19:00:01 User Query: Compare 2024-2025 evidence on ultra-processed foods and give recommendations.

2025-09-21 19:00:02 === CLARIFIED RESEARCH SPECIFICATION ===
2025-09-21 19:00:02 Objective: Compare recent evidence and provide evidence-based analysis
2025-09-21 19:00:02 Time Window: 2024-01 to 2025-09
2025-09-21 19:00:02 Success Criteria: >=10 unique sources
2025-09-21 19:00:02 clarify phase completed successfully
2025-09-21 19:00:02 Files saved to: data/intermediate/clarified_query_{timestamp}.json

2025-09-21 19:00:05 === RESEARCH BRIEF ===
2025-09-21 19:00:05 Generated comprehensive research brief with 6 sub-questions
2025-09-21 19:00:05 Research brief includes inclusion criteria and quality standards
2025-09-21 19:00:05 Files saved to: data/intermediate/research_brief_{timestamp}.md

2025-09-21 19:00:08 === SEARCH PLAN ===
2025-09-21 19:00:08 Created diversified search plan with 6 targeted subqueries
2025-09-21 19:00:08 Coverage target: 15 unique sources across multiple domains
2025-09-21 19:00:08 Files saved to: data/intermediate/search_plan_{timestamp}.json

2025-09-21 19:00:15 === TESTING RESEARCHER AGENT ===
2025-09-21 19:00:15 Researching subquery 1: ultra-processed foods health benefits
2025-09-21 19:00:18 Found 6 evidence items from first search
2025-09-21 19:00:18 Researching subquery 2: ultra-processed foods health risks
2025-09-21 19:00:21 Found 8 evidence items from second search
2025-09-21 19:00:21 research_subquery completed successfully
2025-09-21 19:00:21 Files saved to: data/evidence/evidence_collection_{timestamp}.json

2025-09-21 19:00:25 === COMPRESS + CONFLICT ANALYSIS ===
2025-09-21 19:00:25 Synthesized evidence into 3 key findings
2025-09-21 19:00:25 Identified 2 conflicts between different studies
2025-09-21 19:00:25 compress_and_align completed successfully
2025-09-21 19:00:25 Files saved to: data/intermediate/compression_{timestamp}.json

2025-09-21 19:00:30 === FINAL RESEARCH REPORT ===
2025-09-21 19:00:30 Generated audience-appropriate report with inline citations
2025-09-21 19:00:30 Report includes executive summary and recommendations
2025-09-21 19:00:30 generate_report completed successfully
2025-09-21 19:00:30 Files saved to: data/reports/research_report_{timestamp}.md

2025-09-21 19:00:35 === REPORT EVALUATION ===
2025-09-21 19:00:35 Overall Score: 4.2/5.0
2025-09-21 19:00:35 Coverage: 5/5, Faithfulness: 5/5, Balance: 5/5, Recency: 0/5
2025-09-21 19:00:35 evaluate_report completed successfully
2025-09-21 19:00:35 Files saved to: data/evaluations/evaluation_{timestamp}.json"""

    obs_agent = ObservabilityAgent()
    audit_trail = obs_agent.create_audit_trail(complete_logs)

    print("FULL AUDIT TRAIL:")
    print("=" * 80)
    print(audit_trail)
    print("=" * 80)

    # Check what we're looking for
    print(f"\nLooking for 'Total Steps: 8' in audit trail...")
    print(f"Found: {'Total Steps: 8' in audit_trail}")

    print(f"\nLooking for 'Total Steps:' in audit trail...")
    if "Total Steps:" in audit_trail:
        import re
        match = re.search(r"Total Steps: (\d+)", audit_trail)
        if match:
            print(f"Found: Total Steps: {match.group(1)}")
    else:
        print("Not found")

if __name__ == "__main__":
    debug_observability()