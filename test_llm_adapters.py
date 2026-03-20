#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

from src.llm_gateway.adapters import AdapterFactory

print("=" * 80)
print("Sage - LLM 适配器测试")
print("=" * 80)

class TestLLMRequest:
    def __init__(self, messages, model_params=None):
        self.messages = messages
        self.model_params = model_params if model_params is not None else {}

factory = AdapterFactory()

test_models = [
    ("OpenAI - GPT-4", "gpt-4"),
    ("Anthropic - Claude", "claude-3-haiku-20240307"),
    ("DeepSeek - Chat", "deepseek-chat"),
    ("DeepSeek - Coder", "deepseek-coder"),
    ("Ollama - Llama2", "llama2"),
    ("Ollama - Llama3", "llama3"),
    ("Ollama - Mistral", "mistral"),
    ("Ollama - Gemma", "gemma"),
    ("Mock Model", "mock-model"),
]

test_messages = [
    {"role": "system", "content": "You are a helpful data analysis assistant."},
    {"role": "user", "content": "What can you help me with?"}
]

for name, model_name in test_models:
    print(f"\n{'=' * 80}")
    print(f"测试: {name}")
    print(f"模型名称: {model_name}")
    print(f"{'=' * 80}")
    
    try:
        adapter = factory.get_adapter(model_name)
        request = TestLLMRequest(
            messages=test_messages,
            model_params={"model": model_name, "temperature": 0.7, "max_tokens": 100}
        )
        
        response = adapter.send_request(request)
        
        print(f"✓ 请求成功发送")
        print(f"✓ 响应包含 {len(response.get('choices', []))} 个选择")
        
        if response.get('choices'):
            content = response['choices'][0]['message']['content']
            print(f"✓ 响应内容: {content[:100]}{'...' if len(content) > 100 else ''}")
        
        if 'usage' in response:
            print(f"✓ Token 使用: 提示={response['usage']['prompt_tokens']}, 完成={response['usage']['completion_tokens']}")
        
        print(f"\n✓ {name} 适配器测试通过！")
        
    except Exception as e:
        print(f"\n✗ {name} 适配器测试失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("所有 LLM 适配器测试完成！")
print("=" * 80)
