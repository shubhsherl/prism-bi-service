from collections import OrderedDict
import time

class InMemoryCache:
    def __init__(self, max_size=10):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key):
        value, ttl = self.cache.get(key, (None, None))
        if value is not None:
            # Check if the entry has expired
            if ttl is not None and time.time() > ttl:
                self.delete(key)
                return None
            # Move the accessed key to the end to maintain LRU order
            self.cache.move_to_end(key)
        return value

    def set(self, key, value, ttl_hours=None):
        if len(self.cache) >= self.max_size:
            # Remove the least recently used item (first item in the OrderedDict)
            self.cache.popitem(last=False)

        # Calculate the expiration time (TTL)
        ttl = None
        if ttl_hours is not None:
            ttl = time.time() + ttl_hours * 3600  # Convert hours to seconds

        self.cache[key] = (value, ttl)
        # Move the newly added or accessed key to the end
        self.cache.move_to_end(key)

    def delete(self, key):
        if key in self.cache:
            self.cache.pop(key)

    def contains(self, key):
        return key in self.cache