"""
Phase 4: Researcher Agent

Performs web searches and extracts clean evidence blocks.
Handles search query optimization, content extraction, and quality scoring.
"""

import re
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from dateutil import parser as date_parser
from ddgs import DDGS
import trafilatura


class ResearcherAgent:
    """
    Phase 4: Researcher - Perform web search and extract clean evidence blocks.

    Executes targeted web searches based on planner subqueries, extracts and
    cleans content from web sources, scores evidence quality, and identifies
    research gaps for comprehensive coverage.
    """

    def __init__(self):
        """Initialize the ResearcherAgent with HTTP session."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def research_subquery(self, subquery_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research for a single subquery from the planner.

        Performs web search with specified operators, extracts evidence from results,
        filters by quality threshold, and identifies research gaps.

        Args:
            subquery_obj: Single subquery object from planner containing:
                - subquery: Search terms
                - operators: Search operators (site:, filetype:, etc.)
                - k: Number of results to retrieve

        Returns:
            Evidence findings in structured format with:
            - subquery: Original search query
            - findings: List of evidence objects with quality scores
            - gaps: Identified research gaps
        """
        subquery = subquery_obj.get("subquery", "")
        operators = subquery_obj.get("operators", [])
        k = subquery_obj.get("k", 6)

        # Build search query with operators
        search_query = self._build_search_query(subquery, operators)

        # Perform web search
        raw_results = self._search_web(search_query, k)

        # Extract evidence from each result
        findings = []
        seen_urls = set()

        for result in raw_results:
            if result.get("href") in seen_urls:
                continue

            evidence = self._extract_evidence(result)
            if evidence and evidence["quality"] >= 2:  # Filter low quality results
                findings.append(evidence)
                seen_urls.add(evidence["url"])

        # Identify gaps
        gaps = self._identify_gaps(subquery, findings)

        return {
            "subquery": subquery,
            "findings": findings,
            "gaps": gaps
        }

    def _build_search_query(self, subquery: str, operators: List[str]) -> str:
        """Build final search query with operators for targeted search."""
        query_parts = [subquery]

        for operator in operators:
            query_parts.append(operator)

        return " ".join(query_parts)

    def _search_web(self, query: str, max_results: int = 6) -> List[Dict]:
        """Perform web search using DuckDuckGo with error handling."""
        try:
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                for result in search_results:
                    if isinstance(result, dict):
                        results.append(result)

            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _extract_evidence(self, search_result: Dict) -> Optional[Dict[str, Any]]:
        """
        Extract structured evidence from a search result.

        Processes search results to extract clean text, publication dates,
        publisher information, and quality scores for evidence assessment.
        """
        try:
            url = search_result.get("href", "")
            title = search_result.get("title", "")
            body = search_result.get("body", "")

            # Get full content
            content = self._fetch_content(url)
            if not content:
                content = body  # Fallback to search snippet

            # Extract date
            date = self._extract_date(content, url)

            # Extract publisher
            publisher = self._extract_publisher(url, content)

            # Extract quality snippets
            snippets = self._extract_snippets(content, body)

            # Calculate quality score
            quality = self._calculate_quality_score(url, publisher, content)

            # Generate notes
            notes = self._generate_notes(url, publisher, quality)

            return {
                "url": url,
                "title": title,
                "publisher": publisher,
                "date": date,
                "snippets": snippets,
                "quality": quality,
                "notes": notes
            }

        except Exception as e:
            print(f"Evidence extraction error: {e}")
            return None

    def _fetch_content(self, url: str) -> str:
        """Fetch and extract clean text content from URL using trafilatura."""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Use trafilatura for clean text extraction
                content = trafilatura.extract(response.text)
                return content[:5000] if content else ""  # Limit content length
        except:
            pass
        return ""

    def _extract_date(self, content: str, url: str) -> Optional[str]:
        """Extract publication date using multiple regex patterns."""
        try:
            # Common date patterns
            date_patterns = [
                r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
                r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b',
                r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b'
            ]

            for pattern in date_patterns:
                matches = re.findall(pattern, content[:1000], re.IGNORECASE)
                if matches:
                    try:
                        date_str = matches[0] if isinstance(matches[0], str) else " ".join(matches[0])
                        parsed_date = date_parser.parse(date_str)
                        return parsed_date.strftime("%Y-%m-%d")
                    except:
                        continue

            return None
        except:
            return None

    def _extract_publisher(self, url: str, content: str) -> str:
        """Extract publisher from URL and content with known publisher mappings."""
        try:
            domain = urlparse(url).netloc.replace('www.', '')

            # Known publishers mapping
            publisher_mapping = {
                'pubmed.ncbi.nlm.nih.gov': 'PubMed',
                'cochranelibrary.com': 'Cochrane Library',
                'who.int': 'World Health Organization',
                'fda.gov': 'FDA',
                'nhtsa.gov': 'NHTSA',
                'dot.gov': 'US Department of Transportation',
                'ieee.org': 'IEEE',
                'sae.org': 'SAE International',
                'foodnavigator.com': 'Food Navigator'
            }

            if domain in publisher_mapping:
                return publisher_mapping[domain]
            else:
                return domain.split('.')[0].capitalize()

        except:
            return "Unknown"

    def _extract_snippets(self, content: str, fallback: str) -> List[str]:
        """Extract relevant text snippets from content for evidence summary."""
        try:
            text = content if content else fallback
            if not text:
                return []

            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

            # Take first few meaningful sentences
            snippets = []
            for sentence in sentences[:5]:
                if len(sentence) > 30 and len(sentence) < 300:
                    snippets.append(sentence)
                    if len(snippets) >= 3:
                        break

            return snippets[:3]  # Limit to 3 snippets

        except:
            return [fallback[:200]] if fallback else []

    def _calculate_quality_score(self, url: str, publisher: str, content: str) -> int:
        """
        Calculate quality score 0-5 based on source credibility rubric.

        Scoring criteria:
        5: official/gov/peer-reviewed with clear methodology
        4: reputable media/industry report with data
        3: credible blog/company post with some data
        2: opinion/no data
        1: low credibility/aggregator
        """
        score = 1  # Default low score

        domain = urlparse(url).netloc.lower()
        content_lower = content.lower() if content else ""

        # Score 5: Official/gov/peer-reviewed
        if any(domain.endswith(gov) for gov in ['.gov', '.org']) or \
           any(site in domain for site in ['pubmed', 'cochrane', 'who.int', 'fda.gov']):
            score = 5

        # Score 4: Reputable media/industry
        elif any(site in domain for site in ['reuters.com', 'bbc.com', 'nature.com', 'science.org', 'ieee.org']):
            score = 4

        # Score 3: Credible sources with data
        elif any(keyword in content_lower for keyword in ['study', 'research', 'data', 'analysis']):
            score = 3

        # Boost for methodology indicators
        if any(method in content_lower for method in ['methodology', 'methods', 'systematic review', 'meta-analysis']):
            score = min(5, score + 1)

        # Penalty for low credibility indicators
        if any(indicator in domain for indicator in ['aggregator', 'blog', 'forum']):
            score = max(1, score - 1)

        return score

    def _generate_notes(self, url: str, publisher: str, quality: int) -> str:
        """Generate explanatory notes for the evidence quality assessment."""
        if quality >= 5:
            return f"High-quality {publisher} source with authoritative content"
        elif quality >= 4:
            return f"Reputable {publisher} source with data-driven content"
        elif quality >= 3:
            return f"Credible {publisher} source with some supporting evidence"
        elif quality >= 2:
            return f"Opinion-based content from {publisher}"
        else:
            return f"Low credibility source from {publisher}"

    def _identify_gaps(self, subquery: str, findings: List[Dict]) -> List[str]:
        """Identify research gaps based on search findings for quality assessment."""
        gaps = []

        if len(findings) < 3:
            gaps.append("Insufficient search results found")

        # Check for recent data
        recent_count = sum(1 for f in findings if f.get("date") and f["date"] >= "2024-01-01")
        if recent_count < 2:
            gaps.append("Limited recent data (post-2024)")

        # Check for high-quality sources
        high_quality_count = sum(1 for f in findings if f.get("quality", 0) >= 4)
        if high_quality_count < 2:
            gaps.append("Few high-quality peer-reviewed sources")

        # Topic-specific gaps
        if "systematic review" in subquery.lower() and not any("systematic" in str(f) for f in findings):
            gaps.append("No systematic reviews found")

        if "rct" in subquery.lower() or "randomized" in subquery.lower():
            if not any("randomized" in str(f).lower() for f in findings):
                gaps.append("Missing randomized controlled trials")

        return gaps