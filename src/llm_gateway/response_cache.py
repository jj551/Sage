from typing import Any, Dict
import collections
import time

class ResponseCache:
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl # Time to live in seconds
        self._cache = collections.OrderedDict() # Stores (response, timestamp)

    def _is_expired(self, timestamp: float) -> bool:
        return (time.time() - timestamp) > self.ttl

    def get(self, key: str) -> Any:
        if key in self._cache:
            response, timestamp = self._cache[key]
            if not self._is_expired(timestamp):
                self._cache.move_to_end(key) # Move to end to mark as recently used
                return response
            else:
                del self._cache[key] # Remove expired item
        return None

    def set(self, key: str, value: Any) -> None:
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False) # Remove LRU item
        self._cache[key] = (value, time.time())
        self._cache.move_to_end(key)

    def clear(self) -> None:
        self._cache.clear()

    def __len__(self):
        return len(self._cache)

    def __contains__(self, key: str):
        return self.get(key) is not None

if __name__ == '__main__':
    cache = ResponseCache(max_size=3, ttl=2) # Small cache for testing

    print("--- Adding items to cache ---")
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    print(f"Cache size: {len(cache)}")
    print(f"Cache contains key1: {'key1' in cache}")

    print("\n--- Accessing items ---")
    print(f"Get key2: {cache.get('key2')}") # key2 becomes MRU
    print(f"Cache order (least recently used to most): {list(cache._cache.keys())}")

    print("\n--- Adding item beyond max_size (key1 should be evicted) ---")
    cache.set("key4", "value4")
    print(f"Cache size: {len(cache)}")
    print(f"Cache contains key1: {'key1' in cache}") # Should be False
    print(f"Cache order: {list(cache._cache.keys())}")

    print("\n--- Testing TTL (wait for 3 seconds) ---")
    cache.set("key5", "value5")
    print(f"Cache contains key5 before expiry: {'key5' in cache}")
    time.sleep(3)
    print(f"Cache contains key5 after expiry: {'key5' in cache}") # Should be False

    print("\n--- Clearing cache ---")
    cache.clear()
    print(f"Cache size after clear: {len(cache)}")
