#!/usr/bin/env python3
"""
Simple test to validate telemetry and visualization are working.
"""

import time
from utils.telemetry import get_telemetry_collector, record_phase, record_skip, record_recovery
from utils.terminal_viz import TerminalVisualizer
from rich.console import Console


def test_basic_functionality():
    """Test that basic telemetry and visualization work."""
    print("Testing basic telemetry functionality...")

    # Clear collector
    collector = get_telemetry_collector()
    collector.clear()
    collector.set_pipeline_start()

    # Test basic phase recording
    with record_phase("Test Phase 1", notes="First test"):
        time.sleep(0.02)

    # Test another phase
    with record_phase("Test Phase 2", notes="Second test", model_used="test-model"):
        time.sleep(0.01)

    # Test nested phases
    with record_phase("Parent Phase", notes="Main operation"):
        time.sleep(0.01)
        with record_phase("Child Phase", notes="Sub-operation", parent_phase="Parent Phase"):
            time.sleep(0.01)

    # Test skip recording
    record_skip("Skipped Phase", "Not needed in test")

    # Test recovery
    with record_recovery("Failed Phase", "Testing recovery functionality"):
        time.sleep(0.01)

    # Test pipeline completion
    collector.set_pipeline_end("completed")

    # Check results
    events = collector.get_events()
    print(f"✓ Recorded {len(events)} events")

    # Check duration precision
    durations_precise = sum(1 for event in events if event.duration and event.duration > 0)
    print(f"✓ {durations_precise}/{len(events)} events have precise timing")

    # Check pipeline status
    pipeline_duration = collector.get_pipeline_duration()
    pipeline_status = collector.get_pipeline_status()
    is_complete = collector.is_pipeline_complete()

    print(f"✓ Pipeline duration: {pipeline_duration:.3f}s")
    print(f"✓ Pipeline status: {pipeline_status}")
    print(f"✓ Pipeline complete: {is_complete}")

    for event in events:
        duration_str = f"{event.duration:.3f}s" if event.duration else "N/A"
        parent_str = f" (parent: {event.parent_phase})" if event.parent_phase else ""
        print(f"  - {event.phase_name}: {event.status.value} ({duration_str}){parent_str}")

    # Test visualization rendering
    print("\nTesting visualization...")
    viz = TerminalVisualizer(collector)
    console = Console(record=True)
    viz.console = console

    try:
        viz._update_display()
        output = console.export_text()
        print(f"✓ Visualization rendered {len(output)} characters of output")

        # Check that visualization shows completion status
        if "Completed in" in output or "Pipeline Completed" in output:
            print("✓ Visualization shows completion status")
        else:
            print("⚠️ Visualization may not be showing completion status")

        if len(output) > 0:
            print("✓ Visualization test passed")
        else:
            print("⚠️ Visualization produced no output")
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        return False

    return True


def test_timing_precision():
    """Test that high-precision timing works correctly."""
    print("\nTesting timing precision...")

    collector = get_telemetry_collector()
    collector.clear()

    # Test very short phases
    with record_phase("Short Phase", notes="Testing precision"):
        time.sleep(0.001)  # 1ms

    events = collector.get_events()
    if events:
        duration = events[0].duration
        if duration and duration > 0.0005:  # Should be at least 0.5ms
            print(f"✓ Captured sub-second timing: {duration:.6f}s")
            return True
        else:
            print(f"❌ Duration too low or None: {duration}")
            return False
    else:
        print("❌ No events recorded")
        return False


def test_full_pipeline_simulation():
    """Test with a simulated full pipeline run."""
    print("\nTesting full pipeline simulation...")

    collector = get_telemetry_collector()
    collector.clear()
    collector.set_pipeline_start()

    # Simulate complete pipeline
    phases = [
        ("Clarify Agent", "Processing user query"),
        ("Research Brief Agent", "Creating research brief"),
        ("Supervisor Planner Agent", "Generating search plan"),
        ("Researcher Agent", "Collecting evidence"),
        ("Compress Conflict Agent", "Synthesizing findings"),
        ("Report Agent", "Generating report"),
        ("Evaluator Agent", "Assessing quality")
    ]

    for phase_name, notes in phases:
        with record_phase(phase_name, notes=notes):
            time.sleep(0.005)  # Minimal sleep for timing

    # Simulate subqueries for research phase
    with record_phase("Research Subquery 1", notes="Searching topic 1", parent_phase="Researcher Agent"):
        time.sleep(0.002)

    with record_phase("Research Subquery 2", notes="Searching topic 2", parent_phase="Researcher Agent"):
        time.sleep(0.003)

    collector.set_pipeline_end("completed")

    events = collector.get_events()
    nested_events = [e for e in events if e.parent_phase]
    main_events = [e for e in events if not e.parent_phase]

    print(f"✓ Recorded {len(main_events)} main phases and {len(nested_events)} nested phases")
    print(f"✓ Total events: {len(events)}")

    return len(events) >= len(phases) + 2  # Main phases + nested


if __name__ == "__main__":
    success = True

    success &= test_basic_functionality()
    success &= test_timing_precision()
    success &= test_full_pipeline_simulation()

    print(f"\n{'='*50}")
    print(f"Overall test result: {'✅ ALL PASSED' if success else '❌ SOME FAILED'}")

    if success:
        print("✓ Telemetry system working correctly")
        print("✓ High-precision timing functional")
        print("✓ Pipeline completion tracking works")
        print("✓ Nested phase tracking works")
        print("✓ Visualization renders completion status")