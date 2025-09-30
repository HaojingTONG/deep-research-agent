"""
Phase 2: Research Brief Agent

Creates detailed research outlines from clarified specifications.
Generates sub-questions, inclusion criteria, and evidence requirements.
"""

from typing import Dict, Any, List
from utils import extract_topic_keywords


class ResearchBriefAgent:
    """
    Phase 2: Research Brief Agent - Create detailed research outline from clarified spec.

    Transforms structured research specifications into comprehensive research briefs
    with sub-questions, inclusion criteria, and success metrics.
    """

    def create_brief(self, clarify_json: Dict[str, Any]) -> str:
        """
        Generate research brief from clarified research specification.

        Creates a comprehensive markdown research brief that includes objectives,
        sub-questions, inclusion criteria, expected evidence types, and potential risks.

        Args:
            clarify_json: Output from ClarifyAgent containing structured research spec

        Returns:
            Markdown formatted research brief ready for planning phase
        """
        objective = clarify_json.get("objective", "")
        definitions = clarify_json.get("definitions", [])
        time_window = clarify_json.get("time_window", "")
        geography = clarify_json.get("geography", "")
        audience = clarify_json.get("audience", "")
        success_criteria = clarify_json.get("success_criteria", [])

        # Extract topic keywords for maintaining focus
        topic_keywords = extract_topic_keywords(objective)

        # Generate sub-questions based on objective
        sub_questions = self._generate_sub_questions(objective, clarify_json, topic_keywords)

        # Define inclusion criteria
        inclusion_criteria = self._define_inclusion_criteria(clarify_json)

        # Expected evidence artifacts
        evidence_artifacts = self._define_evidence_artifacts(clarify_json)

        # Risks and unknowns
        risks_unknowns = self._identify_risks_unknowns(clarify_json)

        # Build markdown brief
        brief_md = f"""# Research Brief

## Objective
{objective}

## Key Definitions
{self._format_definitions(definitions)}

## Research Scope
- **Time Window:** {time_window}
- **Geography:** {geography}
- **Target Audience:** {audience}
- **Topic Keywords:** {', '.join(topic_keywords)}

## Key Sub-Questions

{self._format_sub_questions(sub_questions)}

## Inclusion Criteria

{self._format_inclusion_criteria(inclusion_criteria)}

## Expected Evidence Artifacts

{self._format_evidence_artifacts(evidence_artifacts)}

## Risks & Unknowns to Check

{self._format_risks_unknowns(risks_unknowns)}

## Success Criteria
{self._format_success_criteria(success_criteria)}
"""

        return brief_md

    def _generate_sub_questions(self, objective: str, clarify_json: Dict, topic_keywords: List[str]) -> List[str]:
        """Generate 3-6 balanced sub-questions based on research objective."""
        sub_questions = []

        obj_lower = objective.lower()

        if "ultra-processed foods" in obj_lower:
            sub_questions = [
                "What are the documented health benefits (if any) of ultra-processed foods?",
                "What are the proven health risks and negative impacts of ultra-processed foods?",
                "How has the scientific consensus on ultra-processed foods evolved in 2024-2025?",
                "What are the current dietary recommendations from major health organizations?",
                "What gaps exist in current research on ultra-processed foods?",
                "How do ultra-processed food impacts vary across different populations?"
            ]
        elif "compare" in obj_lower and "evidence" in obj_lower:
            sub_questions = [
                "What is the current state of evidence supporting the positive aspects?",
                "What is the current state of evidence highlighting concerns or negative aspects?",
                "How has the evidence base changed over the specified time period?",
                "What are the methodological strengths and limitations of recent studies?",
                "Where do experts disagree and what are the key debate points?",
                "What practical implications emerge from the evidence?"
            ]
        else:
            # Generate topic-specific sub-questions using extracted keywords
            main_topic = ' '.join(topic_keywords[:2]) if topic_keywords else "the topic"

            sub_questions = [
                f"What is the current state of research on {main_topic}?",
                f"What are the main applications and opportunities for {main_topic}?",
                f"What are the key challenges and limitations regarding {main_topic}?",
                f"What evidence supports different approaches to {main_topic}?",
                f"What are the practical implications of {main_topic} implementation?",
                f"What gaps or future research directions exist for {main_topic}?"
            ]

        return sub_questions[:6]  # Limit to 6 questions max

    def _define_inclusion_criteria(self, clarify_json: Dict) -> Dict[str, List[str]]:
        """Define what sources to include based on research requirements."""
        time_window = clarify_json.get("time_window", "")

        return {
            "Source Types": [
                "Peer-reviewed journal articles",
                "Systematic reviews and meta-analyses",
                "Reports from reputable health organizations (WHO, FDA, etc.)",
                "Government health agency publications",
                "Clinical trial results"
            ],
            "Quality Standards": [
                "Published in reputable journals (impact factor > 2.0 preferred)",
                "Sample size > 100 for observational studies",
                "Proper control groups for experimental studies",
                "Clear methodology and statistical analysis"
            ],
            "Recency": [
                f"Primary focus on studies published within {time_window}",
                "Foundational studies from earlier periods if highly cited",
                "Most recent systematic reviews and meta-analyses available"
            ],
            "Exclusions": [
                "Non-peer reviewed preprints (unless from highly reputable sources)",
                "Industry-funded studies without independent validation",
                "Paywalled content without open access alternatives",
                "Opinion pieces without supporting empirical data"
            ]
        }

    def _define_evidence_artifacts(self, clarify_json: Dict) -> List[str]:
        """Define what types of evidence to collect during research."""
        return [
            "**Direct Quotes:** Key findings and conclusions from studies",
            "**Statistical Data:** Effect sizes, confidence intervals, p-values",
            "**Study Characteristics:** Sample sizes, methodologies, study duration",
            "**Expert Opinions:** Quotes from lead researchers and subject matter experts",
            "**Timeline Information:** When key studies were published and findings emerged",
            "**Conflicting Results:** Studies that show contradictory findings",
            "**Practical Applications:** Real-world implementation examples and outcomes"
        ]

    def _identify_risks_unknowns(self, clarify_json: Dict) -> List[str]:
        """Identify potential research risks and unknowns to monitor."""
        risks = [
            "**Publication Bias:** Positive results more likely to be published",
            "**Industry Influence:** Potential conflicts of interest in funding",
            "**Study Quality Variation:** Differences in methodological rigor",
            "**Population Differences:** Results may not generalize across demographics",
            "**Temporal Lag:** Most recent evidence may not yet be peer-reviewed"
        ]

        obj_lower = clarify_json.get("objective", "").lower()
        if "food" in obj_lower or "nutrition" in obj_lower:
            risks.extend([
                "**Individual Variation:** Nutritional impacts vary significantly between individuals",
                "**Long-term vs Short-term Effects:** Different timeframes may show different results",
                "**Confounding Factors:** Diet is complex with many interrelated variables"
            ])

        return risks

    def _format_definitions(self, definitions: List[str]) -> str:
        """Format definitions list for markdown output."""
        if not definitions:
            return "No specific definitions provided."
        return "\n".join([f"- **{def_text}**" for def_text in definitions])

    def _format_sub_questions(self, sub_questions: List[str]) -> str:
        """Format sub-questions as numbered list."""
        return "\n".join([f"{i+1}. {q}" for i, q in enumerate(sub_questions)])

    def _format_inclusion_criteria(self, criteria: Dict[str, List[str]]) -> str:
        """Format inclusion criteria with categories and items."""
        result = ""
        for category, items in criteria.items():
            result += f"### {category}\n"
            result += "\n".join([f"- {item}" for item in items])
            result += "\n\n"
        return result.strip()

    def _format_evidence_artifacts(self, artifacts: List[str]) -> str:
        """Format evidence artifacts as bulleted list."""
        return "\n".join([f"- {artifact}" for artifact in artifacts])

    def _format_risks_unknowns(self, risks: List[str]) -> str:
        """Format risks and unknowns as bulleted list."""
        return "\n".join([f"- {risk}" for risk in risks])

    def _format_success_criteria(self, criteria: List[str]) -> str:
        """Format success criteria as bulleted list."""
        return "\n".join([f"- {criterion}" for criterion in criteria])