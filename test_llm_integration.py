#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

from src.agent_core.agent import SageAgent

print("=" * 60)
print("Sage - LLM 驱动的数据分析测试")
print("=" * 60)

print("\n[1] 初始化 Sage Agent...")
agent = SageAgent()
print(f"   ✓ Agent 初始化完成")
print(f"   使用模型: {agent.model}")

print("\n[2] 创建会话...")
session_id = agent.create_session()
print(f"   ✓ 会话 ID: {session_id}")

print("\n[3] 加载示例数据...")
result = agent.load_dataset('file://sales_sample.csv')
if result['status'] == 'success':
    print(f"   ✓ 数据加载成功")
    print(f"   数据集大小: {result['overview']['shape'][0]} 行 × {result['overview']['shape'][1]} 列")
    print(f"   列名: {', '.join(result['overview']['columns'])}")
else:
    print(f"   ✗ 数据加载失败: {result}")
    sys.exit(1)

print("\n[4] 测试自然语言任务规划...")

test_queries = [
    "show me descriptive statistics",
    "plot the sales trend",
    "show correlation analysis",
    "what can you help me with?"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n   测试 {i}: '{query}'")
    try:
        response = agent.process_message(query)
        print(f"   ✓ 执行完成")
        print(f"   计划步骤数: {len(response['plan'])}")
        for j, step in enumerate(response['plan']):
            print(f"      步骤 {j+1}: {step['action']}")
    except Exception as e:
        print(f"   ✗ 执行失败: {e}")

print("\n[5] 成本统计...")
cost_summary = agent.get_cost_summary()
print(f"   全局调用次数: {cost_summary['global']['llm_calls']}")
print(f"   全局总 Token: {cost_summary['global']['total_tokens']}")
print(f"   会话调用次数: {cost_summary['session']['llm_calls']}")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)

print("\n提示:")
print("- 要使用真实 LLM，请复制 .env.example 为 .env 并填入 API Key")
print("- 设置 SAGE_MODEL=gpt-3.5-turbo 或其他模型")
print("- 运行: python main.py chat 进入交互模式")
