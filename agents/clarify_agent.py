"""
Phase 1: Clarify Agent

Transforms vague user queries into structured research specifications.
Extracts key parameters like objectives, definitions, time windows, and success criteria.
"""

from typing import Dict, Any, List


class ClarifyAgent:
    """
    Phase 1: Clarify Agent - Turn vague query into actionable research input.

    This agent transforms ambiguous user queries into structured research
    specifications that can be processed by downstream agents.
    """

    def __init__(self):
        """Initialize the ClarifyAgent."""
        # In a real implementation, you'd use your preferred LLM
        # self.llm = OpenAI()  # Requires API key
        pass

    def clarify_query(self, user_query: str) -> Dict[str, Any]:
        """
        Transform user query into structured research specification.

        Analyzes the user's input and extracts key research parameters including
        objectives, definitions, time scope, geography, audience, and success criteria.

        Args:
            user_query: Raw user input query

        Returns:
            Structured dict with research parameters including:
            - objective: Main research goal
            - definitions: Key terms requiring definition
            - time_window: Temporal scope for research
            - geography: Geographic scope
            - audience: Target audience type
            - deliverable: Expected output format
            - success_criteria: Quality and completeness requirements
        """
        # For demo purposes, using rule-based logic
        # In production, this would use LLM with the system prompt

        result = {
            "objective": self._extract_objective(user_query),
            "definitions": self._extract_definitions(user_query),
            "time_window": self._extract_time_window(user_query),
            "geography": self._extract_geography(user_query),
            "audience": self._extract_audience(user_query),
            "deliverable": self._extract_deliverable(user_query),
            "success_criteria": self._generate_success_criteria(user_query)
        }

        return result

    def _extract_objective(self, query: str) -> str:
        """Extract main research objective from query."""
        if "compare" in query.lower() and "evidence" in query.lower():
            return f"Compare recent evidence and provide evidence-based analysis on: {query}"
        elif "recommend" in query.lower():
            return f"Provide evidence-based recommendations on: {query}"
        else:
            return f"Research and analyze: {query}"

    def _extract_definitions(self, query: str) -> List[str]:
        """Identify key terms that need definition."""
        definitions = []

        if "ultra-processed foods" in query.lower():
            definitions.append("ultra-processed foods: industrially formulated products with ≥5 ingredients, additives, preservatives")
        if "evidence" in query.lower():
            definitions.append("evidence: peer-reviewed studies, meta-analyses, systematic reviews")

        return definitions

    def _extract_time_window(self, query: str) -> str:
        """Extract or infer time window."""
        if "2024" in query and "2025" in query:
            return "2024-01 to 2025-09"
        elif "recent" in query.lower() or "latest" in query.lower():
            return "2023-01 to 2025-09"
        else:
            return "2020-01 to 2025-09"

    def _extract_geography(self, query: str) -> str:
        """Extract or infer geographic scope."""
        if any(country in query.lower() for country in ["us", "usa", "united states"]):
            return "US"
        elif any(country in query.lower() for country in ["china", "cn"]):
            return "CN"
        else:
            return "global"

    def _extract_audience(self, query: str) -> str:
        """Infer target audience."""
        if "technical" in query.lower() or "research" in query.lower():
            return "researcher"
        elif "executive" in query.lower() or "summary" in query.lower():
            return "executive"
        else:
            return "consumer"

    def _extract_deliverable(self, query: str) -> str:
        """Define expected deliverable format."""
        return "comprehensive report with evidence analysis and actionable recommendations"

    def _generate_success_criteria(self, query: str) -> List[str]:
        """Generate success criteria based on query type."""
        criteria = [">=10 unique sources", "no paywalled-only sources"]

        if "compare" in query.lower():
            criteria.append("covers multiple perspectives")
        if "recommend" in query.lower():
            criteria.append("includes actionable recommendations")
        if "evidence" in query.lower():
            criteria.append("includes recent peer-reviewed studies")

        return criteria