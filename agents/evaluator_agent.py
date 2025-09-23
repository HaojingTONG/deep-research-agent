"""
Phase 7: Evaluator Agent

Automatic report evaluation and scoring across multiple quality dimensions.
Provides comprehensive quality assessment with actionable improvement suggestions.
"""

import re
from typing import Dict, Any, List
from urllib.parse import urlparse


class EvaluatorAgent:
    """
    Phase 7: Evaluator/QA Agent - Automatic report evaluation and scoring.

    Evaluates research reports across 6 quality dimensions with scoring rubrics
    and generates priority improvement suggestions for quality assurance.
    """

    def __init__(self):
        """Initialize the EvaluatorAgent."""
        pass

    def evaluate_report(self, report_markdown: str, evidence_list: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate report quality across multiple dimensions.

        Performs comprehensive quality assessment including coverage, faithfulness,
        balance, recency, actionability, and readability with scoring and suggestions.

        Args:
            report_markdown: The complete Markdown report to evaluate
            evidence_list: Optional evidence list for additional validation

        Returns:
            JSON evaluation with:
            - scores: Dict of dimension scores (0-5 scale)
            - priority_fixes: List of improvement suggestions
            - overall_score: Average score across all dimensions
            - evaluation_summary: Brief quality assessment
        """
        # Extract report sections for analysis
        sections = self._extract_report_sections(report_markdown)

        # Calculate scores for each dimension
        scores = {
            "coverage": self._score_coverage(sections, evidence_list),
            "faithfulness": self._score_faithfulness(sections, report_markdown),
            "balance": self._score_balance(sections),
            "recency": self._score_recency(sections, evidence_list),
            "actionability": self._score_actionability(sections),
            "readability": self._score_readability(sections, report_markdown)
        }

        # Generate priority fix suggestions
        priority_fixes = self._generate_priority_fixes(scores, sections, evidence_list)

        return {
            "scores": scores,
            "priority_fixes": priority_fixes,
            "overall_score": round(sum(scores.values()) / len(scores), 1),
            "evaluation_summary": self._generate_evaluation_summary(scores)
        }

    def _extract_report_sections(self, report_markdown: str) -> Dict[str, str]:
        """Extract different sections from the report for analysis."""
        sections = {}

        # Split by markdown headers
        current_section = "header"
        current_content = []

        for line in report_markdown.split('\n'):
            if line.startswith('## '):
                # Save previous section
                sections[current_section] = '\n'.join(current_content)

                # Start new section
                section_name = line[3:].strip().lower().replace(' ', '_').replace('&', 'and')
                current_section = section_name
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        sections[current_section] = '\n'.join(current_content)

        return sections

    def _score_coverage(self, sections: Dict[str, str], evidence_list: List[Dict] = None) -> int:
        """Score coverage breadth (0-5) based on section completeness and evidence diversity."""
        score = 0

        # Check for essential sections
        required_sections = ['executive_summary', 'key_insights', 'recommendations', 'limitations_and_open_questions']
        sections_present = sum(1 for section in required_sections if section in sections)
        score += min(2, sections_present)  # Up to 2 points for section completeness

        # Check evidence diversity
        if evidence_list:
            unique_domains = set()
            for evidence in evidence_list:
                url = evidence.get("url", "")
                if url:
                    try:
                        domain = urlparse(url).netloc.replace('www.', '')
                        unique_domains.add(domain)
                    except:
                        pass

            domain_count = len(unique_domains)
            if domain_count >= 8:
                score += 2  # Excellent diversity
            elif domain_count >= 5:
                score += 1  # Good diversity
            # 0 points for limited diversity

        # Check topic breadth in key insights
        insights = sections.get('key_insights', '')
        topic_indicators = ['benefit', 'risk', 'recommendation', 'methodology', 'population', 'industry']
        topics_covered = sum(1 for topic in topic_indicators if topic in insights.lower())
        score += min(1, topics_covered // 2)  # 1 point if multiple topics covered

        return min(5, score)

    def _score_faithfulness(self, sections: Dict[str, str], full_report: str) -> int:
        """Score evidence faithfulness - citations match claims (0-5)."""
        score = 5  # Start with perfect score and deduct for issues

        # Check citation format consistency
        citation_pattern = r'\[(\d+(?:,\d+)*)\]'
        citations = re.findall(citation_pattern, full_report)

        if not citations:
            score -= 3  # Major deduction for no citations

        # Check for unsupported claims (statements without citations)
        insights = sections.get('key_insights', '')
        if insights:
            # Split into sentences and check if major claims have citations
            sentences = re.split(r'[.!?]+', insights)
            major_claims = [s for s in sentences if any(word in s.lower() for word in ['studies', 'research', 'evidence', 'shows', 'indicates', 'suggests'])]

            uncited_claims = 0
            for claim in major_claims:
                if not re.search(citation_pattern, claim):
                    uncited_claims += 1

            if uncited_claims > 0:
                score -= min(2, uncited_claims)  # Deduct up to 2 points

        # Check for broken citation references
        evidence_section = sections.get('evidence_references', '')
        if evidence_section:
            # Count available references
            ref_pattern = r'\[(\d+)\]'
            available_refs = set(re.findall(ref_pattern, evidence_section))

            # Check if all cited numbers have corresponding references
            for citation_group in citations:
                for ref_num in citation_group.split(','):
                    ref_num = ref_num.strip()
                    if ref_num not in available_refs:
                        score -= 1  # Deduct for each broken reference
                        break  # Only deduct once per citation group

        return max(0, score)

    def _score_balance(self, sections: Dict[str, str]) -> int:
        """Score balance between different perspectives (0-5)."""
        score = 0

        insights = sections.get('key_insights', '').lower()
        summary = sections.get('executive_summary', '').lower()
        combined_text = insights + " " + summary

        # Check for positive/benefit mentions
        positive_indicators = ['benefit', 'positive', 'advantage', 'helpful', 'good']
        has_positive = any(indicator in combined_text for indicator in positive_indicators)

        # Check for negative/risk mentions
        negative_indicators = ['risk', 'harmful', 'negative', 'danger', 'concern', 'limitation']
        has_negative = any(indicator in combined_text for indicator in negative_indicators)

        # Check for neutral/methodological content
        neutral_indicators = ['methodology', 'study', 'research', 'analysis', 'evidence', 'investigation']
        has_neutral = any(indicator in combined_text for indicator in neutral_indicators)

        # Score based on perspective diversity
        if has_positive and has_negative and has_neutral:
            score = 5  # Excellent balance
        elif has_positive and has_negative:
            score = 4  # Good balance
        elif (has_positive or has_negative) and has_neutral:
            score = 3  # Moderate balance
        elif has_positive or has_negative:
            score = 2  # Limited perspective
        else:
            score = 1  # Very limited

        # Check for explicit conflict acknowledgment
        limitations = sections.get('limitations_and_open_questions', '').lower()
        if 'conflict' in limitations or 'disagree' in limitations or 'contradic' in limitations:
            score = min(5, score + 1)  # Bonus for acknowledging conflicts

        return score

    def _score_recency(self, sections: Dict[str, str], evidence_list: List[Dict] = None) -> int:
        """Score recency of evidence (0-5) based on publication dates."""
        score = 0

        if evidence_list:
            # Count recent evidence (2024-2025)
            recent_count = 0
            total_dated = 0

            for evidence in evidence_list:
                date = evidence.get("date")
                if date:
                    total_dated += 1
                    try:
                        year = int(date.split("-")[0])
                        if year >= 2024:
                            recent_count += 1
                    except:
                        pass

            if total_dated > 0:
                recent_ratio = recent_count / total_dated
                if recent_ratio >= 0.7:
                    score += 3  # Excellent recency
                elif recent_ratio >= 0.5:
                    score += 2  # Good recency
                elif recent_ratio >= 0.3:
                    score += 1  # Moderate recency
                # 0 points for poor recency
            else:
                score -= 1  # Penalty for no date information

        # Check for timeline section
        if 'timeline' in sections or 'evolution' in sections:
            timeline_section = sections.get('research_timeline_and_evolution', sections.get('timeline', ''))
            if '2024' in timeline_section or '2025' in timeline_section:
                score += 1  # Bonus for recent timeline content

        # Check for recent mentions in main content
        insights = sections.get('key_insights', '')
        if '2024' in insights or '2025' in insights:
            score += 1  # Bonus for recent references

        return min(5, max(0, score))

    def _score_actionability(self, sections: Dict[str, str]) -> int:
        """Score actionability of recommendations (0-5) based on specificity and clarity."""
        score = 0

        recommendations = sections.get('recommendations', '')
        if not recommendations:
            return 0

        # Check for specific, numbered recommendations
        numbered_recs = re.findall(r'\*\*\d+\..*?\*\*', recommendations)
        if len(numbered_recs) >= 3:
            score += 2  # Good structure
        elif len(numbered_recs) >= 1:
            score += 1  # Some structure

        # Check for action verbs
        action_verbs = ['follow', 'conduct', 'establish', 'develop', 'monitor', 'consult', 'adhere', 'consider']
        action_count = sum(1 for verb in action_verbs if verb in recommendations.lower())
        score += min(2, action_count // 2)  # Up to 2 points for actionable language

        # Check for risk considerations
        if 'risk' in recommendations.lower() and 'consideration' in recommendations.lower():
            score += 1  # Bonus for risk awareness

        # Check for specificity (avoid vague language)
        vague_indicators = ['should consider', 'might want to', 'could potentially', 'may be beneficial']
        vague_count = sum(1 for phrase in vague_indicators if phrase in recommendations.lower())
        if vague_count == 0:
            score += 1  # Bonus for specific language
        else:
            score -= min(1, vague_count // 2)  # Penalty for vague language

        return min(5, max(0, score))

    def _score_readability(self, sections: Dict[str, str], full_report: str) -> int:
        """Score readability and structure (0-5) based on formatting and organization."""
        score = 0

        # Check structural elements
        if '## Executive Summary' in full_report:
            score += 1
        if '## Key Insights' in full_report:
            score += 1
        if '## Recommendations' in full_report:
            score += 1
        if '## Evidence References' in full_report:
            score += 1

        # Check for bullet points and formatting
        bullet_count = full_report.count('• ')
        numbered_count = full_report.count('**1.')

        if bullet_count >= 5 or numbered_count >= 3:
            score += 1  # Good use of formatting

        # Check for appropriate section lengths
        summary = sections.get('executive_summary', '')
        insights = sections.get('key_insights', '')

        # Executive summary should be concise (5 bullets)
        summary_bullets = summary.count('• ')
        if 4 <= summary_bullets <= 6:
            score += 1  # Good summary length

        # Penalize overly long sections
        if len(insights) > 2000:
            score -= 1  # Too verbose

        # Check for clear conclusion/takeaway
        if 'Risk Considerations' in full_report or 'Consumer Guidance' in full_report:
            score += 1  # Good conclusion structure

        return min(5, max(0, score))

    def _generate_priority_fixes(self, scores: Dict[str, int], sections: Dict[str, str],
                               evidence_list: List[Dict] = None) -> List[str]:
        """Generate prioritized fix suggestions based on scores."""
        fixes = []

        # Identify lowest scoring areas for priority fixes
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])

        for dimension, score in sorted_scores[:3]:  # Focus on 3 lowest scores
            if score <= 2:  # Only suggest fixes for poor scores
                if dimension == "coverage":
                    fixes.append("Expand research scope to include more diverse perspectives and source types")
                elif dimension == "faithfulness":
                    fixes.append("Add proper citations [n] for all major claims and verify reference accuracy")
                elif dimension == "balance":
                    fixes.append("Include both supportive and contradicting evidence to provide balanced analysis")
                elif dimension == "recency":
                    fixes.append("Add more 2024-2025 sources and highlight recent developments in timeline")
                elif dimension == "actionability":
                    fixes.append("Make recommendations more specific and actionable with clear next steps")
                elif dimension == "readability":
                    fixes.append("Improve report structure with clearer headings and better formatting")

        # Add specific fixes based on content analysis
        if evidence_list:
            high_quality_count = sum(1 for e in evidence_list if e.get("quality", 0) >= 4)
            if high_quality_count < len(evidence_list) * 0.7:
                fixes.append("Prioritize higher quality sources (systematic reviews, peer-reviewed studies)")

        # Limit to 2-4 fixes as specified
        return fixes[:4]

    def _generate_evaluation_summary(self, scores: Dict[str, int]) -> str:
        """Generate a brief evaluation summary based on average scores."""
        avg_score = sum(scores.values()) / len(scores)

        if avg_score >= 4.5:
            return "Excellent report quality across all dimensions"
        elif avg_score >= 3.5:
            return "Good report quality with minor areas for improvement"
        elif avg_score >= 2.5:
            return "Moderate report quality requiring focused improvements"
        else:
            return "Report needs significant improvements across multiple dimensions"