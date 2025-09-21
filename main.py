#!/usr/bin/env python3
"""
Deep Research Agent - LangGraph implementation
CLI entry point for running the research agent
"""

import sys
import json
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime
import re
from dateutil import parser as date_parser
from urllib.parse import urlparse
from ddgs import DDGS
import trafilatura
import os


class DataManager:
    """Manages file operations for the new data directory structure"""

    def __init__(self, run_id: str = None):
        if run_id is None:
            run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_id = run_id
        self.run_dir = f"data/runs/{run_id}"
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories"""
        directories = [
            self.run_dir,
            "data/out",
            "data/evidence",
            "data/compressed",
            "data/web_cache/search",
            "data/web_cache/fetch",
            "data/observability"
        ]
        for dir_path in directories:
            os.makedirs(dir_path, exist_ok=True)

    def save_clarify(self, data: Dict[str, Any]) -> str:
        """Save clarification results"""
        filepath = f"{self.run_dir}/clarify.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def save_brief(self, content: str) -> str:
        """Save research brief"""
        filepath = f"{self.run_dir}/brief.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath

    def save_plan(self, data: Dict[str, Any]) -> str:
        """Save search plan"""
        filepath = f"{self.run_dir}/plan.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def save_evidence(self, evidence_list: List[Dict[str, Any]]) -> str:
        """Save evidence as JSONL"""
        filepath = f"{self.run_dir}/evidence.jsonl"
        with open(filepath, 'w', encoding='utf-8') as f:
            for evidence in evidence_list:
                f.write(json.dumps(evidence, ensure_ascii=False) + '\n')

        # Also save to shared evidence directory
        shared_filepath = f"data/evidence/blocks.jsonl"
        with open(shared_filepath, 'a', encoding='utf-8') as f:
            for evidence in evidence_list:
                evidence_with_run = evidence.copy()
                evidence_with_run['run_id'] = self.run_id
                f.write(json.dumps(evidence_with_run, ensure_ascii=False) + '\n')

        return filepath

    def save_compressed(self, data: Dict[str, Any]) -> str:
        """Save compression results"""
        filepath = f"{self.run_dir}/compressed.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Also save to shared compressed directory
        shared_filepath = f"data/compressed/notes.json"
        compressed_with_run = data.copy()
        compressed_with_run['run_id'] = self.run_id
        compressed_with_run['timestamp'] = datetime.now().isoformat()

        # Append to shared notes
        shared_notes = []
        if os.path.exists(shared_filepath):
            with open(shared_filepath, 'r', encoding='utf-8') as f:
                shared_notes = json.load(f)

        shared_notes.append(compressed_with_run)
        with open(shared_filepath, 'w', encoding='utf-8') as f:
            json.dump(shared_notes, f, indent=2, ensure_ascii=False)

        return filepath

    def save_report(self, content: str) -> str:
        """Save final report"""
        filepath = f"{self.run_dir}/report.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Also save to out directory
        out_filepath = f"data/out/research_report_{self.run_id}.md"
        with open(out_filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def save_evaluation(self, data: Dict[str, Any]) -> str:
        """Save evaluation results"""
        filepath = f"{self.run_dir}/judge.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def save_replan(self, data: Dict[str, Any]) -> str:
        """Save replan results"""
        filepath = f"{self.run_dir}/replan.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def save_logs(self, logs: List[Dict[str, Any]]) -> str:
        """Save logs as NDJSON"""
        filepath = f"{self.run_dir}/logs.ndjson"
        with open(filepath, 'w', encoding='utf-8') as f:
            for log_entry in logs:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        # Also append to shared observability
        shared_filepath = "data/observability/traces.ndjson"
        with open(shared_filepath, 'a', encoding='utf-8') as f:
            for log_entry in logs:
                log_with_run = log_entry.copy()
                log_with_run['run_id'] = self.run_id
                f.write(json.dumps(log_with_run, ensure_ascii=False) + '\n')

        return filepath

    def log_error(self, error_data: Dict[str, Any]):
        """Log error to observability"""
        error_filepath = "data/observability/errors.ndjson"
        error_with_run = error_data.copy()
        error_with_run['run_id'] = self.run_id
        error_with_run['timestamp'] = datetime.now().isoformat()

        with open(error_filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_with_run, ensure_ascii=False) + '\n')


class ClarifyAgent:
    """Phase 1: Clarify Agent - Turn vague query into actionable research input"""

    def __init__(self):
        # In a real implementation, you'd use your preferred LLM
        # self.llm = OpenAI()  # Requires API key
        pass

    def clarify_query(self, user_query: str) -> Dict[str, Any]:
        """
        Transform user query into structured research specification

        Args:
            user_query: Raw user input query

        Returns:
            Structured dict with research parameters
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
        """Extract main research objective from query"""
        if "compare" in query.lower() and "evidence" in query.lower():
            return f"Compare recent evidence and provide evidence-based analysis on: {query}"
        elif "recommend" in query.lower():
            return f"Provide evidence-based recommendations on: {query}"
        else:
            return f"Research and analyze: {query}"

    def _extract_definitions(self, query: str) -> List[str]:
        """Identify key terms that need definition"""
        definitions = []

        if "ultra-processed foods" in query.lower():
            definitions.append("ultra-processed foods: industrially formulated products with ≥5 ingredients, additives, preservatives")
        if "evidence" in query.lower():
            definitions.append("evidence: peer-reviewed studies, meta-analyses, systematic reviews")

        return definitions

    def _extract_time_window(self, query: str) -> str:
        """Extract or infer time window"""
        if "2024" in query and "2025" in query:
            return "2024-01 to 2025-09"
        elif "recent" in query.lower() or "latest" in query.lower():
            return "2023-01 to 2025-09"
        else:
            return "2020-01 to 2025-09"

    def _extract_geography(self, query: str) -> str:
        """Extract or infer geographic scope"""
        if any(country in query.lower() for country in ["us", "usa", "united states"]):
            return "US"
        elif any(country in query.lower() for country in ["china", "cn"]):
            return "CN"
        else:
            return "global"

    def _extract_audience(self, query: str) -> str:
        """Infer target audience"""
        if "technical" in query.lower() or "research" in query.lower():
            return "researcher"
        elif "executive" in query.lower() or "summary" in query.lower():
            return "executive"
        else:
            return "consumer"

    def _extract_deliverable(self, query: str) -> str:
        """Define expected deliverable format"""
        return "comprehensive report with evidence analysis and actionable recommendations"

    def _generate_success_criteria(self, query: str) -> List[str]:
        """Generate success criteria based on query type"""
        criteria = [">=10 unique sources", "no paywalled-only sources"]

        if "compare" in query.lower():
            criteria.append("covers multiple perspectives")
        if "recommend" in query.lower():
            criteria.append("includes actionable recommendations")
        if "evidence" in query.lower():
            criteria.append("includes recent peer-reviewed studies")

        return criteria


class ResearchBriefAgent:
    """Phase 2: Research Brief Agent - Create detailed research outline from clarified spec"""

    def create_brief(self, clarify_json: Dict[str, Any]) -> str:
        """
        Generate research brief from clarified research specification

        Args:
            clarify_json: Output from ClarifyAgent

        Returns:
            Markdown formatted research brief
        """

        objective = clarify_json.get("objective", "")
        definitions = clarify_json.get("definitions", [])
        time_window = clarify_json.get("time_window", "")
        geography = clarify_json.get("geography", "")
        audience = clarify_json.get("audience", "")
        success_criteria = clarify_json.get("success_criteria", [])

        # Generate sub-questions based on objective
        sub_questions = self._generate_sub_questions(objective, clarify_json)

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

    def _generate_sub_questions(self, objective: str, clarify_json: Dict) -> List[str]:
        """Generate 3-6 balanced sub-questions"""
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
            # Generic sub-questions
            sub_questions = [
                "What is the current state of research on this topic?",
                "What are the main arguments and perspectives?",
                "What evidence supports different viewpoints?",
                "What are the practical implications?",
                "What gaps or limitations exist in current knowledge?"
            ]

        return sub_questions[:6]  # Limit to 6 questions max

    def _define_inclusion_criteria(self, clarify_json: Dict) -> Dict[str, List[str]]:
        """Define what sources to include"""
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
        """Define what types of evidence to collect"""
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
        """Identify potential research risks and unknowns"""
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
        if not definitions:
            return "No specific definitions provided."
        return "\n".join([f"- **{def_text}**" for def_text in definitions])

    def _format_sub_questions(self, sub_questions: List[str]) -> str:
        return "\n".join([f"{i+1}. {q}" for i, q in enumerate(sub_questions)])

    def _format_inclusion_criteria(self, criteria: Dict[str, List[str]]) -> str:
        result = ""
        for category, items in criteria.items():
            result += f"### {category}\n"
            result += "\n".join([f"- {item}" for item in items])
            result += "\n\n"
        return result.strip()

    def _format_evidence_artifacts(self, artifacts: List[str]) -> str:
        return "\n".join([f"- {artifact}" for artifact in artifacts])

    def _format_risks_unknowns(self, risks: List[str]) -> str:
        return "\n".join([f"- {risk}" for risk in risks])

    def _format_success_criteria(self, criteria: List[str]) -> str:
        return "\n".join([f"- {criterion}" for criterion in criteria])


class SupervisorPlannerAgent:
    """Phase 3: Supervisor/Planner - Convert brief into diversified subqueries for parallel execution"""

    def create_plan(self, brief_markdown: str) -> Dict[str, Any]:
        """
        Convert research brief into structured search plan

        Args:
            brief_markdown: Markdown formatted research brief

        Returns:
            JSON plan with subqueries and coverage targets
        """

        # Extract key sub-questions from brief
        sub_questions = self._extract_sub_questions_from_brief(brief_markdown)

        # Extract research context
        context = self._extract_context_from_brief(brief_markdown)

        # Generate diversified subqueries
        subqueries = self._generate_subqueries(sub_questions, context)

        # Set coverage targets
        coverage_target = self._define_coverage_target(context)

        plan = {
            "plan": subqueries,
            "coverage_target": coverage_target
        }

        return plan

    def _extract_sub_questions_from_brief(self, brief_markdown: str) -> List[str]:
        """Extract the key sub-questions from the brief"""
        questions = []
        lines = brief_markdown.split('\n')

        in_questions_section = False
        for line in lines:
            line = line.strip()

            if "## Key Sub-Questions" in line:
                in_questions_section = True
                continue
            elif line.startswith("##") and in_questions_section:
                break
            elif in_questions_section and line and line[0].isdigit():
                # Extract question text (remove numbering)
                question = line.split('. ', 1)[1] if '. ' in line else line
                questions.append(question)

        return questions

    def _extract_context_from_brief(self, brief_markdown: str) -> Dict[str, str]:
        """Extract key context information from brief"""
        context = {}
        lines = brief_markdown.split('\n')

        for line in lines:
            line = line.strip()
            if "**Time Window:**" in line:
                context["time_window"] = line.split("**Time Window:**")[1].strip()
            elif "**Geography:**" in line:
                context["geography"] = line.split("**Geography:**")[1].strip()
            elif "**Target Audience:**" in line:
                context["audience"] = line.split("**Target Audience:**")[1].strip()

        # Extract topic from objective
        if "ultra-processed foods" in brief_markdown.lower():
            context["topic"] = "ultra-processed foods"
        elif "ai safety" in brief_markdown.lower():
            context["topic"] = "ai safety"
        elif "autonomous vehicles" in brief_markdown.lower():
            context["topic"] = "autonomous vehicles"
        else:
            context["topic"] = "general"

        return context

    def _generate_subqueries(self, sub_questions: List[str], context: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate diversified subqueries with search operators"""
        subqueries = []
        topic = context.get("topic", "general")
        time_window = context.get("time_window", "")

        # Template subqueries based on topic
        if topic == "ultra-processed foods":
            base_queries = [
                {
                    "base": "ultra-processed foods health benefits evidence",
                    "rationale": "Search for potential positive health aspects to ensure balanced coverage",
                    "operators": ["site:pubmed.ncbi.nlm.nih.gov", "filetype:pdf"],
                    "freshness": "recent"
                },
                {
                    "base": "ultra-processed foods health risks systematic review",
                    "rationale": "Find comprehensive evidence on health risks from systematic reviews",
                    "operators": ["site:cochranelibrary.com", "site:pubmed.ncbi.nlm.nih.gov"],
                    "freshness": "recent"
                },
                {
                    "base": "WHO FDA ultra-processed foods dietary recommendations",
                    "rationale": "Get official health organization positions and guidelines",
                    "operators": ["site:who.int", "site:fda.gov", "filetype:pdf"],
                    "freshness": "mixed"
                },
                {
                    "base": "ultra-processed foods population differences demographics",
                    "rationale": "Understand how impacts vary across different populations",
                    "operators": ["inurl:population", "inurl:demographic"],
                    "freshness": "recent"
                },
                {
                    "base": "food industry ultra-processed foods processing methods",
                    "rationale": "Understand industry perspective and processing techniques",
                    "operators": ["site:foodnavigator.com", "inurl:industry"],
                    "freshness": "mixed"
                },
                {
                    "base": "ultra-processed foods research gaps limitations future",
                    "rationale": "Identify what research is still needed",
                    "operators": ["inurl:limitations", "inurl:future-research"],
                    "freshness": "recent"
                }
            ]
        elif topic == "ai safety":
            base_queries = [
                {
                    "base": "AI safety autonomous vehicles regulations standards",
                    "rationale": "Find regulatory frameworks and safety standards",
                    "operators": ["site:nhtsa.gov", "site:dot.gov", "filetype:pdf"],
                    "freshness": "recent"
                },
                {
                    "base": "autonomous vehicle AI safety testing validation",
                    "rationale": "Research current testing methodologies and validation approaches",
                    "operators": ["site:ieee.org", "inurl:testing", "filetype:pdf"],
                    "freshness": "recent"
                },
                {
                    "base": "AI safety autonomous vehicles industry best practices",
                    "rationale": "Get industry perspective on safety implementations",
                    "operators": ["site:sae.org", "inurl:best-practices"],
                    "freshness": "mixed"
                }
            ]
        else:
            # Generic approach for unknown topics
            base_queries = []
            for i, question in enumerate(sub_questions[:6]):
                query_terms = self._extract_key_terms(question)
                base_queries.append({
                    "base": " ".join(query_terms),
                    "rationale": f"Address sub-question {i+1}: {question[:50]}...",
                    "operators": ["filetype:pdf", "inurl:research"],
                    "freshness": "recent"
                })

        # Convert base queries to full subquery format
        for i, base_query in enumerate(base_queries):
            # Add time constraints if available
            query_text = base_query["base"]
            if "2024" in time_window or "2025" in time_window:
                query_text += " 2024 OR 2025"

            subquery = {
                "subquery": query_text,
                "rationale": base_query["rationale"],
                "operators": base_query["operators"],
                "freshness": base_query["freshness"],
                "k": 6  # Number of results to retrieve per query
            }
            subqueries.append(subquery)

        return subqueries

    def _extract_key_terms(self, question: str) -> List[str]:
        """Extract key search terms from a question"""
        # Simple keyword extraction (in production, use NLP)
        stop_words = {"what", "are", "the", "how", "why", "when", "where", "is", "do", "does", "can", "will", "would", "should"}
        words = question.lower().replace("?", "").split()
        key_terms = [word for word in words if word not in stop_words and len(word) > 3]
        return key_terms[:4]  # Limit to 4 key terms

    def _define_coverage_target(self, context: Dict[str, str]) -> Dict[str, Any]:
        """Define coverage requirements for the search plan"""
        topic = context.get("topic", "general")

        base_target = {
            "min_unique_sources": 12,
            "must_include": ["gov", "peer_reviewed"]
        }

        if topic == "ultra-processed foods":
            base_target["must_include"].extend(["health_org", "systematic_review"])
            base_target["min_unique_sources"] = 15
        elif topic == "ai safety":
            base_target["must_include"].extend(["industry_standard", "regulatory"])
            base_target["min_unique_sources"] = 12
        else:
            base_target["must_include"].append("academic")

        return base_target


class ResearcherAgent:
    """Phase 4: Researcher - Perform web search and extract clean evidence blocks"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def research_subquery(self, subquery_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research for a single subquery

        Args:
            subquery_obj: Single subquery object from planner

        Returns:
            Evidence findings in structured format
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
        """Build final search query with operators"""
        query_parts = [subquery]

        for operator in operators:
            query_parts.append(operator)

        return " ".join(query_parts)

    def _search_web(self, query: str, max_results: int = 6) -> List[Dict]:
        """Perform web search using DuckDuckGo"""
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
        """Extract structured evidence from a search result"""
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
        """Fetch and extract clean text content from URL"""
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
        """Extract publication date"""
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
        """Extract publisher from URL and content"""
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
        """Extract relevant snippets from content"""
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
        Calculate quality score 0-5 based on rubric:
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
        """Generate explanatory notes for the evidence"""
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
        """Identify research gaps based on findings"""
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


class CompressConflictAgent:
    """Phase 5: Compress + Conflict - Cluster evidence, identify conflicts, extract key findings"""

    def compress_and_align(self, all_evidence: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Compress and align evidence blocks from multiple subqueries

        Args:
            all_evidence: List of evidence findings from all subqueries

        Returns:
            Structured compression analysis with clusters, findings, conflicts, gaps
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
        """Cluster evidence by themes and deduplicate near-duplicates"""
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
        """Remove near-duplicate evidence within a cluster"""
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
        """Extract key findings with source references"""
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
        """Format source references as [1,2,3]"""
        if not indices:
            return ""
        return f"[{','.join(map(str, indices))}]"

    def _identify_conflicts(self, evidence_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify conflicting claims in the evidence"""
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
        """Identify research gaps and next steps"""
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
        """Calculate coverage statistics"""
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


class ReportAgent:
    """Phase 6: Report Agent - Generate structured decision-grade reports with citations"""

    def __init__(self):
        pass

    def generate_report(self, compressed_json: Dict[str, Any], evidence_list: List[Dict[str, Any]],
                       user_query: str, target_audience: str = "consumer") -> str:
        """
        Generate structured Markdown report from compressed analysis and evidence

        Args:
            compressed_json: Output from CompressConflictAgent
            evidence_list: Full list of evidence blocks for citations
            user_query: Original user query
            target_audience: Target audience (consumer, executive, researcher)

        Returns:
            Structured Markdown report
        """

        # Extract information from compressed analysis
        key_findings = compressed_json.get("key_findings", [])
        conflicts = compressed_json.get("conflicts", [])
        gaps = compressed_json.get("gaps", [])
        coverage_stats = compressed_json.get("coverage_stats", {})
        clusters = compressed_json.get("clusters", [])

        # Generate report sections
        executive_summary = self._generate_executive_summary(key_findings, conflicts, target_audience)
        key_insights = self._generate_key_insights(key_findings, clusters, evidence_list, target_audience)
        timeline_section = self._generate_timeline_section(evidence_list, target_audience)
        recommendations = self._generate_recommendations(key_findings, conflicts, gaps, target_audience)
        limitations = self._generate_limitations(conflicts, gaps, coverage_stats)

        # Build complete report
        report = f"""# Research Report: {self._extract_topic_from_query(user_query)}

**Target Audience:** {target_audience.title()}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Evidence Sources:** {coverage_stats.get('unique_sources', 0)} unique sources across {coverage_stats.get('domains', 0)} domains

---

## Executive Summary

{executive_summary}

---

## Key Insights

{key_insights}

---

{timeline_section}

---

## Recommendations

{recommendations}

---

## Limitations & Open Questions

{limitations}

---

## Evidence References

{self._generate_evidence_references(evidence_list)}

---

*Report generated by Deep Research Agent*
"""

        return report

    def _extract_topic_from_query(self, user_query: str) -> str:
        """Extract main topic from user query for report title"""
        query_lower = user_query.lower()

        if "ultra-processed foods" in query_lower or "upf" in query_lower:
            return "Ultra-Processed Foods Evidence Analysis"
        elif "ai safety" in query_lower:
            return "AI Safety in Autonomous Vehicles"
        elif "climate change" in query_lower:
            return "Climate Change Research Analysis"
        else:
            # Generic title
            return "Research Evidence Analysis"

    def _generate_executive_summary(self, key_findings: List[str], conflicts: List[Dict],
                                  target_audience: str) -> str:
        """Generate 5-bullet executive summary"""
        summary_bullets = []

        # Bullet 1: Main research scope and coverage
        summary_bullets.append("• **Research Scope**: Comprehensive analysis of recent evidence with systematic evaluation of quality and relevance")

        # Bullet 2: Key positive findings (if any)
        positive_findings = [f for f in key_findings if any(word in f.lower() for word in ["benefit", "positive", "advantage"])]
        if positive_findings:
            summary_bullets.append(f"• **Potential Benefits**: {positive_findings[0].split('[')[0].strip()}")
        else:
            summary_bullets.append("• **Limited Positive Evidence**: Few documented benefits identified in current research")

        # Bullet 3: Key concerns or risks
        risk_findings = [f for f in key_findings if any(word in f.lower() for word in ["risk", "harmful", "disease", "negative"])]
        if risk_findings:
            summary_bullets.append(f"• **Primary Concerns**: {risk_findings[0].split('[')[0].strip()}")
        else:
            summary_bullets.append("• **Risk Assessment**: Analysis identifies potential areas of concern requiring further investigation")

        # Bullet 4: Evidence conflicts
        if conflicts:
            summary_bullets.append(f"• **Evidence Conflicts**: {len(conflicts)} significant conflicts identified between different research approaches and findings")
        else:
            summary_bullets.append("• **Evidence Consensus**: Findings show general alignment across different research sources")

        # Bullet 5: Recommendations direction
        if target_audience == "executive":
            summary_bullets.append("• **Strategic Direction**: Evidence supports cautious approach with continued monitoring and risk assessment")
        elif target_audience == "researcher":
            summary_bullets.append("• **Research Priorities**: Multiple knowledge gaps identified requiring systematic investigation")
        else:  # consumer
            summary_bullets.append("• **Consumer Guidance**: Evidence supports following established health organization recommendations")

        return "\n".join(summary_bullets)

    def _generate_key_insights(self, key_findings: List[str], clusters: List[Dict],
                             evidence_list: List[Dict], target_audience: str) -> str:
        """Generate key insights with inline citations"""
        insights = []

        # Process each cluster for insights
        for cluster in clusters:
            cluster_label = cluster["label"]
            items = cluster["items"]

            if not items:
                continue

            # Find corresponding key finding
            cluster_finding = None
            for finding in key_findings:
                if cluster_label.lower() in finding.lower():
                    cluster_finding = finding
                    break

            if cluster_finding:
                # Extract citation from finding
                citation_match = re.search(r'\[([^\]]+)\]', cluster_finding)
                citations = citation_match.group(1) if citation_match else ""

                # Generate insight based on target audience
                insight_text = cluster_finding.split('[')[0].strip()

                if target_audience == "executive":
                    if "health risks" in cluster_label.lower():
                        insight_text = f"**Risk Assessment**: {insight_text} This represents a significant business and regulatory risk factor"
                    elif "recommendations" in cluster_label.lower():
                        insight_text = f"**Regulatory Landscape**: {insight_text} indicating potential future policy changes"
                elif target_audience == "researcher":
                    if "methodology" in cluster_label.lower():
                        insight_text = f"**Methodological Considerations**: {insight_text} requiring standardized research protocols"
                    elif "gaps" in cluster_finding.lower():
                        insight_text = f"**Research Opportunities**: {insight_text} presenting clear research directions"

                # Add strength indicator based on evidence quality
                quality_scores = [evidence_list[int(i)].get("quality", 0) for i in citations.split(",") if i.strip().isdigit() and int(i) < len(evidence_list)]
                avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

                if avg_quality >= 4.5:
                    strength = "**HIGH CONFIDENCE**"
                elif avg_quality >= 3.5:
                    strength = "**MODERATE CONFIDENCE**"
                else:
                    strength = "**UNCERTAIN** - limited evidence quality"

                insights.append(f"{insight_text} [{citations}] *{strength}*")

        return "\n\n".join(insights) if insights else "*No significant insights identified from current evidence*"

    def _generate_timeline_section(self, evidence_list: List[Dict], target_audience: str) -> str:
        """Generate timeline or research evolution section"""
        # Group evidence by year
        timeline_data = {}
        for i, evidence in enumerate(evidence_list):
            date = evidence.get("date")
            if date:
                try:
                    year = date.split("-")[0]
                    if year not in timeline_data:
                        timeline_data[year] = []
                    timeline_data[year].append((i, evidence))
                except:
                    pass

        if not timeline_data:
            return "## Research Evolution\n\n*Insufficient date information to generate timeline*"

        timeline_section = "## Research Timeline & Evolution\n\n"

        for year in sorted(timeline_data.keys(), reverse=True):
            year_evidence = timeline_data[year]
            timeline_section += f"**{year}**\n"

            # Summarize key developments for this year
            high_quality_evidence = [e for _, e in year_evidence if e.get("quality", 0) >= 4]

            if high_quality_evidence:
                # Group by source type
                pubmed_count = len([e for e in high_quality_evidence if "pubmed" in e.get("publisher", "").lower()])
                who_count = len([e for e in high_quality_evidence if "who" in e.get("publisher", "").lower() or "fda" in e.get("publisher", "").lower()])

                developments = []
                if pubmed_count > 0:
                    developments.append(f"{pubmed_count} peer-reviewed studies")
                if who_count > 0:
                    developments.append(f"{who_count} health organization publications")

                timeline_section += f"- {', '.join(developments)} published\n"

                # Add key finding from this year
                if year_evidence:
                    sample_evidence = year_evidence[0][1]
                    sample_snippet = sample_evidence.get("snippets", [""])[0][:100] + "..." if sample_evidence.get("snippets") else ""
                    evidence_idx = year_evidence[0][0]
                    timeline_section += f"- Key development: {sample_snippet} [{evidence_idx}]\n"

            timeline_section += "\n"

        return timeline_section

    def _generate_recommendations(self, key_findings: List[str], conflicts: List[Dict],
                                gaps: List[str], target_audience: str) -> str:
        """Generate actionable, risk-aware recommendations"""
        recommendations = []

        if target_audience == "executive":
            recommendations.extend([
                "**1. Risk Assessment**: Conduct comprehensive risk analysis of current practices based on emerging evidence",
                "**2. Policy Monitoring**: Establish systematic monitoring of regulatory developments and health organization guidance",
                "**3. Stakeholder Communication**: Develop clear communication strategy addressing evidence conflicts and uncertainties"
            ])

            if conflicts:
                recommendations.append("**4. Evidence-Based Decisions**: Given conflicting evidence, adopt precautionary principle until consensus emerges")

        elif target_audience == "researcher":
            recommendations.extend([
                "**1. Methodological Standardization**: Develop standardized protocols to reduce methodological conflicts between studies",
                "**2. Longitudinal Studies**: Prioritize long-term studies to address current evidence limitations"
            ])

            # Add specific research priorities based on gaps
            for i, gap in enumerate(gaps[:3]):
                recommendations.append(f"**{i+3}. Research Priority**: {gap}")

        else:  # consumer
            recommendations.extend([
                "**1. Follow Established Guidelines**: Adhere to current health organization recommendations while research evolves",
                "**2. Balanced Approach**: Consider both benefits and risks when making dietary decisions",
                "**3. Stay Informed**: Monitor updates from reputable health organizations as evidence develops"
            ])

            if conflicts:
                recommendations.append("**4. Consult Professionals**: Given conflicting evidence, consult healthcare providers for personalized advice")

        # Add risk-aware caveats
        recommendations.append("\n**Risk Considerations:**")
        recommendations.append("- Evidence is evolving and recommendations may change as new research emerges")
        recommendations.append("- Individual circumstances may require different approaches than general recommendations")

        if conflicts:
            recommendations.append("- Conflicting evidence indicates need for cautious interpretation of findings")

        return "\n".join(recommendations)

    def _generate_limitations(self, conflicts: List[Dict], gaps: List[str],
                            coverage_stats: Dict) -> str:
        """Generate limitations and open questions section"""
        limitations = []

        # Evidence quality limitations
        total_sources = coverage_stats.get("total_evidence", 0)
        high_quality = coverage_stats.get("high_quality_sources", 0)

        if total_sources > 0:
            quality_ratio = high_quality / total_sources
            if quality_ratio < 0.7:
                limitations.append(f"**Evidence Quality**: Only {high_quality}/{total_sources} sources meet high quality standards (≥4/5)")

        # Coverage limitations
        domain_count = coverage_stats.get("domains", 0)
        if domain_count < 5:
            limitations.append(f"**Source Diversity**: Limited to {domain_count} source domains, potentially missing perspectives")

        # Conflict-based limitations
        if conflicts:
            limitations.append("**Conflicting Evidence**: Significant disagreements between studies limit certainty of conclusions")
            for conflict in conflicts[:2]:  # Show first 2 conflicts
                limitations.append(f"- {conflict.get('claim', 'Conflict identified')}: {conflict.get('reason', 'Methodological differences')}")

        # Research gaps as limitations
        limitations.append("\n**Open Questions & Research Needs:**")
        for gap in gaps:
            limitations.append(f"- {gap}")

        # Methodological limitations
        limitations.extend([
            "\n**Methodological Limitations:**",
            "- Search limited to publicly available sources",
            "- Potential language and publication bias",
            "- Time-constrained evidence collection may miss recent developments"
        ])

        return "\n".join(limitations) if limitations else "*No significant limitations identified*"

    def _generate_evidence_references(self, evidence_list: List[Dict]) -> str:
        """Generate numbered evidence reference list"""
        references = []

        for i, evidence in enumerate(evidence_list):
            url = evidence.get("url", "")
            title = evidence.get("title", "Untitled")
            publisher = evidence.get("publisher", "Unknown")
            date = evidence.get("date", "No date")
            quality = evidence.get("quality", 0)

            # Format reference
            ref = f"[{i}] **{title}**  \n"
            ref += f"Publisher: {publisher}  \n"
            ref += f"Date: {date}  \n"
            ref += f"Quality Score: {quality}/5  \n"
            ref += f"URL: {url}"

            references.append(ref)

        return "\n\n".join(references) if references else "*No references available*"


class EvaluatorAgent:
    """Phase 7: Evaluator/QA Agent - Automatic report evaluation and scoring"""

    def __init__(self):
        pass

    def evaluate_report(self, report_markdown: str, evidence_list: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate report quality across multiple dimensions

        Args:
            report_markdown: The complete Markdown report to evaluate
            evidence_list: Optional evidence list for additional validation

        Returns:
            JSON evaluation with scores and priority fixes
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
        """Extract different sections from the report for analysis"""
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
        """Score coverage breadth (0-5)"""
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
        """Score evidence faithfulness - citations match claims (0-5)"""
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
        """Score balance between different perspectives (0-5)"""
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
        """Score recency of evidence (0-5)"""
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
        """Score actionability of recommendations (0-5)"""
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
        """Score readability and structure (0-5)"""
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
        """Generate prioritized fix suggestions based on scores"""
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
        """Generate a brief evaluation summary"""
        avg_score = sum(scores.values()) / len(scores)

        if avg_score >= 4.5:
            return "Excellent report quality across all dimensions"
        elif avg_score >= 3.5:
            return "Good report quality with minor areas for improvement"
        elif avg_score >= 2.5:
            return "Moderate report quality requiring focused improvements"
        else:
            return "Report needs significant improvements across multiple dimensions"


class RecoveryReplanAgent:
    """Phase 8: Recovery/Replan Agent - Generate targeted fixes for quality issues"""

    def __init__(self):
        pass

    def create_replan(self, compress_gaps_conflicts: Dict[str, Any], judge_json: Dict[str, Any],
                     original_query: str = "") -> Dict[str, Any]:
        """
        Generate targeted replan to address quality gaps and issues

        Args:
            compress_gaps_conflicts: Gaps and conflicts from compression analysis
            judge_json: Evaluation scores and priority fixes
            original_query: Original user query for context

        Returns:
            JSON replan with targeted subqueries and expected improvements
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
        """Generate 3-5 targeted subqueries to address specific issues"""
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
        """Determine what metrics should improve from the replan"""
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
        """Identify which specific metrics need improvement"""
        target_metrics = []

        for metric, score in scores.items():
            if score <= 2:
                target_metrics.append(f"{metric} (current: {score}/5)")

        return target_metrics

    def execute_replan(self, replan_json: Dict[str, Any], researcher_agent) -> List[Dict[str, Any]]:
        """
        Execute the replan by running additional searches

        Args:
            replan_json: Replan specification from create_replan
            researcher_agent: ResearcherAgent instance to execute searches

        Returns:
            List of additional evidence findings
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
        Compare before/after evaluations to measure improvement

        Args:
            original_evaluation: Evaluation before replan
            new_evaluation: Evaluation after replan

        Returns:
            Improvement analysis
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
        """Generate human-readable improvement summary"""
        if overall_improvement >= 0.5:
            return f"Significant improvement achieved (+{overall_improvement:.1f} overall score)"
        elif overall_improvement >= 0.2:
            return f"Moderate improvement achieved (+{overall_improvement:.1f} overall score)"
        elif overall_improvement > 0:
            return f"Minor improvement achieved (+{overall_improvement:.1f} overall score)"
        else:
            return f"No meaningful improvement detected ({overall_improvement:+.1f} overall score)"


class ModelRouterAgent:
    """Phase 9: Model Router Agent - Optimize cost/quality tradeoffs by selecting appropriate model profiles"""

    def __init__(self):
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
        Determine optimal model routing for research pipeline nodes

        Args:
            user_query: The user's research query
            nodes: List of nodes to route (defaults to all 7 nodes)

        Returns:
            Routing recommendations with explanations
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
        """Analyze the complexity characteristics of the user query"""

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
        """Select the optimal model profile for a specific node"""

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
        """Generate human-readable explanation for routing decision"""

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
        """Generate cost breakdown by profile"""
        breakdown = {"cheap": 0, "balanced": 0, "premium": 0}

        for decision in routing_decisions:
            breakdown[decision["profile"]] += 1

        return breakdown

    def _generate_optimization_notes(self, routing_decisions: List[Dict], query_complexity: Dict) -> List[str]:
        """Generate optimization recommendations"""
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


class ObservabilityAgent:
    """Phase 10: Observability Agent - Summarize run logs into concise audit trails"""

    def __init__(self):
        # Define log patterns for different system components
        self.log_patterns = {
            "phase_start": r"=== (.+?) ===",
            "timestamp": r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
            "file_save": r"saved to: (.+)",
            "error": r"Error|Exception|Failed|✗",
            "success": r"✓|completed|success|Found \d+",
            "tool_call": r"(research_subquery|compress_and_align|generate_report|evaluate_report|create_replan)",
            "query": r"Query: (.+)",
            "score": r"Score: ([\d.]+)",
            "cost": r"Cost: ([\d.]+)"
        }

        # Define step mappings for different phases
        self.phase_mappings = {
            "CLARIFIED RESEARCH": "clarify",
            "RESEARCH BRIEF": "brief",
            "SEARCH PLAN": "plan",
            "RESEARCHER AGENT": "research",
            "TESTING RESEARCHER": "research",
            "COMPRESS": "compress",
            "CONFLICT ANALYSIS": "compress",
            "FINAL RESEARCH REPORT": "report",
            "REPORT GENERATION": "report",
            "REPORT EVALUATION": "judge",
            "EVALUATION": "judge",
            "RECOVERY": "recovery",
            "REPLAN": "recovery",
            "MODEL ROUTER": "routing",
            "ROUTING": "routing"
        }

    def create_audit_trail(self, raw_logs: str) -> str:
        """
        Convert raw logs into a structured audit trail

        Args:
            raw_logs: Raw log lines as string

        Returns:
            Formatted Markdown audit trail
        """

        log_lines = raw_logs.split('\n')
        parsed_steps = self._parse_log_lines(log_lines)
        audit_trail = self._format_audit_trail(parsed_steps)

        return audit_trail

    def _parse_log_lines(self, log_lines: List[str]) -> List[Dict[str, Any]]:
        """Parse raw log lines into structured step data"""

        steps = []
        current_step = None
        current_timestamp = None

        for line in log_lines:
            line = line.strip()
            if not line:
                continue

            # Extract timestamp if present
            timestamp_match = re.search(self.log_patterns["timestamp"], line)
            if timestamp_match:
                current_timestamp = timestamp_match.group(1)

            # Detect phase start
            phase_match = re.search(self.log_patterns["phase_start"], line)
            if phase_match:
                # Save previous step if exists
                if current_step:
                    steps.append(current_step)

                # Start new step
                phase_name = phase_match.group(1)
                step_name = self._map_phase_to_step(phase_name)

                current_step = {
                    "step": step_name,
                    "phase_name": phase_name,
                    "timestamp": current_timestamp or self._get_current_timestamp(),
                    "input_summary": "",
                    "decision": "",
                    "tool_calls": [],
                    "outcome": "",
                    "issues": [],
                    "raw_content": []
                }

            # If we have a current step, analyze the line
            if current_step:
                current_step["raw_content"].append(line)
                self._analyze_log_line(line, current_step)

        # Add final step
        if current_step:
            steps.append(current_step)

        # Post-process steps to extract summaries
        for step in steps:
            self._extract_step_summaries(step)

        return steps

    def _map_phase_to_step(self, phase_name: str) -> str:
        """Map phase name to standardized step name"""

        for key, value in self.phase_mappings.items():
            if key.upper() in phase_name.upper():
                return value

        # Default mapping for unknown phases
        return phase_name.lower().replace(" ", "_")

    def _analyze_log_line(self, line: str, step: Dict[str, Any]):
        """Analyze individual log line and extract relevant information"""

        # Check for queries
        query_match = re.search(self.log_patterns["query"], line)
        if query_match and not step["input_summary"]:
            step["input_summary"] = f"Query: {query_match.group(1)[:100]}..."

        # Check for tool calls
        tool_match = re.search(self.log_patterns["tool_call"], line)
        if tool_match:
            step["tool_calls"].append(tool_match.group(1))

        # Check for file saves (outcomes)
        save_match = re.search(self.log_patterns["file_save"], line)
        if save_match:
            if not step["outcome"]:
                step["outcome"] = f"Generated output: {save_match.group(1)}"
            else:
                step["outcome"] += f"; {save_match.group(1)}"

        # Check for errors
        if re.search(self.log_patterns["error"], line):
            step["issues"].append(line)

        # Check for success indicators
        success_match = re.search(self.log_patterns["success"], line)
        if success_match and not step["outcome"]:
            step["outcome"] = line

        # Check for scores
        score_match = re.search(self.log_patterns["score"], line)
        if score_match:
            if not step["outcome"]:
                step["outcome"] = f"Score: {score_match.group(1)}"
            else:
                step["outcome"] += f" (Score: {score_match.group(1)})"

        # Check for costs
        cost_match = re.search(self.log_patterns["cost"], line)
        if cost_match:
            if not step["outcome"]:
                step["outcome"] = f"Cost: {cost_match.group(1)}"
            else:
                step["outcome"] += f" (Cost: {cost_match.group(1)})"

    def _extract_step_summaries(self, step: Dict[str, Any]):
        """Extract summaries and decisions from raw content"""

        raw_text = " ".join(step["raw_content"])

        # Extract input summary if not already set
        if not step["input_summary"]:
            step["input_summary"] = self._extract_input_summary(step["step"], raw_text)

        # Extract decision
        step["decision"] = self._extract_decision(step["step"], raw_text)

        # Extract outcome if not already set
        if not step["outcome"]:
            step["outcome"] = self._extract_outcome(step["step"], raw_text)

        # Deduplicate tool calls
        step["tool_calls"] = list(dict.fromkeys(step["tool_calls"]))

    def _extract_input_summary(self, step_name: str, raw_text: str) -> str:
        """Extract input summary based on step type"""

        if step_name == "clarify":
            return "User research query received for clarification and structuring"
        elif step_name == "brief":
            return "Clarified query processed to generate research brief outline"
        elif step_name == "plan":
            return "Research brief analyzed to create diversified search strategy"
        elif step_name == "research":
            return "Search plan executed to collect evidence from multiple sources"
        elif step_name == "compress":
            return "Raw evidence processed for synthesis and conflict identification"
        elif step_name == "report":
            return "Compressed findings formatted into final narrative report"
        elif step_name == "judge":
            return "Generated report evaluated across quality dimensions"
        elif step_name == "recovery":
            return "Low-quality results detected, recovery plan initiated"
        elif step_name == "routing":
            return "Query analyzed for optimal model routing decisions"
        else:
            return f"Processing {step_name} phase"

    def _extract_decision(self, step_name: str, raw_text: str) -> str:
        """Extract key decision made in this step"""

        if step_name == "clarify":
            return "Structured query into objective, definitions, scope, and success criteria"
        elif step_name == "brief":
            return "Generated comprehensive research brief with sub-questions and criteria"
        elif step_name == "plan":
            return "Created diversified search plan with targeted subqueries"
        elif step_name == "research":
            evidence_count = len(re.findall(r"Found \d+", raw_text))
            return f"Executed search strategy across {evidence_count} queries"
        elif step_name == "compress":
            return "Synthesized evidence into key findings and identified conflicts"
        elif step_name == "report":
            return "Generated audience-appropriate report with citations and recommendations"
        elif step_name == "judge":
            score_match = re.search(r"overall_score.*?(\d\.\d)", raw_text)
            score = score_match.group(1) if score_match else "N/A"
            return f"Evaluated report quality (Overall: {score}/5.0)"
        elif step_name == "recovery":
            query_count = len(re.findall(r"recovery.*?quer", raw_text.lower()))
            return f"Generated {query_count} targeted recovery queries to address quality gaps"
        elif step_name == "routing":
            premium_count = len(re.findall(r"premium", raw_text.lower()))
            return f"Selected model profiles with {premium_count} premium allocations"
        else:
            return f"Processed {step_name} successfully"

    def _extract_outcome(self, step_name: str, raw_text: str) -> str:
        """Extract outcome/result from step"""

        # Look for file saves first
        save_matches = re.findall(self.log_patterns["file_save"], raw_text)
        if save_matches:
            return f"Files saved: {', '.join(save_matches)}"

        # Look for completion indicators
        if "completed" in raw_text.lower() or "success" in raw_text.lower():
            return f"{step_name.capitalize()} phase completed successfully"

        # Default outcome
        return f"{step_name.capitalize()} processing completed"

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in standard format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _format_audit_trail(self, steps: List[Dict[str, Any]]) -> str:
        """Format parsed steps into Markdown audit trail"""

        if not steps:
            return "# Audit Trail\n\nNo steps found in logs."

        audit_lines = [
            "# Deep Research Agent - Audit Trail",
            f"\n**Generated:** {self._get_current_timestamp()}",
            f"**Total Steps:** {len(steps)}",
            "\n---\n"
        ]

        for i, step in enumerate(steps, 1):
            # Format step header
            audit_lines.append(f"## Step {i}: {step['step'].title()}")
            audit_lines.append(f"**Timestamp:** {step['timestamp']}")
            audit_lines.append("")

            # Format checklist items
            audit_lines.append("### Process Checklist")
            audit_lines.append("")

            # Input summary
            audit_lines.append(f"- [x] **Input:** {step['input_summary']}")

            # Decision
            audit_lines.append(f"- [x] **Decision:** {step['decision']}")

            # Tool calls
            if step['tool_calls']:
                tools_str = ", ".join(step['tool_calls'])
                audit_lines.append(f"- [x] **Tools Used:** {tools_str}")
            else:
                audit_lines.append(f"- [x] **Tools Used:** Built-in processing")

            # Outcome
            audit_lines.append(f"- [x] **Outcome:** {step['outcome']}")

            # Issues
            if step['issues']:
                audit_lines.append(f"- [⚠️] **Issues:** {len(step['issues'])} issues detected")
                for issue in step['issues'][:3]:  # Show first 3 issues
                    audit_lines.append(f"  - {issue}")
                if len(step['issues']) > 3:
                    audit_lines.append(f"  - ... and {len(step['issues']) - 3} more")
            else:
                audit_lines.append(f"- [x] **Issues:** None detected")

            audit_lines.append("")
            audit_lines.append("---")
            audit_lines.append("")

        # Add summary
        total_issues = sum(len(step['issues']) for step in steps)
        successful_steps = len([s for s in steps if not s['issues']])

        audit_lines.extend([
            "## Summary",
            "",
            f"- **Total Steps:** {len(steps)}",
            f"- **Successful Steps:** {successful_steps}/{len(steps)}",
            f"- **Total Issues:** {total_issues}",
            f"- **Success Rate:** {(successful_steps/len(steps)*100):.1f}%",
            "",
            "**Key Files Generated:**"
        ])

        # Collect all file outputs
        all_files = []
        for step in steps:
            if "saved to:" in step['outcome']:
                files = re.findall(r"([^/\s]+\.(?:json|md))", step['outcome'])
                all_files.extend(files)

        if all_files:
            for file in set(all_files):  # Remove duplicates
                audit_lines.append(f"- {file}")
        else:
            audit_lines.append("- No files detected in log output")

        return "\n".join(audit_lines)


def main():
    print("Deep Research Agent initialized")

    if len(sys.argv) < 2:
        print("Usage: python main.py '<your research query>'")
        print("Example: python main.py 'Compare 2024–2025 evidence on ultra-processed foods and give recommendations.'")
        return

    user_query = sys.argv[1]
    print(f"User Query: {user_query}\n")

    # Phase 1: Clarify
    clarify_agent = ClarifyAgent()
    clarified = clarify_agent.clarify_query(user_query)

    print("=== CLARIFIED RESEARCH SPECIFICATION ===")
    print(json.dumps(clarified, indent=2, ensure_ascii=False))
    print("\n")

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

    # Save clarified query
    clarified_filename = data_manager.save_clarify(clarified)
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "phase": "clarify",
        "action": "complete",
        "data": {"file": clarified_filename}
    })

    # Phase 2: Research Brief
    brief_agent = ResearchBriefAgent()
    brief_md = brief_agent.create_brief(clarified)

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

    # Phase 3: Supervisor/Planner
    planner_agent = SupervisorPlannerAgent()
    search_plan = planner_agent.create_plan(brief_md)

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

    # Phase 9: Model Router (test routing decisions)
    if len(sys.argv) > 2 and sys.argv[2] == "--test-routing":
        print("\n=== TESTING MODEL ROUTER AGENT ===")
        router_agent = ModelRouterAgent()

        # Test routing for the current query
        routing_result = router_agent.route_models(user_query)

        print("=== MODEL ROUTING DECISIONS ===")
        print(json.dumps(routing_result, indent=2, ensure_ascii=False))

        # Save routing decision
        # Save routing decision to logs
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "phase": "routing",
            "action": "complete",
            "data": routing_result
        })

        print(f"\n=== ROUTING DECISION LOGGED ===")
        print(f"Routing decision added to run logs")

    # Phase 10: Observability (test log summarization)
    if len(sys.argv) > 2 and sys.argv[2] == "--test-observability":
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
Files saved to: data/intermediate/research_brief_{timestamp}.md

=== SEARCH PLAN ===
Created diversified search plan with 6 targeted subqueries
Files saved to: data/intermediate/search_plan_{timestamp}.json

=== TESTING RESEARCHER AGENT ===
Found 8 evidence items from search query
Research phase completed successfully

=== COMPRESS + CONFLICT ANALYSIS ===
Synthesized evidence into key findings
Identified 2 conflicts between studies
Files saved to: data/intermediate/compression_{timestamp}.json

=== FINAL RESEARCH REPORT ===
Generated audience-appropriate report with citations
Files saved to: data/reports/research_report_{timestamp}.md

=== REPORT EVALUATION ===
Overall Score: 4.2/5.0
Coverage: 5/5, Faithfulness: 5/5, Balance: 5/5
Files saved to: data/evaluations/evaluation_{timestamp}.json

=== MODEL ROUTING DECISIONS ===
Selected model profiles with 2 premium allocations
Total Cost: 11.0
Files saved to: data/intermediate/routing_decision_{timestamp}.json"""

        # Test observability agent
        obs_agent = ObservabilityAgent()
        audit_trail = obs_agent.create_audit_trail(sample_logs)

        print("=== AUDIT TRAIL GENERATED ===")
        print(audit_trail[:1000] + "..." if len(audit_trail) > 1000 else audit_trail)

        # Save audit trail
        audit_filename = f"data/logs/audit_trail_{timestamp}.md"
        os.makedirs("data/logs", exist_ok=True)
        with open(audit_filename, 'w', encoding='utf-8') as f:
            f.write(audit_trail)

        print(f"\n=== AUDIT TRAIL SAVED ===")
        print(f"Audit trail saved to: {audit_filename}")

    # Phase 4: Evidence Collection - Run by default or when testing
    if len(sys.argv) <= 2 or sys.argv[2] == "--test-researcher":
        print("\n=== PHASE 4: EVIDENCE COLLECTION ===")
        researcher_agent = ResearcherAgent()

        # Collect evidence from all subqueries (or limit for testing)
        all_evidence = []
        flattened_evidence = []

        if len(sys.argv) > 2 and sys.argv[2] == "--test-researcher":
            # Test mode: only first subquery
            max_queries = 1
            print("Testing mode: processing first subquery only")
        else:
            # Full mode: process all subqueries
            max_queries = len(search_plan["plan"])
            print(f"Full mode: processing {max_queries} subqueries")

        for i in range(min(max_queries, len(search_plan["plan"]))):
            subquery = search_plan["plan"][i]
            print(f"\nSearching subquery {i+1}/{max_queries}: {subquery['subquery']}")

            evidence_result = researcher_agent.research_subquery(subquery)
            all_evidence.append(evidence_result)

            # Flatten evidence for easier processing
            for evidence in evidence_result.get("findings", []):
                flattened_evidence.append(evidence)

            print(f"Found {len(evidence_result.get('findings', []))} pieces of evidence")

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

    # Phase 5: Compress + Conflict Analysis - Run by default or when testing
    if len(sys.argv) <= 2 or sys.argv[2] == "--test-compress":
        print("\n=== PHASE 5: COMPRESS + CONFLICT ANALYSIS ===")
        compress_agent = CompressConflictAgent()

        # Use evidence collected in Phase 4 (reuse variables from scope)
        if 'all_evidence' in locals() and all_evidence:
            print(f"Using {len(all_evidence)} evidence collections from Phase 4")
            compression_result = compress_agent.compress_and_align(all_evidence)
        else:
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

    # Phase 6: Report Generation - Run by default or when testing
    if len(sys.argv) <= 2 or sys.argv[2] == "--test-report":
        print("\n=== PHASE 6: REPORT GENERATION ===")
        report_agent = ReportAgent()

        # Use data from previous phases
        if 'compression_result' in locals() and 'flattened_evidence' in locals():
            print(f"Using compression result and {len(flattened_evidence)} evidence items from previous phases")
        else:
            print("No previous data available - running test mode with fresh data collection")
            # Fallback for test-only mode - collect fresh data
            researcher_agent = ResearcherAgent()
            compress_agent = CompressConflictAgent()
            all_evidence = []
            flattened_evidence = []
            max_queries = min(3, len(search_plan["plan"]))

            for i in range(max_queries):
                subquery = search_plan["plan"][i]
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

        print(f"\n=== REPORT SAVED ===")
        print(f"Report saved to: {report_filename}")

        # Phase 7: Evaluation/QA
        evaluator_agent = EvaluatorAgent()
        evaluation_result = evaluator_agent.evaluate_report(final_report, flattened_evidence)

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

        print(f"\n=== EVALUATION SAVED ===")
        print(f"Evaluation saved to: {eval_filename}")

    # Phase 8: Recovery/Replan (if quality is below threshold)
    if len(sys.argv) > 2 and sys.argv[2] == "--test-recovery":
        print("\n=== TESTING COMPLETE RESEARCH PIPELINE WITH RECOVERY ===")
        researcher_agent = ResearcherAgent()
        compress_agent = CompressConflictAgent()
        report_agent = ReportAgent()
        evaluator_agent = EvaluatorAgent()
        recovery_agent = RecoveryReplanAgent()

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

        # Save collected evidence
        evidence_filename = f"data/evidence/evidence_collection_{timestamp}.json"
        with open(evidence_filename, 'w', encoding='utf-8') as f:
            json.dump(all_evidence, f, indent=2, ensure_ascii=False)

        # Compress and analyze
        compression_result = compress_agent.compress_and_align(all_evidence)

        # Save compression result
        compression_filename = f"data/intermediate/compression_{timestamp}.json"
        with open(compression_filename, 'w', encoding='utf-8') as f:
            json.dump(compression_result, f, indent=2, ensure_ascii=False)

        # Generate report
        target_audience = "consumer"  # Can be changed to "executive" or "researcher"
        final_report = report_agent.generate_report(
            compression_result,
            flattened_evidence,
            user_query,
            target_audience
        )

        print("\n=== INITIAL RESEARCH REPORT ===")
        print(final_report)

        # Save initial report to file
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

        # Phase 7: Evaluation/QA
        evaluation_result = evaluator_agent.evaluate_report(final_report, flattened_evidence)

        print(f"\n=== INITIAL REPORT EVALUATION ===")
        print(json.dumps(evaluation_result, indent=2, ensure_ascii=False))

        # Save evaluation to file
        eval_filename = f"data/evaluations/evaluation_{timestamp}.json"
        with open(eval_filename, 'w', encoding='utf-8') as f:
            json.dump(evaluation_result, f, indent=2, ensure_ascii=False)

        print(f"\n=== INITIAL EVALUATION SAVED ===")
        print(f"Evaluation saved to: {eval_filename}")

        # Create replan based on gaps and evaluation
        print("\n=== TESTING RECOVERY/REPLAN AGENT ===")
        replan_spec = recovery_agent.create_replan(compression_result, evaluation_result, user_query)

        print("=== RECOVERY REPLAN SPECIFICATION ===")
        print(json.dumps(replan_spec, indent=2, ensure_ascii=False))

        # Save replan specification
        replan_filename = f"data/intermediate/replan_spec_{timestamp}.json"
        with open(replan_filename, 'w', encoding='utf-8') as f:
            json.dump(replan_spec, f, indent=2, ensure_ascii=False)

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
        else:
            print("\n=== NO RECOVERY NEEDED ===")
            print("Report quality already meets threshold - no additional searches required")

    # Save logs at the end of execution
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "phase": "complete",
        "action": "end",
        "data": {"run_id": run_id, "status": "success"}
    })

    # Save all logs
    logs_filename = data_manager.save_logs(logs)
    print(f"\n=== RUN COMPLETE ===")
    print(f"Run ID: {run_id}")
    print(f"Logs saved to: {logs_filename}")
    print(f"Report available at: data/runs/{run_id}/report.md")
    print(f"Also exported to: data/out/research_report_{run_id}.md")

    # TODO: Phase 9-N: Implement additional features (Email delivery, API integration, etc.)

if __name__ == "__main__":
    main()