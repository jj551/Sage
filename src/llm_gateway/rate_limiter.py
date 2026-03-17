import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Any

class RateLimiter:
    def __init__(self, rates: Dict[str, Dict[str, Any]] = None):
        # rates example: {"default": {"tokens_per_second": 100, "burst": 200}, "gpt-4": {"tokens_per_second": 10, "burst": 20}}
        self.rates = defaultdict(lambda: {"tokens_per_second": 100, "burst": 200}) # Default rate
        if rates:
            self.rates.update(rates)
        
        self.tokens = defaultdict(lambda: 0.0)
        self.last_refill_time = defaultdict(lambda: time.time())
        self.locks = defaultdict(Lock)

    def _refill_tokens(self, model: str):
        with self.locks[model]:
            now = time.time()
            time_passed = now - self.last_refill_time[model]
            rate_config = self.rates[model]
            
            new_tokens = time_passed * rate_config["tokens_per_second"]
            self.tokens[model] = min(rate_config["burst"], self.tokens[model] + new_tokens)
            self.last_refill_time[model] = now

    def wait_for_allowance(self, model: str, cost: int = 1):
        self._refill_tokens(model)
        
        while self.tokens[model] < cost:
            time_to_wait = (cost - self.tokens[model]) / self.rates[model]["tokens_per_second"]
            print(f"RateLimiter: {model} rate limit hit. Waiting for {time_to_wait:.2f} seconds.")
            time.sleep(time_to_wait)
            self._refill_tokens(model) # Refill after waiting
        
        self.tokens[model] -= cost
        print(f"RateLimiter: {model} consumed {cost} tokens. Remaining: {self.tokens[model]:.2f}")

if __name__ == '__main__':
    # Test with default rates
    limiter = RateLimiter()

    print("--- Default rate limiting test (cost 1 token per request) ---")
    for i in range(5):
        print(f"Request {i+1}:")
        limiter.wait_for_allowance("default")
        time.sleep(0.1) # Simulate some work

    print("\n--- Test with a custom rate for 'gpt-4' (low rate) ---")
    custom_rates = {"gpt-4": {"tokens_per_second": 2, "burst": 5}}
    limiter_custom = RateLimiter(rates=custom_rates)

    for i in range(10):
        print(f"GPT-4 Request {i+1}:")
        limiter_custom.wait_for_allowance("gpt-4")
        # No sleep here, to hit the rate limit quickly and see it wait
