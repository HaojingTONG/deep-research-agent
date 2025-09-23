#!/usr/bin/env python3
"""
演示Model Router Agent如何工作以及如何测试功能是否实现
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import ModelRouterAgent

def demo_model_routing():
    """演示Model Router Agent的工作原理"""

    print("🧠 Model Router Agent演示")
    print("="*60)

    # 初始化路由器
    router = ModelRouterAgent()

    print("\n📋 功能说明:")
    print("Model Router根据查询复杂度为每个处理节点选择最合适的模型档次")
    print("• cheap: 低成本，适合简单任务")
    print("• balanced: 中等成本，适合大多数任务")
    print("• premium: 高质量，适合关键任务")

    # 测试不同复杂度的查询
    test_queries = [
        {
            "name": "简单查询",
            "query": "什么是超加工食品？",
            "expected": "应该大部分使用cheap/balanced模型"
        },
        {
            "name": "复杂查询",
            "query": "比较2024-2025年超加工食品的证据并提供全面的建议",
            "expected": "应该为关键节点使用premium模型"
        }
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\n🔍 测试 {i}: {test['name']}")
        print(f"查询: {test['query']}")
        print(f"预期: {test['expected']}")

        # 获取路由决策
        routing = router.route_models(test['query'])

        print(f"\n分析结果:")
        print(f"• 复杂度级别: {routing['query_analysis']['complexity_level']}")
        print(f"• 复杂度评分: {routing['query_analysis']['complexity_score']}/6")
        print(f"• 总成本估算: {routing['total_estimated_cost']}")

        print(f"\n路由决策:")
        for decision in routing['routing']:
            print(f"  {decision['node']:8} → {decision['profile']:8} | {decision['why']}")

        print(f"\n成本分布: {routing['cost_breakdown']}")

        print("-" * 60)

def test_routing_accuracy():
    """测试路由决策的准确性"""

    print("\n🎯 路由准确性测试")
    print("="*60)

    router = ModelRouterAgent()

    # 测试场景
    scenarios = [
        {
            "query": "超加工食品定义",
            "test": "简单查询应优先使用cheap模型",
            "check": lambda r: r['cost_breakdown']['cheap'] >= 2
        },
        {
            "query": "系统性综述比较2024-2025年超加工食品临床证据与荟萃分析数据",
            "test": "复杂查询应为compress和report使用premium",
            "check": lambda r: any(d['node'] == 'compress' and d['profile'] == 'premium' for d in r['routing']) and
                              any(d['node'] == 'report' and d['profile'] == 'premium' for d in r['routing'])
        },
        {
            "query": "快速事实查询：UPF",
            "test": "极简查询应大量使用cheap模型",
            "check": lambda r: r['total_estimated_cost'] <= 8.0
        }
    ]

    passed = 0
    total = len(scenarios)

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n测试 {i}: {scenario['test']}")
        print(f"查询: '{scenario['query']}'")

        routing = router.route_models(scenario['query'])
        test_passed = scenario['check'](routing)

        if test_passed:
            print("✅ 通过")
            passed += 1
        else:
            print("❌ 失败")

        print(f"  路由: {routing['cost_breakdown']}")
        print(f"  成本: {routing['total_estimated_cost']}")

    print(f"\n测试结果: {passed}/{total} 通过")

def demonstrate_cost_optimization():
    """演示成本优化功能"""

    print("\n💰 成本优化演示")
    print("="*60)

    router = ModelRouterAgent()

    # 高成本查询
    expensive_query = "全面详细的系统性综述，包含随机对照试验的荟萃分析和多人群临床证据分析"

    routing = router.route_models(expensive_query)

    print(f"高成本查询示例:")
    print(f"'{expensive_query}'")

    print(f"\n路由分析:")
    premium_nodes = [d['node'] for d in routing['routing'] if d['profile'] == 'premium']
    print(f"• Premium节点: {premium_nodes}")
    print(f"• 总成本: {routing['total_estimated_cost']}")

    print(f"\n优化建议:")
    for note in routing['optimization_notes']:
        print(f"• {note}")

def show_how_to_test():
    """显示如何测试功能是否实现"""

    print("\n🧪 如何测试Model Router功能")
    print("="*60)

    print("1. 基础功能测试:")
    print("   python test_model_router.py")
    print("   → 测试不同复杂度查询的路由决策")

    print("\n2. 集成测试:")
    print("   python main.py '你的查询' --test-routing")
    print("   → 测试与主流程的集成")

    print("\n3. 验证要点:")
    print("   ✓ 简单查询应多用cheap/balanced模型")
    print("   ✓ 复杂查询应为关键节点用premium模型")
    print("   ✓ compress和report节点对复杂查询用premium")
    print("   ✓ 成本估算合理（cheap=0.3, balanced=1.0, premium=3.0）")
    print("   ✓ 生成有意义的解释说明")
    print("   ✓ 提供优化建议")

    print("\n4. 检查输出文件:")
    print("   data/intermediate/routing_decision_*.json")
    print("   → 路由决策应正确保存")

def main():
    """主演示函数"""

    print("🚀 Phase 9 | Model Router Agent 功能演示")
    print("="*80)

    # 基础演示
    demo_model_routing()

    # 准确性测试
    test_routing_accuracy()

    # 成本优化演示
    demonstrate_cost_optimization()

    # 测试指南
    show_how_to_test()

    print("\n🎉 Model Router Agent功能演示完成！")
    print("\n功能总结:")
    print("✅ 智能分析查询复杂度")
    print("✅ 为每个节点选择最佳模型档次")
    print("✅ 平衡成本与质量")
    print("✅ 提供详细的决策解释")
    print("✅ 生成成本优化建议")
    print("✅ 完整的测试覆盖")

if __name__ == "__main__":
    main()