"""
Telemetry system for Deep Research Agent.

Provides instrumentation for agent execution tracking, including timing,
status monitoring, and event collection for visualization purposes.
"""

import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager


class PhaseStatus(Enum):
    """Status of a pipeline phase execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    SKIPPED = "skipped"
    RECOVERED = "recovered"
    FAILED = "failed"


@dataclass
class PhaseEvent:
    """Represents a single phase execution event."""
    phase_name: str
    status: PhaseStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # seconds (high precision)
    notes: str = ""
    model_used: Optional[str] = None
    recovery_reason: Optional[str] = None
    parent_phase: Optional[str] = None  # for nested/recovery phases
    metadata: Dict[str, Any] = field(default_factory=dict)
    _start_perf: Optional[float] = field(default=None, init=False)  # perf_counter for precision
    _end_perf: Optional[float] = field(default=None, init=False)

    def __post_init__(self):
        """Calculate duration using high-precision timing if available."""
        if self._end_perf is not None and self._start_perf is not None:
            self.duration = self._end_perf - self._start_perf
        elif self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phase_name": self.phase_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "notes": self.notes,
            "model_used": self.model_used,
            "recovery_reason": self.recovery_reason,
            "parent_phase": self.parent_phase,
            "metadata": self.metadata
        }


class TelemetryCollector:
    """
    Central telemetry collector for pipeline execution.

    Thread-safe collector that manages phase events and provides
    real-time access to execution status for visualization.
    """

    def __init__(self):
        self._events: List[PhaseEvent] = []
        self._active_phases: Dict[str, PhaseEvent] = {}
        self._lock = threading.Lock()
        self._listeners: List[Callable[[PhaseEvent], None]] = []
        self._pipeline_start_time: Optional[datetime] = None
        self._pipeline_start_perf: Optional[float] = None
        self._pipeline_end_time: Optional[datetime] = None
        self._pipeline_end_perf: Optional[float] = None
        self._pipeline_status: Optional[str] = None  # "completed", "failed"

    def set_pipeline_start(self):
        """Mark the start of pipeline execution."""
        with self._lock:
            self._pipeline_start_time = datetime.now()
            self._pipeline_start_perf = time.perf_counter()
            self._pipeline_end_time = None
            self._pipeline_end_perf = None
            self._pipeline_status = None

    def set_pipeline_end(self, status: str = "completed"):
        """Mark the end of pipeline execution."""
        with self._lock:
            self._pipeline_end_time = datetime.now()
            self._pipeline_end_perf = time.perf_counter()
            self._pipeline_status = status

    def get_pipeline_duration(self) -> Optional[float]:
        """Get total pipeline duration in seconds (high precision)."""
        with self._lock:
            if self._pipeline_end_perf and self._pipeline_start_perf:
                # Pipeline completed, return final duration
                return self._pipeline_end_perf - self._pipeline_start_perf
            elif self._pipeline_start_perf:
                # Pipeline running, return current duration
                return time.perf_counter() - self._pipeline_start_perf
            else:
                return None

    def get_pipeline_status(self) -> Optional[str]:
        """Get pipeline completion status."""
        with self._lock:
            return self._pipeline_status

    def is_pipeline_complete(self) -> bool:
        """Check if pipeline has completed."""
        with self._lock:
            return self._pipeline_status is not None

    def add_listener(self, listener: Callable[[PhaseEvent], None]):
        """Add a listener for phase events."""
        with self._lock:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[PhaseEvent], None]):
        """Remove a listener for phase events."""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def _notify_listeners(self, event: PhaseEvent):
        """Notify all listeners of a phase event."""
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                # Silently ignore listener errors to avoid breaking pipeline
                pass

    def start_phase(self, phase_name: str, notes: str = "", model_used: str = None,
                   parent_phase: str = None, **metadata) -> PhaseEvent:
        """Start tracking a new phase."""
        start_perf = time.perf_counter()
        with self._lock:
            event = PhaseEvent(
                phase_name=phase_name,
                status=PhaseStatus.RUNNING,
                start_time=datetime.now(),
                notes=notes,
                model_used=model_used,
                parent_phase=parent_phase,
                metadata=metadata
            )
            event._start_perf = start_perf
            self._active_phases[phase_name] = event
            self._events.append(event)

        self._notify_listeners(event)
        return event

    def end_phase(self, phase_name: str, status: PhaseStatus, notes: str = "",
                 recovery_reason: str = None, **metadata):
        """End tracking of a phase."""
        end_perf = time.perf_counter()
        with self._lock:
            if phase_name in self._active_phases:
                event = self._active_phases[phase_name]
                event.end_time = datetime.now()
                event._end_perf = end_perf
                event.status = status
                if notes:
                    event.notes = notes
                if recovery_reason:
                    event.recovery_reason = recovery_reason
                event.metadata.update(metadata)
                event.__post_init__()  # Recalculate duration with perf_counter
                del self._active_phases[phase_name]

                self._notify_listeners(event)

    def get_events(self) -> List[PhaseEvent]:
        """Get all phase events (thread-safe copy)."""
        with self._lock:
            return self._events.copy()

    def get_active_phases(self) -> List[PhaseEvent]:
        """Get currently active phases (thread-safe copy)."""
        with self._lock:
            return list(self._active_phases.values())

    def get_phase_by_name(self, phase_name: str) -> Optional[PhaseEvent]:
        """Get a specific phase event by name."""
        with self._lock:
            # Return the most recent event with this name
            for event in reversed(self._events):
                if event.phase_name == phase_name:
                    return event
            return None

    def clear(self):
        """Clear all collected events (for testing)."""
        with self._lock:
            self._events.clear()
            self._active_phases.clear()
            self._pipeline_start_time = None
            self._pipeline_start_perf = None
            self._pipeline_end_time = None
            self._pipeline_end_perf = None
            self._pipeline_status = None


# Global telemetry collector instance
_global_collector = TelemetryCollector()


def get_telemetry_collector() -> TelemetryCollector:
    """Get the global telemetry collector instance."""
    return _global_collector


@contextmanager
def record_phase(phase_name: str, notes: str = "", model_used: str = None,
                parent_phase: str = None, **metadata):
    """
    Context manager for recording phase execution.

    Usage:
        with record_phase("Clarify Agent", notes="Processing user query"):
            # agent execution code
            pass
    """
    collector = get_telemetry_collector()
    event = collector.start_phase(phase_name, notes, model_used, parent_phase, **metadata)

    try:
        yield event
        collector.end_phase(phase_name, PhaseStatus.SUCCESS)
    except Exception as e:
        collector.end_phase(phase_name, PhaseStatus.FAILED,
                          notes=f"Error: {str(e)}")
        raise


def record_recovery(original_phase: str, recovery_reason: str, **metadata):
    """
    Record a recovery action for a phase.

    Args:
        original_phase: Name of the phase being recovered
        recovery_reason: Why recovery was needed
        **metadata: Additional metadata to record
    """
    recovery_phase_name = f"{original_phase} (Recovery)"
    return record_phase(recovery_phase_name,
                       notes=f"Recovery: {recovery_reason}",
                       parent_phase=original_phase,
                       recovery_reason=recovery_reason,
                       **metadata)


def record_skip(phase_name: str, reason: str, **metadata):
    """
    Record a skipped phase.

    Args:
        phase_name: Name of the phase being skipped
        reason: Why the phase was skipped
        **metadata: Additional metadata to record
    """
    collector = get_telemetry_collector()
    event = collector.start_phase(phase_name, notes=f"Skipped: {reason}", **metadata)
    collector.end_phase(phase_name, PhaseStatus.SKIPPED, notes=f"Skipped: {reason}")