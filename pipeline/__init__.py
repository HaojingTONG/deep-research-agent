"""
Pipeline package for Deep Research Agent.

Contains the main pipeline runner and orchestration logic for the 10-phase research process.
Provides a unified interface for executing the complete research workflow.
"""

from .runner import run_research_pipeline

__all__ = ['run_research_pipeline']