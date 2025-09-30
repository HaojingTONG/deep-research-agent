"""
Deep Research Agent - Pipeline Runner

Main execution pipeline for the 10-phase research process.
Orchestrates the complete workflow from query clarification to final report generation.
"""

import sys
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import all agent classes
from agents import (
    ClarifyAgent,
    ResearchBriefAgent,
    SupervisorPlannerAgent,
    ResearcherAgent,
    CompressConflictAgent,
    ReportAgent,
    EvaluatorAgent,
    RecoveryReplanAgent,
    ModelRouterAgent,
    ObservabilityAgent
)

# Import utilities
from utils import (
    DataManager, get_telemetry_collector, record_phase, record_recovery, record_skip,
    visualize_pipeline
)


def run_research_pipeline(user_query: str, test_mode: Optional[str] = None,
                         enable_viz: bool = False) -> Dict[str, Any]:
    """
    Execute the complete 10-phase Deep Research Agent pipeline.

    Orchestrates the full research workflow from initial query clarification
    through final report generation and quality evaluation.

    Args:
        user_query: The user's research query to process
        test_mode: Optional test mode for specific phases
                  (routing, observability, researcher, compress, report, recovery)
        enable_viz: Enable terminal visualization

    Returns:
        Dict containing execution results and file paths for generated outputs
    """
    # Initialize telemetry and visualization
    collector = get_telemetry_collector()
    collector.clear()  # Clear any previous runs
    collector.set_pipeline_start()

    viz = None
    if enable_viz:
        print("🔬 Starting Deep Research Agent with visualization...")
        viz = visualize_pipeline(collector)
    else:
        print("Deep Research Agent initialized")
        print(f"User Query: {user_query}\n")

    # Initialize data manager for new directory structure
    data_manager = DataManager()
    run_id = data_manager.run_id

    # Initialize logs for observability
    logs = []
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "phase": "clarify",
        "action": "start",
        "data": {"query": user_query}
    })

    results = {
        "run_id": run_id,
        "user_query": user_query,
        "test_mode": test_mode,
        "files_generated": {},
        "execution_status": "started"
    }

    try:
        # Phase 1: Clarify
        with record_phase("Clarify Agent", notes="Processing and clarifying user query"):
            clarify_agent = ClarifyAgent()
            clarified = clarify_agent.clarify_query(user_query)

            if not enable_viz:
                print("=== CLARIFIED RESEARCH SPECIFICATION ===")
                print(json.dumps(clarified, indent=2, ensure_ascii=False))
                print("\n")

            # Save clarified query
            clarified_filename = data_manager.save_clarify(clarified)
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "clarify",
                "action": "complete",
                "data": {"file": clarified_filename}
            })
            results["files_generated"]["clarify"] = clarified_filename

        # Phase 2: Research Brief
        with record_phase("Research Brief Agent", notes="Creating comprehensive research brief"):
            brief_agent = ResearchBriefAgent()
            brief_md = brief_agent.create_brief(clarified)

            if not enable_viz:
                print("=== RESEARCH BRIEF ===")
                print(brief_md)
                print("\n")

            # Save research brief
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "brief",
                "action": "start",
                "data": {}
            })
            brief_filename = data_manager.save_brief(brief_md)
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "brief",
                "action": "complete",
                "data": {"file": brief_filename}
            })
            results["files_generated"]["brief"] = brief_filename

        # Phase 3: Supervisor/Planner
        with record_phase("Supervisor Planner Agent", notes="Creating targeted search plan"):
            planner_agent = SupervisorPlannerAgent()
            search_plan = planner_agent.create_plan(brief_md)

            if not enable_viz:
                print("=== SEARCH PLAN ===")
                print(json.dumps(search_plan, indent=2, ensure_ascii=False))

            # Save search plan
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "plan",
                "action": "start",
                "data": {}
            })
            plan_filename = data_manager.save_plan(search_plan)
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "plan",
                "action": "complete",
                "data": {"file": plan_filename}
            })
            results["files_generated"]["plan"] = plan_filename

        # Phase 9: Model Router (test routing decisions)
        if test_mode == "routing":
            with record_phase("Model Router Agent", notes="Testing model routing decisions"):
                if not enable_viz:
                    print("\n=== TESTING MODEL ROUTER AGENT ===")
                router_agent = ModelRouterAgent()

                # Test routing for the current query
                routing_result = router_agent.route_models(user_query)

                if not enable_viz:
                    print("=== MODEL ROUTING DECISIONS ===")
                    print(json.dumps(routing_result, indent=2, ensure_ascii=False))

                # Save routing decision to logs
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "phase": "routing",
                    "action": "complete",
                    "data": routing_result
                })

                if not enable_viz:
                    print(f"\n=== ROUTING DECISION LOGGED ===")
                    print(f"Routing decision added to run logs")
                results["routing_result"] = routing_result

        # Phase 10: Observability (test log summarization)
        if test_mode == "observability":
            with record_phase("Observability Agent", notes="Testing log summarization and audit trail generation"):
                if not enable_viz:
                    print("\n=== TESTING OBSERVABILITY AGENT ===")

                # Create sample log data from current session
                sample_logs = f"""Deep Research Agent initialized
User Query: {user_query}

=== CLARIFIED RESEARCH SPECIFICATION ===
Objective: Compare recent evidence and provide analysis
Time Window: 2024-01 to 2025-09
Success Criteria: >=10 unique sources

=== RESEARCH BRIEF ===
Generated comprehensive research brief with sub-questions
Files saved to: data/intermediate/research_brief_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md

=== SEARCH PLAN ===
Created diversified search plan with 6 targeted subqueries
Files saved to: data/intermediate/search_plan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json

=== TESTING RESEARCHER AGENT ===
Found 8 evidence items from search query
Research phase completed successfully

=== COMPRESS + CONFLICT ANALYSIS ===
Synthesized evidence into key findings
Identified 2 conflicts between studies
Files saved to: data/intermediate/compression_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json

=== FINAL RESEARCH REPORT ===
Generated audience-appropriate report with citations
Files saved to: data/reports/research_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md

=== REPORT EVALUATION ===
Overall Score: 4.2/5.0
Coverage: 5/5, Faithfulness: 5/5, Balance: 5/5
Files saved to: data/evaluations/evaluation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json

=== MODEL ROUTING DECISIONS ===
Selected model profiles with 2 premium allocations
Total Cost: 11.0
Files saved to: data/intermediate/routing_decision_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"""

                # Test observability agent
                obs_agent = ObservabilityAgent()
                audit_trail = obs_agent.create_audit_trail(sample_logs)

                if not enable_viz:
                    print("=== AUDIT TRAIL GENERATED ===")
                    print(audit_trail[:1000] + "..." if len(audit_trail) > 1000 else audit_trail)

                # Save audit trail
                import os
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audit_filename = f"data/logs/audit_trail_{timestamp}.md"
                os.makedirs("data/logs", exist_ok=True)
                with open(audit_filename, 'w', encoding='utf-8') as f:
                    f.write(audit_trail)

                if not enable_viz:
                    print(f"\n=== AUDIT TRAIL SAVED ===")
                    print(f"Audit trail saved to: {audit_filename}")
                results["files_generated"]["audit_trail"] = audit_filename

        # Phase 4: Evidence Collection - Run by default or when testing
        if test_mode is None or test_mode == "researcher":
            with record_phase("Researcher Agent", notes="Collecting evidence from multiple sources"):
                if not enable_viz:
                    print("\n=== PHASE 4: EVIDENCE COLLECTION ===")
                researcher_agent = ResearcherAgent()

                # Collect evidence from all subqueries (or limit for testing)
                all_evidence = []
                flattened_evidence = []

                if test_mode == "researcher":
                    # Test mode: only first subquery
                    max_queries = 1
                    if not enable_viz:
                        print("Testing mode: processing first subquery only")
                else:
                    # Full mode: process all subqueries
                    max_queries = len(search_plan["plan"])
                    if not enable_viz:
                        print(f"Full mode: processing {max_queries} subqueries")

                for i in range(min(max_queries, len(search_plan["plan"]))):
                    subquery = search_plan["plan"][i]
                    subquery_text = subquery.get('subquery', f'Subquery {i+1}')

                    with record_phase(f"Research Subquery {i+1}",
                                    notes=f"Searching: {subquery_text[:50]}...",
                                    parent_phase="Researcher Agent",
                                    subquery_index=i+1,
                                    total_subqueries=max_queries):
                        if not enable_viz:
                            print(f"\nSearching subquery {i+1}/{max_queries}: {subquery_text}")

                        evidence_result = researcher_agent.research_subquery(subquery)
                        all_evidence.append(evidence_result)

                        # Flatten evidence for easier processing
                        for evidence in evidence_result.get("findings", []):
                            flattened_evidence.append(evidence)

                        if not enable_viz:
                            print(f"Found {len(evidence_result.get('findings', []))} pieces of evidence")

                if not enable_viz:
                    print(f"\n=== TOTAL EVIDENCE COLLECTED: {len(flattened_evidence)} items ===")

                # Save evidence
                if flattened_evidence:
                    evidence_filename = data_manager.save_evidence(flattened_evidence)
                    logs.append({
                        "timestamp": datetime.now().isoformat(),
                        "phase": "evidence",
                        "action": "complete",
                        "data": {"file": evidence_filename, "count": len(flattened_evidence)}
                    })
                    results["files_generated"]["evidence"] = evidence_filename
                    results["evidence_count"] = len(flattened_evidence)

        # Phase 5: Compress + Conflict Analysis - Run by default or when testing
        if test_mode is None or test_mode == "compress":
            with record_phase("Compress Conflict Agent", notes="Synthesizing findings and detecting conflicts"):
                if not enable_viz:
                    print("\n=== PHASE 5: COMPRESS + CONFLICT ANALYSIS ===")
                compress_agent = CompressConflictAgent()

                # Use evidence collected in Phase 4 (reuse variables from scope)
                if 'all_evidence' in locals() and all_evidence:
                    if not enable_viz:
                        print(f"Using {len(all_evidence)} evidence collections from Phase 4")
                    compression_result = compress_agent.compress_and_align(all_evidence)
                else:
                    if not enable_viz:
                        print("No evidence available - running limited compression test")
                    # Fallback for test-only mode
                    researcher_agent = ResearcherAgent()
                    test_evidence = []
                    max_queries = min(3, len(search_plan["plan"]))
                    for i in range(max_queries):
                        subquery = search_plan["plan"][i]
                        evidence_result = researcher_agent.research_subquery(subquery)
                        test_evidence.append(evidence_result)
                    compression_result = compress_agent.compress_and_align(test_evidence)
                    # Update flattened_evidence for later use
                    flattened_evidence = []
                    for evidence_result in test_evidence:
                        for evidence in evidence_result.get("findings", []):
                            flattened_evidence.append(evidence)

                if not enable_viz:
                    print("\n=== COMPRESSION & CONFLICT ANALYSIS ===")
                    print(json.dumps(compression_result, indent=2, ensure_ascii=False))

                # Save compression result
                compression_filename = data_manager.save_compressed(compression_result)
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "phase": "compress",
                    "action": "complete",
                    "data": {"file": compression_filename}
                })
                results["files_generated"]["compress"] = compression_filename

        # Phase 6: Report Generation - Run by default or when testing
        if test_mode is None or test_mode == "report":
            with record_phase("Report Agent", notes="Generating structured research report", model_used="gpt-4"):
                if not enable_viz:
                    print("\n=== PHASE 6: REPORT GENERATION ===")
                report_agent = ReportAgent()

                # Use data from previous phases
                if 'compression_result' in locals() and 'flattened_evidence' in locals():
                    if not enable_viz:
                        print(f"Using compression result and {len(flattened_evidence)} evidence items from previous phases")
                else:
                    if not enable_viz:
                        print("No previous data available - running test mode with fresh data collection")
                    # Fallback for test-only mode - collect fresh data
                    researcher_agent = ResearcherAgent()
                    compress_agent = CompressConflictAgent()
                    all_evidence = []
                    flattened_evidence = []
                    max_queries = min(3, len(search_plan["plan"]))

                    for i in range(max_queries):
                        subquery = search_plan["plan"][i]
                        if not enable_viz:
                            print(f"Researching subquery {i+1}: {subquery['subquery']}")
                        evidence_result = researcher_agent.research_subquery(subquery)
                        all_evidence.append(evidence_result)
                        for evidence in evidence_result.get("findings", []):
                            flattened_evidence.append(evidence)

                    compression_result = compress_agent.compress_and_align(all_evidence)

                # Generate report
                target_audience = "consumer"  # Can be changed to "executive" or "researcher"
                final_report = report_agent.generate_report(
                    compression_result,
                    flattened_evidence,
                    user_query,
                    target_audience
                )

                if not enable_viz:
                    print("\n=== FINAL RESEARCH REPORT ===")
                    print(final_report)

                # Save report
                report_filename = data_manager.save_report(final_report)
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "phase": "report",
                    "action": "complete",
                    "data": {"file": report_filename, "audience": target_audience}
                })
                results["files_generated"]["report"] = report_filename

                if not enable_viz:
                    print(f"\n=== REPORT SAVED ===")
            if not enable_viz:
                print(f"Report saved to: {report_filename}")

            # Phase 7: Evaluation/QA
            with record_phase("Evaluator Agent", notes="Assessing report quality across 6 dimensions"):
                evaluator_agent = EvaluatorAgent()
                evaluation_result = evaluator_agent.evaluate_report(final_report, flattened_evidence)

                if not enable_viz:
                    print(f"\n=== REPORT EVALUATION ===")
                    print(json.dumps(evaluation_result, indent=2, ensure_ascii=False))

                # Save evaluation
                eval_filename = data_manager.save_evaluation(evaluation_result)
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "phase": "evaluation",
                    "action": "complete",
                    "data": {"file": eval_filename, "overall_score": evaluation_result.get("overall_score", 0)}
                })
                results["files_generated"]["evaluation"] = eval_filename
                results["evaluation_score"] = evaluation_result.get("overall_score", 0)

                if not enable_viz:
                    print(f"\n=== EVALUATION SAVED ===")
                    print(f"Evaluation saved to: {eval_filename}")

        # Phase 8: Recovery/Replan (when testing recovery)
        if test_mode == "recovery":
            results.update(_run_recovery_test(
                user_query, search_plan, data_manager, logs
            ))

        # Save logs at the end of execution
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "phase": "complete",
            "action": "end",
            "data": {"run_id": run_id, "status": "success"}
        })

        # Save all logs
        logs_filename = data_manager.save_logs(logs)
        results["files_generated"]["logs"] = logs_filename
        results["execution_status"] = "completed"

        # Mark pipeline completion
        collector.set_pipeline_end("completed")

        if not enable_viz:
            print(f"\n=== RUN COMPLETE ===")
            print(f"Run ID: {run_id}")
            print(f"Logs saved to: {logs_filename}")
            if "report" in results["files_generated"]:
                print(f"Report available at: data/runs/{run_id}/report.md")
                print(f"Also exported to: data/out/research_report_{run_id}.md")

    except Exception as e:
        # Mark pipeline failure
        collector.set_pipeline_end("failed")

        if not enable_viz:
            print(f"\n=== EXECUTION ERROR ===")
            print(f"Error: {str(e)}")
        results["execution_status"] = "failed"
        results["error"] = str(e)

        # Log error
        data_manager.log_error({
            "error": str(e),
            "phase": "pipeline_execution",
            "query": user_query
        })

    finally:
        # Stop visualization if enabled
        if viz:
            # Give visualization time to show final state
            time.sleep(2)
            viz.stop()

    return results


def _run_recovery_test(user_query: str, search_plan: Dict, data_manager: DataManager, logs: List) -> Dict:
    """Run the complete recovery test pipeline."""
    print("\n=== TESTING COMPLETE RESEARCH PIPELINE WITH RECOVERY ===")

    # Initialize agents
    researcher_agent = ResearcherAgent()
    compress_agent = CompressConflictAgent()
    report_agent = ReportAgent()
    evaluator_agent = EvaluatorAgent()
    recovery_agent = RecoveryReplanAgent()

    recovery_results = {}

    # Collect evidence from multiple subqueries
    all_evidence = []
    flattened_evidence = []
    max_queries = min(3, len(search_plan["plan"]))  # Test with first 3 subqueries

    for i in range(max_queries):
        subquery = search_plan["plan"][i]
        print(f"Researching subquery {i+1}: {subquery['subquery']}")

        evidence_result = researcher_agent.research_subquery(subquery)
        all_evidence.append(evidence_result)

        # Flatten evidence for report
        for evidence in evidence_result.get("findings", []):
            flattened_evidence.append(evidence)

    # Compress and analyze
    compression_result = compress_agent.compress_and_align(all_evidence)

    # Generate report
    target_audience = "consumer"
    final_report = report_agent.generate_report(
        compression_result,
        flattened_evidence,
        user_query,
        target_audience
    )

    print("\n=== INITIAL RESEARCH REPORT ===")
    print(final_report)

    # Save initial report
    import os
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/evaluations", exist_ok=True)
    os.makedirs("data/evidence", exist_ok=True)
    os.makedirs("data/intermediate", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"data/reports/research_report_{timestamp}.md"

    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(final_report)

    print(f"\n=== INITIAL REPORT SAVED ===")
    print(f"Report saved to: {report_filename}")
    recovery_results["initial_report"] = report_filename

    # Phase 7: Evaluation/QA
    evaluation_result = evaluator_agent.evaluate_report(final_report, flattened_evidence)

    print(f"\n=== INITIAL REPORT EVALUATION ===")
    print(json.dumps(evaluation_result, indent=2, ensure_ascii=False))

    # Save evaluation
    eval_filename = f"data/evaluations/evaluation_{timestamp}.json"
    with open(eval_filename, 'w', encoding='utf-8') as f:
        json.dump(evaluation_result, f, indent=2, ensure_ascii=False)

    print(f"\n=== INITIAL EVALUATION SAVED ===")
    print(f"Evaluation saved to: {eval_filename}")
    recovery_results["initial_evaluation"] = eval_filename

    # Create replan based on gaps and evaluation
    print("\n=== TESTING RECOVERY/REPLAN AGENT ===")
    replan_spec = recovery_agent.create_replan(compression_result, evaluation_result, user_query)

    print("=== RECOVERY REPLAN SPECIFICATION ===")
    print(json.dumps(replan_spec, indent=2, ensure_ascii=False))

    # Save replan specification
    replan_filename = f"data/intermediate/replan_spec_{timestamp}.json"
    with open(replan_filename, 'w', encoding='utf-8') as f:
        json.dump(replan_spec, f, indent=2, ensure_ascii=False)
    recovery_results["replan_spec"] = replan_filename

    # Execute recovery if needed
    if replan_spec.get("replan"):
        additional_evidence = recovery_agent.execute_replan(replan_spec, researcher_agent)

        # Save recovery evidence
        recovery_evidence_filename = f"data/evidence/recovery_evidence_{timestamp}.json"
        with open(recovery_evidence_filename, 'w', encoding='utf-8') as f:
            json.dump(additional_evidence, f, indent=2, ensure_ascii=False)

        # Merge additional evidence with original
        all_flattened_evidence = flattened_evidence.copy()
        for recovery_result in additional_evidence:
            for evidence in recovery_result.get("findings", []):
                all_flattened_evidence.append(evidence)

        # Re-compress with additional evidence
        print("\n=== RE-COMPRESSING WITH ADDITIONAL EVIDENCE ===")
        all_evidence_for_compression = all_evidence + additional_evidence
        updated_compression = compress_agent.compress_and_align(all_evidence_for_compression)

        # Generate updated report
        print("\n=== GENERATING UPDATED REPORT ===")
        updated_report = report_agent.generate_report(
            updated_compression,
            all_flattened_evidence,
            user_query,
            target_audience
        )

        # Re-evaluate updated report
        print("\n=== RE-EVALUATING UPDATED REPORT ===")
        updated_evaluation = evaluator_agent.evaluate_report(updated_report, all_flattened_evidence)

        # Compare improvements
        improvement_analysis = recovery_agent.evaluate_improvement(evaluation_result, updated_evaluation)

        print("\n=== IMPROVEMENT ANALYSIS ===")
        print(json.dumps(improvement_analysis, indent=2, ensure_ascii=False))

        # Save updated artifacts
        updated_report_filename = f"data/reports/updated_report_{timestamp}.md"
        updated_eval_filename = f"data/evaluations/updated_evaluation_{timestamp}.json"
        improvement_filename = f"data/evaluations/improvement_analysis_{timestamp}.json"

        with open(updated_report_filename, 'w', encoding='utf-8') as f:
            f.write(updated_report)

        with open(updated_eval_filename, 'w', encoding='utf-8') as f:
            json.dump(updated_evaluation, f, indent=2, ensure_ascii=False)

        with open(improvement_filename, 'w', encoding='utf-8') as f:
            json.dump(improvement_analysis, f, indent=2, ensure_ascii=False)

        print(f"\n=== RECOVERY RESULTS SAVED ===")
        print(f"Updated report: {updated_report_filename}")
        print(f"Updated evaluation: {updated_eval_filename}")
        print(f"Improvement analysis: {improvement_filename}")

        recovery_results.update({
            "recovery_evidence": recovery_evidence_filename,
            "updated_report": updated_report_filename,
            "updated_evaluation": updated_eval_filename,
            "improvement_analysis": improvement_filename
        })
    else:
        print("\n=== NO RECOVERY NEEDED ===")
        print("Report quality already meets threshold - no additional searches required")

    return recovery_results


def main():
    """
    CLI entry point for the Deep Research Agent pipeline.

    Handles command line arguments and invokes the appropriate pipeline execution.
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py '<your research query>' [--test-mode]")
        print("Example: python main.py 'Compare 2024–2025 evidence on ultra-processed foods and give recommendations.'")
        print("\nTest modes:")
        print("  --test-routing      Test model routing decisions")
        print("  --test-observability Test log summarization")
        print("  --test-researcher   Test evidence collection (first subquery only)")
        print("  --test-compress     Test evidence compression and conflict analysis")
        print("  --test-report       Test report generation and evaluation")
        print("  --test-recovery     Test complete pipeline with recovery")
        return

    user_query = sys.argv[1]

    # Parse test mode
    test_mode = None
    if len(sys.argv) > 2:
        test_arg = sys.argv[2]
        if test_arg.startswith("--test-"):
            test_mode = test_arg[7:]  # Remove "--test-" prefix

    # Run the pipeline
    results = run_research_pipeline(user_query, test_mode)

    return results


if __name__ == "__main__":
    main()