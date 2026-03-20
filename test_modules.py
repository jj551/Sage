#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

from src.agent_core.agent import SageAgent

print("=" * 80)
print("Sage - 所有工具模块综合测试")
print("=" * 80)

print("\n[初始化]")
agent = SageAgent()
session_id = agent.create_session()
print(f"   ✓ 会话 ID: {session_id}")

test_results = []

def test_module(name, description, func):
    print(f"\n{'=' * 80}")
    print(f"测试: {name}")
    print(f"描述: {description}")
    print(f"{'=' * 80}")
    try:
        result = func()
        print(f"✓ {name} 测试通过!")
        test_results.append((name, True, ""))
        return result
    except Exception as e:
        print(f"✗ {name} 测试失败: {e}")
        test_results.append((name, False, str(e)))
        return None

print("\n" + "=" * 80)
print("1. load_data - 加载数据集")
print("=" * 80)
load_result = test_module(
    "load_data",
    "从 sales_sample.csv 加载数据集",
    lambda: agent.load_dataset('file://sales_sample.csv')
)
if load_result and load_result['status'] == 'success':
    print(f"   ✓ 数据集大小: {load_result['overview']['shape'][0]} 行 × {load_result['overview']['shape'][1]} 列")
    print(f"   ✓ 列名: {', '.join(load_result['overview']['columns'])}")

print("\n" + "=" * 80)
print("2. descriptive_stats - 描述性统计分析")
print("=" * 80)
stats_result = test_module(
    "descriptive_stats",
    "对加载的数据进行描述性统计分析",
    lambda: agent._tool_descriptive_stats()
)
if stats_result and stats_result['status'] == 'success':
    print(f"   ✓ 统计结果获取成功")
    print(f"   ✓ 总结: {stats_result['result']['text_summary'][:200]}...")

print("\n" + "=" * 80)
print("3. plot_trend - 绘制趋势图")
print("=" * 80)
plot_result = test_module(
    "plot_trend",
    "绘制销售趋势图",
    lambda: agent._tool_plot_trend(column='date', value_column='sales')
)
if plot_result and plot_result['status'] == 'success':
    print(f"   ✓ 趋势图绘制成功")

print("\n" + "=" * 80)
print("4. correlation - 相关性分析与热力图")
print("=" * 80)
corr_result = test_module(
    "correlation",
    "进行相关性分析并生成热力图",
    lambda: agent._tool_correlation()
)
if corr_result and corr_result['status'] == 'success':
    print(f"   ✓ 相关性分析成功")

print("\n" + "=" * 80)
print("5. clean_data - 数据清洗")
print("=" * 80)
clean_result = test_module(
    "clean_data",
    "对数据进行清洗处理",
    lambda: agent._tool_clean_data(drop_na=False, fill_na='mean')
)
if clean_result and clean_result['status'] == 'success':
    print(f"   ✓ 数据清洗成功")
    print(f"   ✓ 数据形状: {agent.current_dataset.shape}")

print("\n" + "=" * 80)
print("6. feature_engineering - 特征工程")
print("=" * 80)
feat_result = test_module(
    "feature_engineering",
    "进行特征工程处理",
    lambda: agent._tool_feature_engineering(
        date_columns=['date'],
        categorical_columns=['region']
    )
)
if feat_result and feat_result['status'] == 'success':
    print(f"   ✓ 特征工程成功")
    print(f"   ✓ 新数据形状: {agent.current_dataset.shape}")

print("\n" + "=" * 80)
print("7. outlier_detection - 异常值检测")
print("=" * 80)
outlier_result = test_module(
    "outlier_detection",
    "使用 IQR 方法检测异常值",
    lambda: agent._tool_outlier_detection(column='sales', method='iqr')
)
if outlier_result and outlier_result['status'] == 'success':
    print(f"   ✓ 异常值检测成功")

print("\n" + "=" * 80)
print("8. respond - 自然语言响应")
print("=" * 80)
respond_result = test_module(
    "respond",
    "测试自然语言响应功能",
    lambda: agent._tool_respond(message="这是一个测试响应")
)
if respond_result and respond_result['status'] == 'success':
    print(f"   ✓ 响应成功: {respond_result['message']}")

print("\n" + "=" * 80)
print("测试结果总结")
print("=" * 80)

passed = 0
failed = 0

for name, success, error in test_results:
    status = "✓ 通过" if success else "✗ 失败"
    print(f"{name}: {status}")
    if not success:
        print(f"  错误: {error}")
    if success:
        passed += 1
    else:
        failed += 1

print("\n" + "=" * 80)
print(f"总计: {len(test_results)} 个测试")
print(f"通过: {passed} 个")
print(f"失败: {failed} 个")
print("=" * 80)

if failed == 0:
    print("\n🎉 所有模块测试通过！")
else:
    print(f"\n⚠️  有 {failed} 个测试失败，请检查")

print("=" * 80)
