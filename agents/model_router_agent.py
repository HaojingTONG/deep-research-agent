"""
Phase 9: Model Router Agent

Optimizes cost/quality tradeoffs by selecting appropriate model profiles.
Analyzes query complexity and node requirements to make routing decisions.
"""

import re
from typing import Dict, Any, List


class ModelRouterAgent:
    """
    Phase 9: Model Router Agent - Optimize cost/quality tradeoffs by selecting appropriate model profiles.

    Analyzes query complexity and pipeline node characteristics to make optimal
    model routing decisions that balance cost efficiency with quality requirements.
    """

    def __init__(self):
        """Initialize the ModelRouterAgent with predefined model profiles and node characteristics."""
        # Define model profiles with characteristics
        self.model_profiles = {
            "cheap": {
                "cost_factor": 0.3,
                "quality_factor": 0.6,
                "max_context": 8000,
                "best_for": ["simple parsing", "structured data", "quick decisions"]
            },
            "balanced": {
                "cost_factor": 1.0,
                "quality_factor": 0.8,
                "max_context": 32000,
                "best_for": ["moderate reasoning", "balanced tasks", "general analysis"]
            },
            "premium": {
                "cost_factor": 3.0,
                "quality_factor": 1.0,
                "max_context": 128000,
                "best_for": ["complex reasoning", "critical outputs", "long contexts"]
            }
        }

        # Define node characteristics
        self.node_characteristics = {
            "clarify": {
                "context_need": "low",
                "reasoning_complexity": "medium",
                "output_criticality": "medium",
                "typical_input_length": 500,
                "description": "Parse and structure user query"
            },
            "brief": {
                "context_need": "medium",
                "reasoning_complexity": "medium",
                "output_criticality": "high",
                "typical_input_length": 1000,
                "description": "Generate comprehensive research outline"
            },
            "plan": {
                "context_need": "medium",
                "reasoning_complexity": "high",
                "output_criticality": "high",
                "typical_input_length": 3000,
                "description": "Create diversified search strategy"
            },
            "research": {
                "context_need": "low",
                "reasoning_complexity": "low",
                "output_criticality": "medium",
                "typical_input_length": 800,
                "description": "Execute searches and extract evidence"
            },
            "compress": {
                "context_need": "very_high",
                "reasoning_complexity": "very_high",
                "output_criticality": "very_high",
                "typical_input_length": 50000,
                "description": "Synthesize evidence and identify conflicts"
            },
            "report": {
                "context_need": "very_high",
                "reasoning_complexity": "very_high",
                "output_criticality": "critical",
                "typical_input_length": 40000,
                "description": "Generate final narrative report with citations"
            },
            "judge": {
                "context_need": "high",
                "reasoning_complexity": "high",
                "output_criticality": "high",
                "typical_input_length": 15000,
                "description": "Evaluate report quality across dimensions"
            }
        }

    def route_models(self, user_query: str, nodes: List[str] = None) -> Dict[str, Any]:
        """
        Determine optimal model routing for research pipeline nodes.

        Analyzes query complexity and matches it with node requirements to select
        the most cost-effective model profiles while maintaining quality standards.

        Args:
            user_query: The user's research query for complexity analysis
            nodes: List of nodes to route (defaults to all 7 pipeline nodes)

        Returns:
            Routing recommendations with:
            - routing: List of node routing decisions
            - query_analysis: Complexity analysis results
            - total_estimated_cost: Relative cost estimate
            - cost_breakdown: Count by profile type
            - optimization_notes: Improvement suggestions
        """
        if nodes is None:
            nodes = ["clarify", "brief", "plan", "research", "compress", "report", "judge"]

        query_complexity = self._analyze_query_complexity(user_query)

        routing_decisions = []
        total_estimated_cost = 0

        for node in nodes:
            if node not in self.node_characteristics:
                continue

            profile = self._select_profile_for_node(node, query_complexity, user_query)
            explanation = self._generate_explanation(node, profile, query_complexity)

            routing_decisions.append({
                "node": node,
                "profile": profile,
                "why": explanation
            })

            # Estimate relative cost
            node_cost = self.model_profiles[profile]["cost_factor"]
            total_estimated_cost += node_cost

        return {
            "routing": routing_decisions,
            "query_analysis": query_complexity,
            "total_estimated_cost": round(total_estimated_cost, 2),
            "cost_breakdown": self._generate_cost_breakdown(routing_decisions),
            "optimization_notes": self._generate_optimization_notes(routing_decisions, query_complexity)
        }

    def _analyze_query_complexity(self, user_query: str) -> Dict[str, Any]:
        """Analyze the complexity characteristics of the user query for routing decisions."""
        query_length = len(user_query)

        # Check for complexity indicators
        complexity_indicators = {
            "temporal_scope": any(word in user_query.lower() for word in ["2024", "2025", "recent", "latest", "current"]),
            "comparative": any(word in user_query.lower() for word in ["compare", "versus", "vs", "difference", "contrast", "比较"]),
            "multi_domain": any(word in user_query.lower() for word in ["and", "plus", "including", "across", "multiple", "多", "全面", "综合"]),
            "technical_topic": any(word in user_query.lower() for word in ["processed", "clinical", "systematic", "meta-analysis", "evidence", "超加工", "临床", "系统性", "荟萃", "证据", "研究"]),
            "actionable_output": any(word in user_query.lower() for word in ["recommendations", "guidance", "advice", "what should", "how to", "建议", "指导", "如何"]),
            "comprehensive": any(word in user_query.lower() for word in ["comprehensive", "complete", "thorough", "detailed", "extensive", "全面", "详细", "完整", "深入", "彻底"])
        }

        # Calculate complexity score
        complexity_score = sum(complexity_indicators.values())

        # Determine overall complexity level
        if complexity_score >= 4:
            complexity_level = "very_high"
        elif complexity_score >= 3:
            complexity_level = "high"
        elif complexity_score >= 2:
            complexity_level = "medium"
        else:
            complexity_level = "low"

        return {
            "query_length": query_length,
            "complexity_indicators": complexity_indicators,
            "complexity_score": complexity_score,
            "complexity_level": complexity_level,
            "estimated_evidence_volume": "high" if complexity_score >= 3 else "medium" if complexity_score >= 2 else "low"
        }

    def _select_profile_for_node(self, node: str, query_complexity: Dict, user_query: str) -> str:
        """Select the optimal model profile for a specific node based on requirements."""
        node_chars = self.node_characteristics[node]
        complexity_level = query_complexity["complexity_level"]
        query_length = query_complexity["query_length"]

        # Decision matrix based on node + query characteristics

        # Critical nodes always get premium for complex queries
        if node in ["compress", "report"] and complexity_level in ["high", "very_high"]:
            return "premium"

        # High-criticality nodes with complex queries get premium
        if node_chars["output_criticality"] == "critical":
            return "premium"
        elif node_chars["output_criticality"] == "very_high" and complexity_level in ["high", "very_high"]:
            return "premium"

        # Context-heavy nodes need higher profiles
        if node_chars["context_need"] == "very_high":
            return "premium" if complexity_level == "very_high" else "balanced"
        elif node_chars["context_need"] == "high" and complexity_level in ["high", "very_high"]:
            return "balanced"

        # Research node can usually be cheap (simple extraction)
        if node == "research":
            return "cheap" if complexity_level in ["low", "medium"] else "balanced"

        # Clarify can be cheap for simple queries
        if node == "clarify" and complexity_level in ["low", "medium"] and query_length < 200:
            return "cheap"

        # Default to balanced for most cases
        return "balanced"

    def _generate_explanation(self, node: str, profile: str, query_complexity: Dict) -> str:
        """Generate human-readable explanation for routing decision."""
        node_chars = self.node_characteristics[node]
        complexity_level = query_complexity["complexity_level"]

        # Base explanation components
        criticality = node_chars["output_criticality"]
        context_need = node_chars["context_need"]
        reasoning = node_chars["reasoning_complexity"]

        # Build explanation
        reasons = []

        if profile == "premium":
            if criticality in ["critical", "very_high"]:
                reasons.append(f"{criticality} output importance")
            if context_need == "very_high":
                reasons.append("extensive context processing")
            if reasoning in ["very_high", "high"]:
                reasons.append("complex reasoning required")
            if complexity_level in ["high", "very_high"]:
                reasons.append("complex query characteristics")

        elif profile == "balanced":
            if criticality == "high":
                reasons.append("important output quality")
            if context_need in ["medium", "high"]:
                reasons.append("moderate context needs")
            if reasoning == "medium":
                reasons.append("standard reasoning complexity")

        else:  # cheap
            if criticality == "medium":
                reasons.append("acceptable with lower quality")
            if context_need == "low":
                reasons.append("minimal context required")
            if reasoning == "low":
                reasons.append("simple processing task")

        explanation = "; ".join(reasons) if reasons else f"standard {profile} profile suitable"

        return explanation

    def _generate_cost_breakdown(self, routing_decisions: List[Dict]) -> Dict[str, int]:
        """Generate cost breakdown by profile type for analysis."""
        breakdown = {"cheap": 0, "balanced": 0, "premium": 0}

        for decision in routing_decisions:
            breakdown[decision["profile"]] += 1

        return breakdown

    def _generate_optimization_notes(self, routing_decisions: List[Dict], query_complexity: Dict) -> List[str]:
        """Generate optimization recommendations based on routing decisions."""
        notes = []

        profile_counts = self._generate_cost_breakdown(routing_decisions)
        complexity_level = query_complexity["complexity_level"]

        # Cost optimization suggestions
        if profile_counts["premium"] >= 4:
            notes.append("High premium usage - consider if all critical nodes truly need premium quality")
        elif profile_counts["cheap"] >= 4:
            notes.append("Heavy cheap usage - verify quality requirements are met")

        # Query-specific optimizations
        if complexity_level == "low" and profile_counts["premium"] >= 2:
            notes.append("Simple query with premium models - potential cost savings available")
        elif complexity_level == "very_high" and profile_counts["cheap"] >= 2:
            notes.append("Complex query with cheap models - quality may be compromised")

        # Node-specific recommendations
        premium_nodes = [d["node"] for d in routing_decisions if d["profile"] == "premium"]
        if "research" in premium_nodes:
            notes.append("Research node set to premium - usually balanced/cheap sufficient for search tasks")

        if not notes:
            notes.append("Routing appears well-optimized for query complexity and quality requirements")

        return notes