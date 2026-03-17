from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
from .llm_api_gateway import LLMRequest

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

class LLMAdapter(ABC):
    @abstractmethod
    def send_request(self, request: LLMRequest) -> Dict:
        """Sends a request to the LLM and returns the raw response."""
        pass

class OpenAIAdapter(LLMAdapter):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        
        if HAS_OPENAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None
    
    def send_request(self, request: LLMRequest) -> Dict:
        model = request.model_params.get('model', 'gpt-3.5-turbo')
        temperature = request.model_params.get('temperature', 0.7)
        max_tokens = request.model_params.get('max_tokens', 1000)
        
        print(f"OpenAIAdapter: Sending request for model {model}")
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=request.messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return {
                    "choices": [{"message": {"content": response.choices[0].message.content}}],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens
                    },
                    "model": response.model
                }
            except Exception as e:
                print(f"OpenAI API error: {e}, falling back to mock")
        
        return {
            "choices": [{"message": {"content": f"[Mock] OpenAI response for: {request.messages[-1]['content']}"}}],
            "usage": {"prompt_tokens": 15, "completion_tokens": 25},
            "model": model
        }

class AnthropicAdapter(LLMAdapter):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if HAS_ANTHROPIC and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
    
    def send_request(self, request: LLMRequest) -> Dict:
        model = request.model_params.get('model', 'claude-3-haiku-20240307')
        max_tokens = request.model_params.get('max_tokens', 1024)
        
        print(f"AnthropicAdapter: Sending request for model {model}")
        
        if self.client:
            try:
                system_message = ""
                user_messages = []
                
                for msg in request.messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    else:
                        user_messages.append({"role": msg["role"], "content": msg["content"]})
                
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_message,
                    messages=user_messages
                )
                return {
                    "choices": [{"message": {"content": response.content[0].text}}],
                    "usage": {
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens
                    },
                    "model": response.model
                }
            except Exception as e:
                print(f"Anthropic API error: {e}, falling back to mock")
        
        return {
            "choices": [{"message": {"content": f"[Mock] Anthropic response for: {request.messages[-1]['content']}"}}],
            "usage": {"prompt_tokens": 20, "completion_tokens": 30},
            "model": model
        }

class DeepSeekAdapter(LLMAdapter):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        if HAS_OPENAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None
    
    def send_request(self, request: LLMRequest) -> Dict:
        model = request.model_params.get('model', 'deepseek-chat')
        temperature = request.model_params.get('temperature', 0.7)
        max_tokens = request.model_params.get('max_tokens', 1000)
        
        print(f"DeepSeekAdapter: Sending request for model {model}")
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=request.messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return {
                    "choices": [{"message": {"content": response.choices[0].message.content}}],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens
                    },
                    "model": response.model
                }
            except Exception as e:
                print(f"DeepSeek API error: {e}, falling back to mock")
        
        return {
            "choices": [{"message": {"content": f"[Mock] DeepSeek response for: {request.messages[-1]['content']}"}}],
            "usage": {"prompt_tokens": 15, "completion_tokens": 25},
            "model": model
        }

class OllamaAdapter(LLMAdapter):
    def __init__(self, base_url: str = "http://localhost:11434", api_key: Optional[str] = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.api_key = api_key or os.getenv("OLLAMA_API_KEY")
        self._session = None
    
    def _get_session(self):
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
            except ImportError:
                pass
        return self._session
    
    def send_request(self, request: LLMRequest) -> Dict:
        model = request.model_params.get('model', 'llama2')
        temperature = request.model_params.get('temperature', 0.7)
        max_tokens = request.model_params.get('max_tokens', 1000)
        
        print(f"OllamaAdapter: Sending request for model {model}")
        
        session = self._get_session()
        if session:
            try:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = session.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": model,
                        "messages": request.messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=60
                )
                response.raise_for_status()
                result = response.json()
                
                usage = result.get("usage", {"prompt_tokens": 10, "completion_tokens": 15})
                
                return {
                    "choices": result.get("choices", []),
                    "usage": usage,
                    "model": result.get("model", model)
                }
            except Exception as e:
                print(f"Ollama /v1/chat/completions API error: {e}, trying old /api/generate endpoint")
                try:
                    prompt = "\n".join([f"{m['role']}: {m['content']}" for m in request.messages])
                    response = session.post(
                        f"{self.base_url}/api/generate",
                        json={"model": model, "prompt": prompt, "stream": False},
                        timeout=60
                    )
                    response.raise_for_status()
                    result = response.json()
                    return {
                        "choices": [{"message": {"content": result.get("response", "")}}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 15},
                        "model": model
                    }
                except Exception as e2:
                    print(f"Ollama /api/generate API error: {e2}, falling back to mock")
        
        return {
            "choices": [{"message": {"content": f"[Mock] Ollama response for: {request.messages[-1]['content']}"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 15},
            "model": model
        }

class MockAdapter(LLMAdapter):
    def send_request(self, request: LLMRequest) -> Dict:
        print(f"MockAdapter: Sending request for model {request.model_params.get('model', 'default')}")
        
        user_msg = request.messages[-1]['content'] if request.messages else ""
        full_context = str(request.messages)
        
        data_loaded = "Current Dataset Loaded: Yes" in full_context
        
        if "load" in user_msg.lower() and "data" in user_msg.lower():
            content = '[{"action": "load_data", "params": {"source": "file://sales_sample.csv"}}]'
        elif "stat" in user_msg.lower() or "describe" in user_msg.lower():
            if not data_loaded:
                content = '[{"action": "load_data", "params": {"source": "file://sales_sample.csv"}}, {"action": "descriptive_stats", "params": {}}]'
            else:
                content = '[{"action": "descriptive_stats", "params": {}}]'
        elif "plot" in user_msg.lower() or "chart" in user_msg.lower():
            if not data_loaded:
                content = '[{"action": "load_data", "params": {"source": "file://sales_sample.csv"}}, {"action": "plot_trend", "params": {"column": "date", "value_column": "sales"}}]'
            else:
                content = '[{"action": "plot_trend", "params": {"column": "date", "value_column": "sales"}}]'
        elif "correl" in user_msg.lower():
            if not data_loaded:
                content = '[{"action": "load_data", "params": {"source": "file://sales_sample.csv"}}, {"action": "correlation", "params": {}}]'
            else:
                content = '[{"action": "correlation", "params": {}}]'
        else:
            content = '[{"action": "respond", "params": {"message": "I can help you load data, run statistics, create plots, and analyze correlations!"}}]'
        
        return {
            "choices": [{"message": {"content": content}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            "model": "mock-model"
        }

class AdapterFactory:
    def __init__(self, config: Dict = None):
        self.config = config if config is not None else {}
        self._adapters = {
            "openai": OpenAIAdapter(),
            "anthropic": AnthropicAdapter(),
            "deepseek": DeepSeekAdapter(),
            "ollama": OllamaAdapter(),
            "mock": MockAdapter(),
        }
    
    def get_adapter(self, model_name: str) -> LLMAdapter:
        if "gpt" in model_name:
            return self._adapters["openai"]
        elif "claude" in model_name:
            return self._adapters["anthropic"]
        elif "deepseek" in model_name.lower():
            return self._adapters["deepseek"]
        elif "llama" in model_name or "ollama" in model_name or "mistral" in model_name.lower() or "gemma" in model_name.lower():
            return self._adapters["ollama"]
        elif "mock" in model_name:
            return self._adapters["mock"]
        else:
            return self._adapters["mock"] 

if __name__ == '__main__':
    # For testing, we need LLMRequest which is in llm_api_gateway.py
    # We'll define a simple one here for standalone testing of adapters.
    class TestLLMRequest:
        def __init__(self, messages: List[Dict], model_params: Dict = None):
            self.messages = messages
            self.model_params = model_params if model_params is not None else {}

    factory = AdapterFactory()

    print("--- Testing OpenAI Adapter ---")
    openai_request = TestLLMRequest(messages=[{"role": "user", "content": "Hello"}], model_params={"model": "gpt-4"})
    openai_adapter = factory.get_adapter("gpt-4")
    print(openai_adapter.send_request(openai_request))

    print("\n--- Testing Anthropic Adapter ---")
    anthropic_request = TestLLMRequest(messages=[{"role": "user", "content": "Hi"}], model_params={"model": "claude-3"})
    anthropic_adapter = factory.get_adapter("claude-3")
    print(anthropic_adapter.send_request(anthropic_request))

    print("\n--- Testing Ollama Adapter ---")
    ollama_request = TestLLMRequest(messages=[{"role": "user", "content": "Hey"}], model_params={"model": "llama2"})
    ollama_adapter = factory.get_adapter("llama2")
    print(ollama_adapter.send_request(ollama_request))

    print("\n--- Testing Mock Adapter ---")
    mock_request = TestLLMRequest(messages=[{"role": "user", "content": "Test"}], model_params={"model": "mock-test"})
    mock_adapter = factory.get_adapter("mock-test")
    print(mock_adapter.send_request(mock_request))
