"""
Agents package for Deep Research Agent.

Contains all 10 specialized agents that comprise the research pipeline:
- Phase 1: ClarifyAgent - Transform vague queries into structured specs
- Phase 2: ResearchBriefAgent - Create detailed research outlines
- Phase 3: SupervisorPlannerAgent - Decompose into parallel search tasks
- Phase 4: ResearcherAgent - Execute web searches and extract evidence
- Phase 5: CompressConflictAgent - Synthesize findings and identify conflicts
- Phase 6: ReportAgent - Generate structured, audience-tailored reports
- Phase 7: EvaluatorAgent - Assess report quality across 6 dimensions
- Phase 8: RecoveryReplanAgent - Fix quality issues through targeted searches
- Phase 9: ModelRouterAgent - Optimize cost/quality by selecting models
- Phase 10: ObservabilityAgent - Generate audit trails and structured logs
"""

from .clarify_agent import ClarifyAgent
from .research_brief_agent import ResearchBriefAgent
from .supervisor_planner_agent import SupervisorPlannerAgent
from .researcher_agent import ResearcherAgent
from .compress_conflict_agent import CompressConflictAgent
from .report_agent import ReportAgent
from .evaluator_agent import EvaluatorAgent
from .recovery_replan_agent import RecoveryReplanAgent
from .model_router_agent import ModelRouterAgent
from .observability_agent import ObservabilityAgent

__all__ = [
    'ClarifyAgent',
    'ResearchBriefAgent',
    'SupervisorPlannerAgent',
    'ResearcherAgent',
    'CompressConflictAgent',
    'ReportAgent',
    'EvaluatorAgent',
    'RecoveryReplanAgent',
    'ModelRouterAgent',
    'ObservabilityAgent'
]