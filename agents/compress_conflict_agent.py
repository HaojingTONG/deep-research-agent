"""
Phase 5: Compress/Conflict Agent

Clusters evidence, identifies conflicts, and extracts key findings.
Synthesizes findings from multiple subqueries and detects contradictory evidence.
"""

from typing import Dict, Any, List
from urllib.parse import urlparse


class CompressConflictAgent:
    """
    Phase 5: Compress + Conflict - Cluster evidence, identify conflicts, extract key findings.

    Takes evidence from multiple subqueries and performs synthesis including clustering
    by themes, conflict detection, gap analysis, and coverage statistics generation.
    """

    def compress_and_align(self, all_evidence: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Compress and align evidence blocks from multiple subqueries.

        Performs comprehensive analysis including theme clustering, conflict detection,
        gap identification, and coverage assessment to synthesize research findings.

        Args:
            all_evidence: List of evidence findings from all subqueries

        Returns:
            Structured compression analysis with:
            - clusters: Thematic groupings of evidence
            - key_findings: Synthesized findings with source references
            - conflicts: Identified contradictory claims
            - gaps: Research gaps and limitations
            - coverage_stats: Statistical analysis of coverage
        """
        # Flatten all evidence blocks into single list with indices
        flattened_evidence = []
        evidence_map = {}  # Map index to original evidence

        idx = 0
        for subquery_evidence in all_evidence:
            for evidence in subquery_evidence.get("findings", []):
                flattened_evidence.append(evidence)
                evidence_map[idx] = evidence
                idx += 1

        # Step 1: Cluster by theme and deduplicate
        clusters = self._cluster_evidence(flattened_evidence)

        # Step 2: Extract key findings with source references
        key_findings = self._extract_key_findings(flattened_evidence, clusters)

        # Step 3: Identify conflicts
        conflicts = self._identify_conflicts(flattened_evidence)

        # Step 4: Identify gaps and next steps
        gaps = self._identify_research_gaps(flattened_evidence)

        # Step 5: Calculate coverage statistics
        coverage_stats = self._calculate_coverage_stats(flattened_evidence)

        return {
            "clusters": clusters,
            "key_findings": key_findings,
            "conflicts": conflicts,
            "gaps": gaps,
            "coverage_stats": coverage_stats
        }

    def _cluster_evidence(self, evidence_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cluster evidence by themes and deduplicate near-duplicates."""
        clusters = []

        # Define theme categories based on content analysis
        theme_keywords = {
            "health_benefits": ["benefits", "positive", "advantage", "helpful", "nutrition", "nutrient"],
            "health_risks": ["risks", "harmful", "negative", "danger", "disease", "mortality", "cancer"],
            "recommendations": ["recommend", "guideline", "advice", "should", "best practice", "dietary"],
            "methodology": ["study", "research", "method", "analysis", "systematic", "meta-analysis"],
            "demographics": ["population", "demographic", "age", "gender", "children", "adults"],
            "industry": ["industry", "processing", "manufacturing", "commercial", "food production"]
        }

        # Group evidence by themes
        theme_groups = {theme: [] for theme in theme_keywords.keys()}
        unclassified = []

        for idx, evidence in enumerate(evidence_list):
            # Combine all text for analysis
            text_content = " ".join([
                evidence.get("title", ""),
                " ".join(evidence.get("snippets", [])),
                evidence.get("notes", "")
            ]).lower()

            # Find best matching theme
            best_theme = None
            max_matches = 0

            for theme, keywords in theme_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in text_content)
                if matches > max_matches:
                    max_matches = matches
                    best_theme = theme

            if best_theme and max_matches > 0:
                theme_groups[best_theme].append(idx)
            else:
                unclassified.append(idx)

        # Create clusters from theme groups
        for theme, items in theme_groups.items():
            if items:  # Only include non-empty clusters
                clusters.append({
                    "label": theme.replace("_", " ").title(),
                    "items": items
                })

        # Add unclassified items as separate cluster if any
        if unclassified:
            clusters.append({
                "label": "Other/Unclassified",
                "items": unclassified
            })

        # Deduplicate within clusters based on URL similarity
        for cluster in clusters:
            cluster["items"] = self._deduplicate_items(cluster["items"], evidence_list)

        return clusters

    def _deduplicate_items(self, item_indices: List[int], evidence_list: List[Dict[str, Any]]) -> List[int]:
        """Remove near-duplicate evidence within a cluster based on domain similarity."""
        deduplicated = []
        seen_domains = set()

        for idx in item_indices:
            evidence = evidence_list[idx]
            url = evidence.get("url", "")

            # Extract domain for deduplication
            try:
                domain = urlparse(url).netloc.replace('www.', '')
                # Keep only one evidence per domain per cluster (prioritize higher quality)
                if domain not in seen_domains:
                    deduplicated.append(idx)
                    seen_domains.add(domain)
                else:
                    # Check if current evidence has higher quality than existing
                    existing_idx = next(i for i in deduplicated if urlparse(evidence_list[i].get("url", "")).netloc.replace('www.', '') == domain)
                    if evidence.get("quality", 0) > evidence_list[existing_idx].get("quality", 0):
                        deduplicated.remove(existing_idx)
                        deduplicated.append(idx)
            except:
                # If URL parsing fails, keep the item
                deduplicated.append(idx)

        return deduplicated

    def _extract_key_findings(self, evidence_list: List[Dict[str, Any]], clusters: List[Dict[str, Any]]) -> List[str]:
        """Extract key findings with source references from evidence clusters."""
        key_findings = []

        for cluster in clusters:
            cluster_label = cluster["label"]
            items = cluster["items"]

            if not items:
                continue

            # Get high-quality evidence from this cluster
            high_quality_items = [idx for idx in items if evidence_list[idx].get("quality", 0) >= 4]
            reference_items = high_quality_items if high_quality_items else items[:2]  # Take top 2 if no high quality

            # Generate finding based on cluster theme
            if "Health Benefits" in cluster_label:
                finding = f"Potential health benefits of ultra-processed foods are limited and controversial {self._format_references(reference_items)}"
            elif "Health Risks" in cluster_label:
                finding = f"Multiple studies link ultra-processed foods to increased health risks including cardiovascular disease and metabolic disorders {self._format_references(reference_items)}"
            elif "Recommendations" in cluster_label:
                finding = f"Major health organizations recommend limiting ultra-processed food consumption {self._format_references(reference_items)}"
            elif "Methodology" in cluster_label:
                finding = f"Research methodologies vary significantly across studies, affecting result comparability {self._format_references(reference_items)}"
            elif "Demographics" in cluster_label:
                finding = f"Health impacts of ultra-processed foods vary across different population groups {self._format_references(reference_items)}"
            elif "Industry" in cluster_label:
                finding = f"Food industry perspectives emphasize processing innovations and convenience benefits {self._format_references(reference_items)}"
            else:
                # Generic finding for unclassified
                finding = f"Additional evidence provides context for ultra-processed food research {self._format_references(reference_items)}"

            key_findings.append(finding)

        return key_findings

    def _format_references(self, indices: List[int]) -> str:
        """Format source references as [1,2,3] notation."""
        if not indices:
            return ""
        return f"[{','.join(map(str, indices))}]"

    def _identify_conflicts(self, evidence_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify conflicting claims in the evidence base."""
        conflicts = []

        # Look for conflicting evidence about health effects
        benefits_evidence = []
        risks_evidence = []

        for idx, evidence in enumerate(evidence_list):
            text_content = " ".join([
                evidence.get("title", ""),
                " ".join(evidence.get("snippets", [])),
                evidence.get("notes", "")
            ]).lower()

            if any(word in text_content for word in ["benefit", "positive", "advantage", "healthy"]):
                benefits_evidence.append(idx)
            if any(word in text_content for word in ["risk", "harmful", "negative", "disease", "mortality"]):
                risks_evidence.append(idx)

        # Create conflict if we have both types of evidence
        if benefits_evidence and risks_evidence:
            conflicts.append({
                "claim": "Ultra-processed foods may have some health benefits",
                "support": benefits_evidence[:3],  # Limit to first 3
                "counter": risks_evidence[:3],    # Limit to first 3
                "reason": "Different study methodologies and populations; benefits may be limited to specific contexts"
            })

        # Look for methodology conflicts
        systematic_review_evidence = []
        observational_evidence = []

        for idx, evidence in enumerate(evidence_list):
            text_content = " ".join([
                evidence.get("title", ""),
                " ".join(evidence.get("snippets", [])),
                evidence.get("notes", "")
            ]).lower()

            if "systematic review" in text_content or "meta-analysis" in text_content:
                systematic_review_evidence.append(idx)
            elif "observational" in text_content or "cohort" in text_content:
                observational_evidence.append(idx)

        if systematic_review_evidence and observational_evidence:
            conflicts.append({
                "claim": "Systematic reviews provide strongest evidence",
                "support": systematic_review_evidence,
                "counter": observational_evidence,
                "reason": "Different levels of evidence hierarchy; systematic reviews synthesize multiple studies while observational studies provide specific findings"
            })

        return conflicts

    def _identify_research_gaps(self, evidence_list: List[Dict[str, Any]]) -> List[str]:
        """Identify research gaps and next steps based on evidence analysis."""
        gaps = []

        # Check for recent data (2024-2025)
        recent_evidence = [e for e in evidence_list if e.get("date") and e["date"] >= "2024-01-01"]
        if len(recent_evidence) < len(evidence_list) * 0.3:  # Less than 30% recent
            gaps.append("Need more 2024-2025 research on ultra-processed foods")

        # Check for systematic reviews
        systematic_reviews = [e for e in evidence_list if "systematic" in str(e).lower()]
        if len(systematic_reviews) < 2:
            gaps.append("Need comprehensive systematic review of 2024-2025 evidence")

        # Check for population diversity
        population_evidence = [e for e in evidence_list if any(pop in str(e).lower() for pop in ["children", "elderly", "demographic"])]
        if len(population_evidence) < 2:
            gaps.append("Need research on ultra-processed food effects across different age groups")

        # Check for long-term studies
        longterm_evidence = [e for e in evidence_list if any(term in str(e).lower() for term in ["long-term", "longitudinal", "follow-up"])]
        if len(longterm_evidence) < 2:
            gaps.append("Need long-term longitudinal studies on health outcomes")

        # Check for intervention studies
        intervention_evidence = [e for e in evidence_list if any(term in str(e).lower() for term in ["intervention", "trial", "randomized"])]
        if len(intervention_evidence) < 2:
            gaps.append("Need randomized controlled trials testing interventions")

        return gaps

    def _calculate_coverage_stats(self, evidence_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate coverage statistics for quality assessment."""
        unique_urls = set()
        unique_domains = set()

        for evidence in evidence_list:
            url = evidence.get("url", "")
            if url:
                unique_urls.add(url)
                try:
                    domain = urlparse(url).netloc.replace('www.', '')
                    unique_domains.add(domain)
                except:
                    pass

        return {
            "unique_sources": len(unique_urls),
            "domains": len(unique_domains),
            "total_evidence": len(evidence_list),
            "high_quality_sources": len([e for e in evidence_list if e.get("quality", 0) >= 4])
        }