"""
Phase 3: Supervisor/Planner Agent

Converts research briefs into diversified subqueries for parallel execution.
Decomposes research objectives into targeted search strategies with specific operators.
"""

from typing import Dict, Any, List


class SupervisorPlannerAgent:
    """
    Phase 3: Supervisor/Planner - Convert brief into diversified subqueries for parallel execution.

    Takes comprehensive research briefs and creates structured search plans with
    multiple targeted subqueries designed to gather diverse, high-quality evidence.
    """

    def create_plan(self, brief_markdown: str) -> Dict[str, Any]:
        """
        Convert research brief into structured search plan.

        Analyzes the research brief to extract key questions and context, then generates
        diversified subqueries with specific search operators and coverage targets.

        Args:
            brief_markdown: Markdown formatted research brief from ResearchBriefAgent

        Returns:
            JSON plan with subqueries and coverage targets including:
            - plan: List of subqueries with operators and rationale
            - coverage_target: Quality and quantity requirements
        """
        # Extract key sub-questions from brief
        sub_questions = self._extract_sub_questions_from_brief(brief_markdown)

        # Extract research context
        context = self._extract_context_from_brief(brief_markdown)

        # Extract topic keywords from brief
        topic_keywords = self._extract_topic_keywords_from_brief(brief_markdown)

        # Generate diversified subqueries
        subqueries = self._generate_subqueries(sub_questions, context, topic_keywords)

        # Set coverage targets
        coverage_target = self._define_coverage_target(context)

        plan = {
            "plan": subqueries,
            "coverage_target": coverage_target
        }

        return plan

    def _extract_sub_questions_from_brief(self, brief_markdown: str) -> List[str]:
        """Extract the key sub-questions from the research brief."""
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
        """Extract key context information from research brief."""
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

    def _extract_topic_keywords_from_brief(self, brief_markdown: str) -> List[str]:
        """Extract topic keywords from research brief."""
        lines = brief_markdown.split('\n')
        for line in lines:
            line = line.strip()
            if "**Topic Keywords:**" in line:
                keywords_str = line.split("**Topic Keywords:**")[1].strip()
                return [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
        return []

    def _generate_subqueries(self, sub_questions: List[str], context: Dict[str, str], topic_keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Generate diversified subqueries with search operators based on research context."""
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
            # Generic approach using topic keywords and sub-questions
            base_queries = []
            topic_terms = topic_keywords[:2] if topic_keywords else []  # Use top 2 topic keywords

            for i, question in enumerate(sub_questions[:6]):
                # Extract key terms from question and combine with topic keywords
                question_terms = self._extract_key_terms(question)

                # Prioritize topic keywords, then meaningful question terms
                combined_terms = topic_terms + [term for term in question_terms if term not in topic_terms]
                search_terms = combined_terms[:4]  # Limit to 4 terms for focused search

                base_queries.append({
                    "base": " ".join(search_terms),
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
        """Extract key search terms from a question using simple keyword filtering."""
        # Simple keyword extraction (in production, use NLP)
        stop_words = {"what", "are", "the", "how", "why", "when", "where", "is", "do", "does", "can", "will", "would", "should"}
        words = question.lower().replace("?", "").split()
        key_terms = [word for word in words if word not in stop_words and len(word) > 3]
        return key_terms[:4]  # Limit to 4 key terms

    def _define_coverage_target(self, context: Dict[str, str]) -> Dict[str, Any]:
        """Define coverage requirements for the search plan based on research topic."""
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