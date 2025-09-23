"""
Data Manager for Deep Research Agent.

Manages file operations and data persistence for the research pipeline.
Handles creation of directory structure and saving of results from each phase.
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime


class DataManager:
    """
    Manages file operations for the structured data directory layout.

    Creates timestamped run directories and manages persistence of results
    from each phase of the research pipeline. Also maintains shared aggregated
    data across multiple runs.
    """

    def __init__(self, run_id: str = None):
        """
        Initialize DataManager with a unique run identifier.

        Args:
            run_id: Optional run identifier. If None, generates timestamp-based ID.
        """
        if run_id is None:
            run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_id = run_id
        self.run_dir = f"data/runs/{run_id}"
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories for data organization."""
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
        """Save clarification results from Phase 1."""
        filepath = f"{self.run_dir}/clarify.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def save_brief(self, content: str) -> str:
        """Save research brief from Phase 2."""
        filepath = f"{self.run_dir}/brief.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath

    def save_plan(self, data: Dict[str, Any]) -> str:
        """Save search plan from Phase 3."""
        filepath = f"{self.run_dir}/plan.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def save_evidence(self, evidence_list: List[Dict[str, Any]]) -> str:
        """
        Save evidence collection from Phase 4.

        Stores evidence as JSONL format in both run-specific and shared locations.
        """
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
        """
        Save compression results from Phase 5.

        Stores synthesized insights in both run-specific and aggregated locations.
        """
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
        """
        Save final report from Phase 6.

        Stores report in both run directory and exportable output location.
        """
        filepath = f"{self.run_dir}/report.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Also save to out directory
        out_filepath = f"data/out/research_report_{self.run_id}.md"
        with open(out_filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def save_evaluation(self, data: Dict[str, Any]) -> str:
        """Save evaluation results from Phase 7."""
        filepath = f"{self.run_dir}/judge.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def save_replan(self, data: Dict[str, Any]) -> str:
        """Save replan results from Phase 8."""
        filepath = f"{self.run_dir}/replan.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def save_logs(self, logs: List[Dict[str, Any]]) -> str:
        """
        Save structured logs from Phase 10.

        Stores logs as NDJSON format for observability and audit trails.
        """
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
        """Log error information to observability system."""
        error_filepath = "data/observability/errors.ndjson"
        error_with_run = error_data.copy()
        error_with_run['run_id'] = self.run_id
        error_with_run['timestamp'] = datetime.now().isoformat()

        with open(error_filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_with_run, ensure_ascii=False) + '\n')