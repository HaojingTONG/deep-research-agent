#!/usr/bin/env python3
"""
Test script for telemetry and visualization system.

Tests the core functionality of the telemetry collector and terminal visualization
to ensure proper event recording and rendering.
"""

import time
import unittest
from datetime import datetime
from utils.telemetry import TelemetryCollector, PhaseStatus, record_phase, record_skip
from utils.terminal_viz import TerminalVisualizer
from rich.console import Console


class TestTelemetryCollector(unittest.TestCase):
    """Test cases for TelemetryCollector."""

    def setUp(self):
        """Set up test fixtures."""
        from utils.telemetry import get_telemetry_collector
        self.collector = get_telemetry_collector()
        self.collector.clear()  # Clear for each test

    def test_pipeline_timing(self):
        """Test pipeline timing functionality."""
        self.collector.set_pipeline_start()
        time.sleep(0.1)  # Small delay
        duration = self.collector.get_pipeline_duration()

        self.assertIsNotNone(duration)
        self.assertGreater(duration, 0.05)  # Should be at least 50ms
        self.assertLess(duration, 1.0)      # Should be less than 1 second

    def test_phase_recording(self):
        """Test basic phase event recording."""
        # Start a phase
        event = self.collector.start_phase("Test Phase", notes="Testing basic functionality")

        # Check event is created correctly
        self.assertEqual(event.phase_name, "Test Phase")
        self.assertEqual(event.status, PhaseStatus.RUNNING)
        self.assertEqual(event.notes, "Testing basic functionality")
        self.assertIsNone(event.duration)

        # Check phase is in active list
        active_phases = self.collector.get_active_phases()
        self.assertEqual(len(active_phases), 1)
        self.assertEqual(active_phases[0].phase_name, "Test Phase")

        # End the phase
        time.sleep(0.05)  # Small delay to measure duration
        self.collector.end_phase("Test Phase", PhaseStatus.SUCCESS, notes="Completed successfully")

        # Check phase is no longer active
        active_phases = self.collector.get_active_phases()
        self.assertEqual(len(active_phases), 0)

        # Check final event state
        events = self.collector.get_events()
        self.assertEqual(len(events), 1)
        final_event = events[0]

        self.assertEqual(final_event.status, PhaseStatus.SUCCESS)
        self.assertEqual(final_event.notes, "Completed successfully")
        self.assertIsNotNone(final_event.duration)
        self.assertGreater(final_event.duration, 0.02)  # Should be at least 20ms

    def test_context_manager(self):
        """Test the record_phase context manager."""
        with record_phase("Context Test", notes="Testing context manager"):
            time.sleep(0.05)

        events = self.collector.get_events()
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertEqual(event.phase_name, "Context Test")
        self.assertEqual(event.status, PhaseStatus.SUCCESS)
        self.assertIsNotNone(event.duration)
        self.assertGreater(event.duration, 0.02)

    def test_context_manager_with_exception(self):
        """Test context manager properly handles exceptions."""
        try:
            with record_phase("Error Test", notes="Testing error handling"):
                raise ValueError("Test error")
        except ValueError:
            pass  # Expected

        events = self.collector.get_events()
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertEqual(event.phase_name, "Error Test")
        self.assertEqual(event.status, PhaseStatus.FAILED)
        self.assertIn("Error: Test error", event.notes)

    def test_nested_phases(self):
        """Test nested phase recording."""
        # Start parent phase
        with record_phase("Parent Phase", notes="Main operation"):
            time.sleep(0.02)

            # Start nested phase
            with record_phase("Child Phase", notes="Recovery operation", parent_phase="Parent Phase"):
                time.sleep(0.02)

        events = self.collector.get_events()
        self.assertEqual(len(events), 2)

        # Find parent and child events
        parent_event = next(e for e in events if e.phase_name == "Parent Phase")
        child_event = next(e for e in events if e.phase_name == "Child Phase")

        self.assertIsNone(parent_event.parent_phase)
        self.assertEqual(child_event.parent_phase, "Parent Phase")
        self.assertEqual(parent_event.status, PhaseStatus.SUCCESS)
        self.assertEqual(child_event.status, PhaseStatus.SUCCESS)

    def test_skip_recording(self):
        """Test phase skip recording."""
        record_skip("Skipped Phase", "Not needed in test mode")

        events = self.collector.get_events()
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertEqual(event.phase_name, "Skipped Phase")
        self.assertEqual(event.status, PhaseStatus.SKIPPED)
        self.assertIn("Skipped: Not needed in test mode", event.notes)

    def test_event_serialization(self):
        """Test event serialization to dict."""
        with record_phase("Serialization Test", model_used="gpt-4", test_metadata="value"):
            pass

        events = self.collector.get_events()
        event_dict = events[0].to_dict()

        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict["phase_name"], "Serialization Test")
        self.assertEqual(event_dict["status"], "success")
        self.assertEqual(event_dict["model_used"], "gpt-4")
        self.assertIn("test_metadata", event_dict["metadata"])
        self.assertEqual(event_dict["metadata"]["test_metadata"], "value")


class TestTerminalVisualization(unittest.TestCase):
    """Test cases for terminal visualization."""

    def setUp(self):
        """Set up test fixtures."""
        self.collector = TelemetryCollector()
        self.collector.clear()

    def test_visualization_creation(self):
        """Test that visualization can be created without errors."""
        viz = TerminalVisualizer(self.collector)
        self.assertIsNotNone(viz)
        self.assertEqual(viz.collector, self.collector)

    def test_visualization_with_dummy_console(self):
        """Test visualization rendering with dummy console."""
        # Create console that records output instead of printing
        console = Console(record=True)

        viz = TerminalVisualizer(self.collector)
        viz.console = console  # Replace with recording console

        # Add some test data
        self.collector.set_pipeline_start()
        with record_phase("Test Phase 1", notes="First test phase"):
            time.sleep(0.01)

        with record_phase("Test Phase 2", notes="Second test phase"):
            time.sleep(0.01)

        # Test that update_display doesn't crash
        try:
            viz._update_display()
            success = True
        except Exception as e:
            success = False
            error = str(e)

        self.assertTrue(success, f"Visualization update failed: {error if not success else ''}")

        # Check that console recorded some output
        recorded = console.export_text()
        self.assertGreater(len(recorded), 0, "Console should have recorded some output")

    def test_status_formatting(self):
        """Test status icon and color formatting."""
        viz = TerminalVisualizer(self.collector)

        # Test status icons
        self.assertEqual(viz._get_status_icon(PhaseStatus.SUCCESS), "✅")
        self.assertEqual(viz._get_status_icon(PhaseStatus.FAILED), "❌")
        self.assertEqual(viz._get_status_icon(PhaseStatus.RUNNING), "🔄")
        self.assertEqual(viz._get_status_icon(PhaseStatus.SKIPPED), "⏭️")

        # Test status colors
        self.assertEqual(viz._get_status_color(PhaseStatus.SUCCESS), "green")
        self.assertEqual(viz._get_status_color(PhaseStatus.FAILED), "red")
        self.assertEqual(viz._get_status_color(PhaseStatus.RUNNING), "cyan")

    def test_duration_formatting(self):
        """Test duration formatting for different time ranges."""
        viz = TerminalVisualizer(self.collector)

        # Test various duration formats
        self.assertEqual(viz._format_duration(None), "-")
        self.assertEqual(viz._format_duration(0.05), "50ms")  # < 1 second
        self.assertEqual(viz._format_duration(1.5), "1.5s")   # < 1 minute
        self.assertEqual(viz._format_duration(65.0), "1m 5.0s")  # > 1 minute


def run_smoke_test():
    """
    Run a smoke test of the complete visualization system.

    This test runs the visualization in the background for a short time
    to ensure it works with real phase execution.
    """
    print("Running telemetry and visualization smoke test...")

    collector = TelemetryCollector()
    collector.clear()
    collector.set_pipeline_start()

    # Start visualization in a way that doesn't block
    viz = TerminalVisualizer(collector)
    console = Console(record=True)  # Use recording console for testing
    viz.console = console

    try:
        viz.start()

        # Simulate a few phases
        with record_phase("Initialization", notes="Setting up test environment"):
            time.sleep(0.1)

        with record_phase("Data Processing", notes="Processing test data", model_used="test-model"):
            time.sleep(0.15)

            # Simulate a recovery
            with record_phase("Data Processing (Recovery)",
                            notes="Retrying failed operation",
                            parent_phase="Data Processing"):
                time.sleep(0.05)

        with record_phase("Finalization", notes="Cleaning up"):
            time.sleep(0.05)

        # Let visualization update
        time.sleep(0.5)

        # Check that events were recorded
        events = collector.get_events()
        assert len(events) >= 3, f"Expected at least 3 events, got {len(events)}"

        # Check that visualization rendered something
        output = console.export_text()
        assert len(output) > 0, "Visualization should have rendered some output"

        print("✅ Smoke test passed - telemetry and visualization working correctly")
        return True

    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False
    finally:
        viz.stop()


if __name__ == "__main__":
    # Run unit tests
    print("Running telemetry unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run smoke test
    print("\n" + "="*50)
    run_smoke_test()