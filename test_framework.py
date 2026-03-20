import sys
sys.path.insert(0, 'src')
from src.agent_core.agent import SageAgent

print('=== Testing Sage Agent ===')
agent = SageAgent()
session_id = agent.create_session()
print(f'Created session: {session_id}')

print('\n--- Loading sample data ---')
result = agent.load_dataset('file://sales_sample.csv')
print(f'Load result status: {result["status"]}')

if result['status'] == 'success':
    print(f'Dataset loaded: {result["overview"]["shape"][0]} rows × {result["overview"]["shape"][1]} columns')
    print(f'Columns: {result["overview"]["columns"]}')
    
    print('\n--- Running descriptive stats ---')
    stats_result = agent._tool_descriptive_stats()
    print(f'Stats status: {stats_result["status"]}')
    if stats_result['status'] == 'success':
        print(f'Summary: {stats_result["result"]["text_summary"]}')

print('\n--- All tests passed! ---')
