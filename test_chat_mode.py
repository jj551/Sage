#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

from src.agent_core.agent import SageAgent

print("=" * 70)
print("Sage - 交互模式测试 (优化版)")
print("=" * 70)

print("\n[初始化]")
agent = SageAgent()
session_id = agent.create_session()
print(f"   ✓ 会话已创建: {session_id}")
print(f"   ✓ 使用模型: {agent.model}")

print("\n" + "=" * 70)
print("测试 1: 加载数据")
print("=" * 70)
print("> load sales data from sales_sample.csv")

result = agent.process_message("load sales data from sales_sample.csv")
print(f"\n结果:")
print(f"  计划步骤: {[s['action'] for s in result['plan']]}")
if result['results']:
    last_result = result['results'][-1]
    print(f"  状态: {last_result['status']}")
    if last_result['status'] == 'success' and 'result' in last_result:
        res = last_result['result']
        if 'overview' in res:
            print(f"  数据大小: {res['overview']['shape'][0]} 行 × {res['overview']['shape'][1]} 列")
            print(f"  列名: {', '.join(res['overview']['columns'])}")

print("\n" + "=" * 70)
print("测试 2: 描述性统计 (数据已加载)")
print("=" * 70)
print("> show descriptive statistics")

result = agent.process_message("show descriptive statistics")
print(f"\n结果:")
print(f"  计划步骤: {[s['action'] for s in result['plan']]}")

print("\n" + "=" * 70)
print("测试 3: 相关性分析 (数据已加载)")
print("=" * 70)
print("> show correlation analysis")

result = agent.process_message("show correlation analysis")
print(f"\n结果:")
print(f"  计划步骤: {[s['action'] for s in result['plan']]}")

print("\n" + "=" * 70)
print("测试 4: 查询帮助")
print("=" * 70)
print("> what can you help me with?")

result = agent.process_message("what can you help me with?")
print(f"\n结果:")
print(f"  计划步骤: {[s['action'] for s in result['plan']]}")

print("\n" + "=" * 70)
print("测试 5: 成本统计")
print("=" * 70)
cost = agent.get_cost_summary()
print(f"全局调用次数: {cost['global']['llm_calls']}")
print(f"全局总 Token: {cost['global']['total_tokens']}")

print("\n" + "=" * 70)
print("✓ 所有交互测试完成！")
print("=" * 70)
