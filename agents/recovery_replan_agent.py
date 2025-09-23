"""
Phase 8: Recovery/Replan Agent

Generates targeted fixes for quality issues identified in report evaluation.
Creates recovery search strategies to address specific gaps and improve scores.
"""

from typing import Dict, Any, List


class RecoveryReplanAgent:
    """
    Phase 8: Recovery/Replan Agent - Generate targeted fixes for quality issues.

    Analyzes evaluation results and compression gaps to create targeted recovery
    search plans that address specific quality shortcomings.
    """

    def __init__(self):
        """Initialize the RecoveryReplanAgent."""
        pass

    def create_replan(self, compress_gaps_conflicts: Dict[str, Any], judge_json: Dict[str, Any],
                     original_query: str = "") -> Dict[str, Any]:
        """
        Generate targeted replan to address quality gaps and issues.

        Analyzes evaluation scores and identified gaps to create focused recovery
        searches that target specific quality improvement areas.

        Args:
            compress_gaps_conflicts: Gaps and conflicts from compression analysis
            judge_json: Evaluation scores and priority fixes from EvaluatorAgent
            original_query: Original user query for context

        Returns:
            JSON replan with:
            - replan: List of targeted subqueries for recovery
            - expected_gain: Description of expected improvements
            - trigger_reason: Why recovery was triggered
            - target_metrics: Specific metrics to improve
        """
        # Extract key information
        gaps = compress_gaps_conflicts.get("gaps", [])
        conflicts = compress_gaps_conflicts.get("conflicts", [])
        scores = judge_json.get("scores", {})
        priority_fixes = judge_json.get("priority_fixes", [])
        overall_score = judge_json.get("overall_score", 0)

        # Only create replan if quality is below threshold
        if overall_score >= 4.0:
            return {
                "replan": [],
                "expected_gain": "No significant improvements needed - report quality is already high",
                "trigger_threshold": f"Current score {overall_score} above 4.0 threshold"
            }

        # Generate targeted subqueries
        replan_queries = self._generate_targeted_queries(gaps, conflicts, scores, priority_fixes, original_query)

        # Determine expected improvements
        expected_gain = self._determine_expected_gain(scores, priority_fixes)

        return {
            "replan": replan_queries,
            "expected_gain": expected_gain,
            "trigger_reason": f"Quality score {overall_score} below 4.0 threshold",
            "target_metrics": self._identify_target_metrics(scores)
        }

    def _generate_targeted_queries(self, gaps: List[str], conflicts: List[Dict], scores: Dict[str, int],
                                 priority_fixes: List[str], original_query: str) -> List[Dict[str, Any]]:
        """Generate 3-5 targeted subqueries to address specific quality issues."""
        queries = []

        # Address recency issues (most common problem)
        if scores.get("recency", 5) <= 2:
            queries.append({
                "subquery": "ultra-processed foods health research 2024 2025 recent studies",
                "rationale": "Address lack of recent evidence by targeting 2024-2025 publications",
                "operators": ["site:pubmed.ncbi.nlm.nih.gov", "site:nih.gov", "inurl:2024", "inurl:2025"],
                "k": 8
            })

        # Address coverage issues
        if scores.get("coverage", 5) <= 2:
            queries.append({
                "subquery": "ultra-processed foods systematic review meta-analysis comprehensive",
                "rationale": "Expand coverage with high-quality systematic reviews and meta-analyses",
                "operators": ["site:cochranelibrary.com", "site:pubmed.ncbi.nlm.nih.gov", "filetype:pdf"],
                "k": 6
            })

        # Address faithfulness/evidence quality issues
        if scores.get("faithfulness", 5) <= 3:
            queries.append({
                "subquery": "ultra-processed foods randomized controlled trial clinical study methodology",
                "rationale": "Improve evidence quality with RCTs and rigorous clinical studies",
                "operators": ["site:clinicaltrials.gov", "site:pubmed.ncbi.nlm.nih.gov", "inurl:rct"],
                "k": 6
            })

        # Address balance issues
        if scores.get("balance", 5) <= 2:
            queries.append({
                "subquery": "ultra-processed foods benefits advantages nutritional value positive",
                "rationale": "Balance perspective by seeking evidence of potential benefits or advantages",
                "operators": ["site:nutritionsource.hsph.harvard.edu", "site:eatright.org"],
                "k": 5
            })

        # Address specific gaps from compression analysis
        for gap in gaps[:2]:  # Focus on top 2 gaps
            if "2024-2025" in gap.lower() or "recent" in gap.lower():
                # Already handled above
                continue
            elif "systematic review" in gap.lower():
                queries.append({
                    "subquery": "ultra-processed foods umbrella review systematic evidence synthesis",
                    "rationale": "Address gap in comprehensive systematic reviews",
                    "operators": ["site:pubmed.ncbi.nlm.nih.gov", "site:cochranelibrary.com"],
                    "k": 6
                })
            elif "population" in gap.lower() or "age group" in gap.lower():
                queries.append({
                    "subquery": "ultra-processed foods children elderly demographics population health",
                    "rationale": "Address gap in population-specific research across age groups",
                    "operators": ["inurl:population", "inurl:demographic", "inurl:children", "inurl:elderly"],
                    "k": 6
                })
            elif "long-term" in gap.lower() or "longitudinal" in gap.lower():
                queries.append({
                    "subquery": "ultra-processed foods longitudinal cohort long-term follow-up study",
                    "rationale": "Address gap in long-term longitudinal health outcome studies",
                    "operators": ["site:pubmed.ncbi.nlm.nih.gov", "inurl:longitudinal", "inurl:cohort"],
                    "k": 6
                })

        # Address conflicts by seeking clarifying evidence
        if conflicts:
            for conflict in conflicts[:1]:  # Focus on main conflict
                claim = conflict.get("claim", "")
                if "benefit" in claim.lower():
                    queries.append({
                        "subquery": "ultra-processed foods health benefits controversy evidence review",
                        "rationale": "Resolve conflict about health benefits with authoritative reviews",
                        "operators": ["site:who.int", "site:fda.gov", "site:pubmed.ncbi.nlm.nih.gov"],
                        "k": 6
                    })

        # Limit to 5 queries maximum
        return queries[:5]

    def _determine_expected_gain(self, scores: Dict[str, int], priority_fixes: List[str]) -> str:
        """Determine what metrics should improve from the replan execution."""
        improvements = []

        # Map low scores to expected improvements
        if scores.get("recency", 5) <= 2:
            improvements.append("Recency score should increase to 3-4 with 2024-2025 sources")

        if scores.get("coverage", 5) <= 2:
            improvements.append("Coverage score should increase to 3-4 with diverse systematic reviews")

        if scores.get("faithfulness", 5) <= 3:
            improvements.append("Faithfulness score should increase to 4-5 with higher quality evidence")

        if scores.get("balance", 5) <= 2:
            improvements.append("Balance score should increase to 3-4 with broader perspective coverage")

        # Add overall improvement expectation
        current_avg = sum(scores.values()) / len(scores) if scores else 0
        target_avg = min(4.5, current_avg + 1.0)
        improvements.append(f"Overall score should improve from {current_avg:.1f} to approximately {target_avg:.1f}")

        return "; ".join(improvements) if improvements else "Minimal improvements expected"

    def _identify_target_metrics(self, scores: Dict[str, int]) -> List[str]:
        """Identify which specific metrics need improvement for tracking."""
        target_metrics = []

        for metric, score in scores.items():
            if score <= 2:
                target_metrics.append(f"{metric} (current: {score}/5)")

        return target_metrics

    def execute_replan(self, replan_json: Dict[str, Any], researcher_agent) -> List[Dict[str, Any]]:
        """
        Execute the replan by running additional targeted searches.

        Takes the recovery plan and executes the targeted searches using the
        ResearcherAgent to gather additional evidence for quality improvement.

        Args:
            replan_json: Replan specification from create_replan
            researcher_agent: ResearcherAgent instance to execute searches

        Returns:
            List of additional evidence findings from recovery searches
        """
        replan_queries = replan_json.get("replan", [])
        additional_evidence = []

        print(f"\n=== EXECUTING RECOVERY REPLAN ===")
        print(f"Running {len(replan_queries)} targeted recovery queries...")

        for i, query_spec in enumerate(replan_queries):
            print(f"\nRecovery Query {i+1}: {query_spec['subquery']}")
            print(f"Rationale: {query_spec['rationale']}")

            # Convert to format expected by ResearcherAgent
            subquery_obj = {
                "subquery": query_spec["subquery"],
                "operators": query_spec.get("operators", []),
                "k": query_spec.get("k", 6)
            }

            # Execute search
            try:
                evidence_result = researcher_agent.research_subquery(subquery_obj)
                additional_evidence.append(evidence_result)

                findings_count = len(evidence_result.get("findings", []))
                print(f"Found {findings_count} additional evidence items")

            except Exception as e:
                print(f"Error in recovery query {i+1}: {e}")
                # Continue with other queries even if one fails

        return additional_evidence

    def evaluate_improvement(self, original_evaluation: Dict[str, Any],
                           new_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare before/after evaluations to measure recovery effectiveness.

        Analyzes the improvement in evaluation scores after recovery execution
        to determine if the recovery was successful.

        Args:
            original_evaluation: Evaluation before replan execution
            new_evaluation: Evaluation after replan execution

        Returns:
            Improvement analysis with:
            - metric_improvements: Per-metric before/after comparison
            - overall_improvement: Overall score change
            - success: Boolean indicating meaningful improvement
            - summary: Human-readable improvement summary
        """
        original_scores = original_evaluation.get("scores", {})
        new_scores = new_evaluation.get("scores", {})

        improvements = {}
        for metric in original_scores:
            if metric in new_scores:
                improvement = new_scores[metric] - original_scores[metric]
                improvements[metric] = {
                    "before": original_scores[metric],
                    "after": new_scores[metric],
                    "improvement": improvement
                }

        original_overall = original_evaluation.get("overall_score", 0)
        new_overall = new_evaluation.get("overall_score", 0)
        overall_improvement = new_overall - original_overall

        return {
            "metric_improvements": improvements,
            "overall_improvement": {
                "before": original_overall,
                "after": new_overall,
                "improvement": overall_improvement
            },
            "success": overall_improvement > 0.3,  # Threshold for meaningful improvement
            "summary": self._generate_improvement_summary(improvements, overall_improvement)
        }

    def _generate_improvement_summary(self, improvements: Dict, overall_improvement: float) -> str:
        """Generate human-readable improvement summary for reporting."""
        if overall_improvement >= 0.5:
            return f"Significant improvement achieved (+{overall_improvement:.1f} overall score)"
        elif overall_improvement >= 0.2:
            return f"Moderate improvement achieved (+{overall_improvement:.1f} overall score)"
        elif overall_improvement > 0:
            return f"Minor improvement achieved (+{overall_improvement:.1f} overall score)"
        else:
            return f"No meaningful improvement detected ({overall_improvement:+.1f} overall score)"