from typing import Dict, Any, Optional, List
import time

class LLMRequest:
    def __init__(self, messages: List[Dict], model_params: Dict = None, function_call: Optional[Dict] = None):
        self.messages = messages
        self.model_params = model_params if model_params is not None else {}
        self.function_call = function_call

class LLMResponse:
    def __init__(self, text: str, usage: Dict = None, function_call_result: Optional[Dict] = None):
        self.text = text
        self.usage = usage if usage is not None else {}
        self.function_call_result = function_call_result

class LLMAPIGateway:
    def __init__(self, adapter_factory, response_cache, rate_limiter, cost_tracker):
        self.adapter_factory = adapter_factory
        self.response_cache = response_cache
        self.rate_limiter = rate_limiter
        self.cost_tracker = cost_tracker

    def send_request(self, request: LLMRequest) -> LLMResponse:
        # 1. Check cache
        cache_key = self._generate_cache_key(request)
        cached_response = self.response_cache.get(cache_key)
        if cached_response:
            print("DEBUG: Cache hit for LLM request.")
            return cached_response

        # 2. Apply rate limiting
        self.rate_limiter.wait_for_allowance(request.model_params.get("model", "default"))

        # 3. Get adapter
        adapter = self.adapter_factory.get_adapter(request.model_params.get("model", "default"))

        start_time = time.time()
        # 4. Send request via adapter
        try:
            raw_response = adapter.send_request(request)
            response = self._process_raw_response(raw_response)
        except Exception as e:
            print(f"ERROR: LLM request failed: {e}")
            response = LLMResponse(text=f"Error: {e}")

        end_time = time.time()
        duration = end_time - start_time

        # 5. Track cost
        self.cost_tracker.track_usage(request.model_params.get("model", "default"), response.usage, duration)

        # 6. Cache response
        self.response_cache.set(cache_key, response)

        return response

    def _generate_cache_key(self, request: LLMRequest) -> str:
        # A simple cache key generation. In production, this would be more robust.
        return f"{request.messages}-{request.model_params}-{request.function_call}"

    def _process_raw_response(self, raw_response: Dict) -> LLMResponse:
        # Dummy processing for now
        text = raw_response.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = raw_response.get("usage", {})
        return LLMResponse(text=text, usage=usage)

if __name__ == '__main__':
    # Mock dependencies for testing
    class MockAdapterFactory:
        def get_adapter(self, model: str):
            class MockAdapter:
                def send_request(self, request: LLMRequest) -> Dict:
                    print(f"MockAdapter sending request for model: {model}")
                    # Simulate an LLM response
                    return {
                        "choices": [{"message": {"content": f"Mock response for: {request.messages[-1]['content']}"}}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 20}
                    }
            return MockAdapter()

    class MockResponseCache:
        def __init__(self):
            self._cache = {}
        def get(self, key: str):
            print(f"Cache get: {key}")
            return self._cache.get(key)
        def set(self, key: str, value: LLMResponse):
            print(f"Cache set: {key}")
            self._cache[key] = value

    class MockRateLimiter:
        def wait_for_allowance(self, model: str):
            print(f"RateLimiter: Waiting for allowance for {model}")

    class MockCostTracker:
        def track_usage(self, model: str, usage: Dict, duration: float):
            print(f"CostTracker: Tracked usage for {model}: {usage}, duration: {duration:.2f}s")

    mock_adapter_factory = MockAdapterFactory()
    mock_response_cache = MockResponseCache()
    mock_rate_limiter = MockRateLimiter()
    mock_cost_tracker = MockCostTracker()

    gateway = LLMAPIGateway(mock_adapter_factory, mock_response_cache, mock_rate_limiter, mock_cost_tracker)

    # Test sending a request
    print("--- Sending first request ---")
    req1 = LLMRequest(messages=[{"role": "user", "content": "Hello LLM"}], model_params={"model": "gpt-4"})
    res1 = gateway.send_request(req1)
    print(f"Response 1: {res1.text}")

    print("\n--- Sending second (cached) request ---")
    res2 = gateway.send_request(req1) # Should be cached
    print(f"Response 2: {res2.text}")

    print("\n--- Sending third (new) request ---")
    req3 = LLMRequest(messages=[{"role": "user", "content": "Tell me a joke"}], model_params={"model": "gpt-3.5"})
    res3 = gateway.send_request(req3)
    print(f"Response 3: {res3.text}")
