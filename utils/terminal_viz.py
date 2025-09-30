"""
Terminal visualization for Deep Research Agent pipeline.

Provides real-time terminal UI showing agent execution progress,
timing, and status using the Rich library.
"""

import threading
import time
from typing import Dict, List, Optional
from datetime import datetime

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .telemetry import TelemetryCollector, PhaseEvent, PhaseStatus, get_telemetry_collector


class TerminalVisualizer:
    """
    Real-time terminal visualization for pipeline execution.

    Creates a Rich-based terminal UI that updates live as agents execute,
    showing timeline, status, and progress information.
    """

    def __init__(self, collector: TelemetryCollector = None):
        self.collector = collector or get_telemetry_collector()
        self.console = Console()
        self.layout = Layout()
        self._setup_layout()
        self._live: Optional[Live] = None
        self._running = False
        self._update_thread: Optional[threading.Thread] = None

    def _setup_layout(self):
        """Setup the main layout structure."""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )

        # Split main area into timeline and details
        self.layout["main"].split_row(
            Layout(name="timeline", ratio=2),
            Layout(name="details", ratio=1)
        )

    def _get_status_icon(self, status: PhaseStatus) -> str:
        """Get icon for phase status."""
        icons = {
            PhaseStatus.PENDING: "⏳",
            PhaseStatus.RUNNING: "🔄",
            PhaseStatus.SUCCESS: "✅",
            PhaseStatus.SKIPPED: "⏭️",
            PhaseStatus.RECOVERED: "🔧",
            PhaseStatus.FAILED: "❌"
        }
        return icons.get(status, "❓")

    def _get_status_color(self, status: PhaseStatus) -> str:
        """Get color for phase status."""
        colors = {
            PhaseStatus.PENDING: "yellow",
            PhaseStatus.RUNNING: "cyan",
            PhaseStatus.SUCCESS: "green",
            PhaseStatus.SKIPPED: "blue",
            PhaseStatus.RECOVERED: "magenta",
            PhaseStatus.FAILED: "red"
        }
        return colors.get(status, "white")

    def _format_duration(self, duration: Optional[float]) -> str:
        """Format duration in human-readable format."""
        if duration is None:
            return "-"
        if duration < 1:
            return f"{duration*1000:.0f}ms"
        elif duration < 60:
            return f"{duration:.1f}s"
        else:
            minutes = int(duration // 60)
            seconds = duration % 60
            return f"{minutes}m {seconds:.1f}s"

    def _create_header(self) -> Panel:
        """Create the header panel."""
        pipeline_duration = self.collector.get_pipeline_duration()
        duration_text = self._format_duration(pipeline_duration) if pipeline_duration else "Starting..."
        pipeline_status = self.collector.get_pipeline_status()
        is_complete = self.collector.is_pipeline_complete()

        header_text = Text()
        header_text.append("🔬 Deep Research Agent Pipeline ", style="bold cyan")

        if is_complete:
            if pipeline_status == "completed":
                header_text.append(f"│ Completed in {duration_text}", style="bold green")
            else:
                header_text.append(f"│ Failed after {duration_text}", style="bold red")
        else:
            header_text.append(f"│ Runtime: {duration_text}", style="bold white")

        active_phases = self.collector.get_active_phases()
        if active_phases and not is_complete:
            active_names = [phase.phase_name for phase in active_phases]
            header_text.append(f" │ Active: {', '.join(active_names)}", style="bold yellow")
        elif not active_phases and not is_complete:
            header_text.append(" │ Idle – awaiting next phase", style="dim yellow")

        return Panel(header_text, title="Pipeline Status", border_style="cyan")

    def _create_timeline(self) -> Panel:
        """Create the timeline panel showing all phases."""
        events = self.collector.get_events()

        if not events:
            return Panel("No phases started yet...", title="Timeline", border_style="blue")

        tree = Tree("🔬 Research Pipeline")

        # Group events by parent phase to show nesting
        main_phases = []
        nested_phases = {}

        for event in events:
            if event.parent_phase:
                if event.parent_phase not in nested_phases:
                    nested_phases[event.parent_phase] = []
                nested_phases[event.parent_phase].append(event)
            else:
                main_phases.append(event)

        # Add main phases to tree
        for event in main_phases:
            icon = self._get_status_icon(event.status)
            color = self._get_status_color(event.status)
            duration = self._format_duration(event.duration)
            start_time = event.start_time.strftime("%H:%M:%S")

            # Create phase text
            phase_text = Text()
            phase_text.append(f"{icon} ", style=color)
            phase_text.append(f"{event.phase_name}", style=f"bold {color}")
            phase_text.append(f" ({duration}) ", style="dim")
            phase_text.append(f"[{start_time}]", style="dim blue")

            if event.notes:
                phase_text.append(f"\n   {event.notes}", style="dim")

            phase_node = tree.add(phase_text)

            # Add nested phases (like recovery)
            if event.phase_name in nested_phases:
                for nested_event in nested_phases[event.phase_name]:
                    nested_icon = self._get_status_icon(nested_event.status)
                    nested_color = self._get_status_color(nested_event.status)
                    nested_duration = self._format_duration(nested_event.duration)
                    nested_start = nested_event.start_time.strftime("%H:%M:%S")

                    nested_text = Text()
                    nested_text.append(f"{nested_icon} ", style=nested_color)
                    nested_text.append(f"{nested_event.phase_name}", style=f"bold {nested_color}")
                    nested_text.append(f" ({nested_duration}) ", style="dim")
                    nested_text.append(f"[{nested_start}]", style="dim blue")

                    if nested_event.notes:
                        nested_text.append(f"\n   {nested_event.notes}", style="dim")

                    phase_node.add(nested_text)

        # Add pipeline summary if completed
        if self.collector.is_pipeline_complete():
            pipeline_status = self.collector.get_pipeline_status()
            pipeline_duration = self.collector.get_pipeline_duration()

            summary_text = Text()
            if pipeline_status == "completed":
                summary_text.append("🏁 ", style="bold green")
                summary_text.append("Pipeline Completed", style="bold green")
            else:
                summary_text.append("💥 ", style="bold red")
                summary_text.append("Pipeline Failed", style="bold red")

            if pipeline_duration:
                summary_text.append(f" ({self._format_duration(pipeline_duration)})", style="dim")

            tree.add(summary_text)

        return Panel(tree, title="Execution Timeline", border_style="blue")

    def _create_details(self) -> Panel:
        """Create the details panel showing current phase info."""
        active_phases = self.collector.get_active_phases()

        if not active_phases:
            events = self.collector.get_events()
            if events:
                # Show last completed phase
                last_event = events[-1]
                status_text = Text()
                status_text.append("Last Phase: ", style="bold")
                status_text.append(f"{last_event.phase_name}\n", style="bold white")
                status_text.append(f"Status: {last_event.status.value.title()}\n",
                                 style=self._get_status_color(last_event.status))
                if last_event.duration:
                    status_text.append(f"Duration: {self._format_duration(last_event.duration)}\n", style="dim")
                if last_event.notes:
                    status_text.append(f"Notes: {last_event.notes}\n", style="dim")

                return Panel(status_text, title="Phase Details", border_style="green")
            else:
                return Panel("Waiting for pipeline to start...", title="Phase Details", border_style="dim")

        # Show active phase details
        active_phase = active_phases[0]  # Show first active phase
        status_text = Text()
        status_text.append("Currently Running: ", style="bold")
        status_text.append(f"{active_phase.phase_name}\n", style="bold cyan")

        # Calculate current duration
        current_duration = (datetime.now() - active_phase.start_time).total_seconds()
        status_text.append(f"Running for: {self._format_duration(current_duration)}\n", style="dim")

        if active_phase.model_used:
            status_text.append(f"Model: {active_phase.model_used}\n", style="dim")

        if active_phase.notes:
            status_text.append(f"Notes: {active_phase.notes}\n", style="dim")

        # Show metadata if available
        if active_phase.metadata:
            status_text.append("\nMetadata:\n", style="bold dim")
            for key, value in active_phase.metadata.items():
                status_text.append(f"  {key}: {value}\n", style="dim")

        return Panel(status_text, title="Current Phase", border_style="cyan")

    def _create_footer(self) -> Panel:
        """Create the footer panel."""
        events = self.collector.get_events()

        # Count phases by status
        status_counts = {}
        for event in events:
            status = event.status
            status_counts[status] = status_counts.get(status, 0) + 1

        footer_text = Text()

        if status_counts:
            status_parts = []
            for status, count in status_counts.items():
                icon = self._get_status_icon(status)
                color = self._get_status_color(status)
                status_parts.append(f"{icon} {count}")

            footer_text.append("Status: ", style="bold")
            footer_text.append(" │ ".join(status_parts), style="white")
        else:
            footer_text.append("Ready to start pipeline...", style="dim")

        return Panel(footer_text, border_style="dim")

    def _update_display(self):
        """Update the display with current data."""
        try:
            self.layout["header"].update(self._create_header())
            self.layout["timeline"].update(self._create_timeline())
            self.layout["details"].update(self._create_details())
            self.layout["footer"].update(self._create_footer())
        except Exception:
            # Silently handle any rendering errors to avoid breaking pipeline
            pass

    def _update_loop(self):
        """Background update loop."""
        while self._running:
            self._update_display()
            time.sleep(0.5)  # Update every 500ms

    def start(self):
        """Start the visualization."""
        if self._running:
            return

        self._running = True
        self._update_display()  # Initial render

        # Start live display
        self._live = Live(self.layout, console=self.console, refresh_per_second=2)
        self._live.start()

        # Start update thread
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()

    def stop(self):
        """Stop the visualization."""
        self._running = False

        # Render final state before stopping
        if self._live:
            self._update_display()
            time.sleep(0.1)  # Brief pause to show final state
            self._live.stop()
            self._live = None

        if self._update_thread:
            self._update_thread.join(timeout=1)
            self._update_thread = None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def create_terminal_viz(collector: TelemetryCollector = None) -> TerminalVisualizer:
    """Create a new terminal visualizer instance."""
    return TerminalVisualizer(collector)


# Helper function for simple visualization
def visualize_pipeline(collector: TelemetryCollector = None) -> TerminalVisualizer:
    """
    Create and start a terminal visualizer.

    Returns the visualizer instance which should be stopped when done.
    """
    viz = create_terminal_viz(collector)
    viz.start()
    return viz