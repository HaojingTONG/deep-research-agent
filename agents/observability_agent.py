"""
Phase 10: Observability Agent

Summarizes run logs into concise audit trails.
Generates structured audit reports for transparency and debugging.
"""

import re
from typing import Dict, Any, List


class ObservabilityAgent:
    """
    Phase 10: Observability Agent - Summarize run logs into concise audit trails.

    Processes raw execution logs and generates structured audit trails for
    transparency, debugging, and compliance purposes.
    """

    def __init__(self):
        """Initialize the ObservabilityAgent with log parsing patterns."""
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
        Convert raw logs into a structured audit trail.

        Processes execution logs to extract key events, decisions, and outcomes
        in a format suitable for audit and compliance purposes.

        Args:
            raw_logs: Raw log lines as string from pipeline execution

        Returns:
            Formatted Markdown audit trail with structured step information
        """
        log_lines = raw_logs.split('\n')
        parsed_steps = self._parse_log_lines(log_lines)
        audit_trail = self._format_audit_trail(parsed_steps)

        return audit_trail

    def _parse_log_lines(self, log_lines: List[str]) -> List[Dict[str, Any]]:
        """Parse raw log lines into structured step data."""
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
        """Map phase name to standardized step name for consistency."""
        for key, value in self.phase_mappings.items():
            if key.upper() in phase_name.upper():
                return value

        # Default mapping for unknown phases
        return phase_name.lower().replace(" ", "_")

    def _analyze_log_line(self, line: str, step: Dict[str, Any]):
        """Analyze individual log line and extract relevant information."""
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
        """Extract summaries and decisions from raw content for each step."""
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
        """Extract input summary based on step type and context."""
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
        """Extract key decision made in this step based on step type."""
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
        """Extract outcome/result from step execution."""
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
        """Get current timestamp in standard format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _format_audit_trail(self, steps: List[Dict[str, Any]]) -> str:
        """Format parsed steps into comprehensive Markdown audit trail."""
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