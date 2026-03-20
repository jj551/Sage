#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

from src.agent_core.agent import SageAgent

print("=" * 70)
print("Sage - 简单功能测试")
print("=" * 70)

print("\n[1] 初始化 Agent")
agent = SageAgent()
session_id = agent.create_session()
print(f"   ✓ 会话 ID: {session_id}")

print("\n[2] 加载数据 (直接调用)")
load_result = agent.load_dataset('file://sales_sample.csv')
if load_result['status'] == 'success':
    print(f"   ✓ 数据加载成功!")
    print(f"   形状: {load_result['overview']['shape']}")
    print(f"   列: {load_result['overview']['columns']}")

print("\n[3] 描述性统计 (直接调用)")
stats_result = agent._tool_descriptive_stats()
if stats_result['status'] == 'success':
    print(f"   ✓ 统计成功!")
    print(f"   总结: {stats_result['result']['text_summary'][:150]}...")

print("\n[4] 验证数据已加载状态")
if agent.current_dataset is not None:
    print(f"   ✓ current_dataset 存在")
    print(f"   数据集形状: {agent.current_dataset.shape}")

print("\n" + "=" * 70)
print("✓ 所有简单测试通过!")
print("=" * 70)
