#!/usr/bin/env python3
"""
Test script for Report Agent functionality
"""

from agents import ReportAgent

def test_report_generation():
    """Test Report Agent with mock compression results and evidence"""

    # Mock compression result from Compress + Conflict Agent
    mock_compression = {
        "clusters": [
            {"label": "Health Benefits", "items": [0, 1]},
            {"label": "Health Risks", "items": [2, 3]},
            {"label": "Recommendations", "items": [4, 5]}
        ],
        "key_findings": [
            "Potential health benefits of ultra-processed foods are limited and controversial [0,1]",
            "Multiple studies link ultra-processed foods to increased health risks including cardiovascular disease and metabolic disorders [2,3]",
            "Major health organizations recommend limiting ultra-processed food consumption [4,5]"
        ],
        "conflicts": [
            {
                "claim": "Ultra-processed foods may have some health benefits",
                "support": [0, 1],
                "counter": [2, 3],
                "reason": "Different study methodologies and populations; benefits may be limited to specific contexts"
            }
        ],
        "gaps": [
            "Need more 2024-2025 research on ultra-processed foods",
            "Need comprehensive systematic review of 2024-2025 evidence",
            "Need research on ultra-processed food effects across different age groups"
        ],
        "coverage_stats": {
            "unique_sources": 6,
            "domains": 4,
            "total_evidence": 6,
            "high_quality_sources": 5
        }
    }

    # Mock evidence list for citations
    mock_evidence = [
        {
            "url": "https://example-nutrition.com/benefits",
            "title": "Nutritional Advantages of Some Ultra-Processed Foods",
            "publisher": "Nutrition Journal",
            "date": "2024-03-15",
            "snippets": ["Some ultra-processed foods provide essential nutrients"],
            "quality": 4
        },
        {
            "url": "https://food-industry.com/processing",
            "title": "Food Processing and Convenience Benefits",
            "publisher": "Food Industry Magazine",
            "date": "2024-01-20",
            "snippets": ["Processing enhances food safety and shelf life"],
            "quality": 3
        },
        {
            "url": "https://pubmed.ncbi.nlm.nih.gov/12345",
            "title": "Ultra-processed Foods and Cardiovascular Disease Risk",
            "publisher": "PubMed",
            "date": "2024-06-10",
            "snippets": ["Increased cardiovascular disease risk with ultra-processed food consumption"],
            "quality": 5
        },
        {
            "url": "https://bmj.com/upf-cancer-study",
            "title": "Association Between Ultra-processed Food and Cancer Risk",
            "publisher": "BMJ",
            "date": "2024-02-28",
            "snippets": ["Links ultra-processed foods to increased cancer mortality"],
            "quality": 5
        },
        {
            "url": "https://who.int/nutrition/upf-guidelines",
            "title": "WHO Guidelines on Ultra-processed Food Consumption",
            "publisher": "World Health Organization",
            "date": "2024-04-05",
            "snippets": ["WHO recommends limiting ultra-processed food consumption"],
            "quality": 5
        },
        {
            "url": "https://fda.gov/dietary-guidelines",
            "title": "FDA Dietary Recommendations for Processed Foods",
            "publisher": "FDA",
            "date": "2024-01-15",
            "snippets": ["FDA advises choosing minimally processed options"],
            "quality": 5
        }
    ]

    user_query = "Compare 2024–2025 evidence on ultra-processed foods and give recommendations."

    # Test Report Agent
    report_agent = ReportAgent()

    print("=== TESTING REPORT AGENT ===")
    print("Testing different target audiences...\n")

    # Test for different audiences
    for audience in ["consumer", "executive", "researcher"]:
        print(f"=== REPORT FOR {audience.upper()} AUDIENCE ===")

        report = report_agent.generate_report(
            mock_compression,
            mock_evidence,
            user_query,
            audience
        )

        print(report)
        print("\n" + "="*80 + "\n")

        # Save individual reports
        filename = f"data/out/test_report_{audience}.md"
        try:
            import os
            os.makedirs("data/out", exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {filename}")
        except Exception as e:
            print(f"Could not save report: {e}")

if __name__ == "__main__":
    test_report_generation()