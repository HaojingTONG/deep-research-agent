#!/usr/bin/env python3
"""
Deep Research Agent - CLI Entry Point

Command-line interface for the Deep Research Agent pipeline.
Provides access to the complete 10-phase research workflow.
"""

import sys
from pipeline import run_research_pipeline


def main():
    """
    CLI entry point for the Deep Research Agent.

    Handles command line arguments and invokes the appropriate pipeline execution.
    Supports full pipeline execution and various test modes for individual phases.
    """
    if len(sys.argv) < 2:
        print("Deep Research Agent - CLI Interface")
        print("\nUsage: python main.py '<your research query>' [options]")
        print("\nExample:")
        print("  python main.py 'Compare 2024–2025 evidence on ultra-processed foods and give recommendations.'")
        print("  python main.py 'Research query here' --viz  # Enable terminal visualization")
        print("\nOptions:")
        print("  --viz               Enable interactive terminal visualization")
        print("\nTest modes:")
        print("  --test-routing      Test model routing decisions")
        print("  --test-observability Test log summarization and audit trail generation")
        print("  --test-researcher   Test evidence collection (first subquery only)")
        print("  --test-compress     Test evidence compression and conflict analysis")
        print("  --test-report       Test report generation and evaluation")
        print("  --test-recovery     Test complete pipeline with recovery")
        print("\nFor more information, see README.md")
        return 1

    user_query = sys.argv[1]

    # Parse arguments
    test_mode = None
    enable_viz = False

    for arg in sys.argv[2:]:
        if arg.startswith("--test-"):
            test_mode = arg[7:]  # Remove "--test-" prefix
        elif arg == "--viz":
            enable_viz = True
        else:
            print(f"Error: Unknown argument '{arg}'")
            print("Use --viz for visualization or --test-[mode] for test modes. See --help for options.")
            return 1

    try:
        # Run the pipeline
        results = run_research_pipeline(user_query, test_mode, enable_viz=enable_viz)

        # Check execution status
        if results.get("execution_status") == "completed":
            print(f"\n✓ Pipeline execution completed successfully")
            if "evaluation_score" in results:
                print(f"✓ Report quality score: {results['evaluation_score']}/5.0")
            return 0
        elif results.get("execution_status") == "failed":
            print(f"\n✗ Pipeline execution failed: {results.get('error', 'Unknown error')}")
            return 1
        else:
            print(f"\n? Pipeline execution status: {results.get('execution_status', 'unknown')}")
            return 0

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)