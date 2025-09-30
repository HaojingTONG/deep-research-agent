#!/usr/bin/env python3
"""
Demo script showing the terminal visualization system.

This demonstrates the telemetry and visualization capabilities
without running the full research pipeline.
"""

import time
from utils.telemetry import get_telemetry_collector, record_phase, record_skip, record_recovery
from utils.terminal_viz import visualize_pipeline


def demo_visualization():
    """
    Demo the visualization system with simulated agent execution.

    This shows how the terminal UI updates as agents run through
    various phases and status changes.
    """
    print("🔬 Starting Deep Research Agent Visualization Demo")
    print("\nThis demo shows the terminal visualization with simulated agent execution.")
    print("Watch the live timeline update as each phase completes!")
    print("Features: High-precision timing, nested operations, completion status")
    print("\nPress Ctrl+C to stop the demo at any time.\n")

    # Clear telemetry and start pipeline timing
    collector = get_telemetry_collector()
    collector.clear()
    collector.set_pipeline_start()

    # Start visualization
    viz = visualize_pipeline(collector)

    try:
        # Simulate the research pipeline phases with realistic timing
        with record_phase("Clarify Agent", notes="Processing and clarifying user query"):
            time.sleep(1.2)

        with record_phase("Research Brief Agent", notes="Creating comprehensive research brief"):
            time.sleep(0.8)

        with record_phase("Supervisor Planner Agent", notes="Generating targeted search plan"):
            time.sleep(0.6)

        # Simulate a longer evidence collection phase with subqueries
        with record_phase("Researcher Agent", notes="Collecting evidence from multiple sources", model_used="gpt-4"):
            time.sleep(0.3)
            # Simulate subquery processing
            for i in range(1, 4):
                with record_phase(f"Research Subquery {i}",
                                notes=f"Searching: 'Topic {i} recent evidence'",
                                parent_phase="Researcher Agent",
                                subquery_index=i,
                                total_subqueries=3):
                    time.sleep(0.8)

        with record_phase("Compress Conflict Agent", notes="Synthesizing findings and detecting conflicts"):
            time.sleep(1.1)

        # Simulate a phase that needs recovery
        try:
            with record_phase("Report Agent", notes="Generating initial report", model_used="gpt-4"):
                time.sleep(0.7)
                # Simulate a failure that triggers recovery
                raise Exception("Report quality below threshold")
        except Exception:
            # Recovery phase
            with record_recovery("Report Agent", "Quality threshold not met", model_used="gpt-4"):
                time.sleep(1.2)

        with record_phase("Evaluator Agent", notes="Assessing report quality across 6 dimensions"):
            time.sleep(0.6)

        # Skip some phases in demo mode
        record_skip("Model Router Agent", "Not needed in demo mode")
        record_skip("Observability Agent", "Demo complete")

        # Mark pipeline completion
        collector.set_pipeline_end("completed")

        print(f"\n🎉 Demo completed! The visualization showed {len(collector.get_events())} events.")
        print("In a real run, you would see live updates as each agent executes.")
        print("\nVisualization features demonstrated:")
        print("  ✅ Real-time timeline updates with high-precision timing")
        print("  🔄 Status indicators (success/failed/skipped/recovery)")
        print("  🔗 Nested operations (subqueries and recovery)")
        print("  ⏭️ Skipped phases")
        print("  🏁 Pipeline completion status")
        print("  📊 Overall pipeline progress and final summary")

        pipeline_duration = collector.get_pipeline_duration()
        print(f"\n📊 Final stats:")
        print(f"  Total runtime: {pipeline_duration:.2f}s")
        print(f"  Events recorded: {len(collector.get_events())}")
        print(f"  Pipeline status: {collector.get_pipeline_status()}")

        # Keep visualization running for a moment to see final state
        time.sleep(3)

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        collector.set_pipeline_end("failed")
    finally:
        viz.stop()
        print("\nVisualization stopped. Demo complete!")


if __name__ == "__main__":
    demo_visualization()