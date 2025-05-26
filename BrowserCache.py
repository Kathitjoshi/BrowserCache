# Problem Statement:
# Modern web browsers use caching to reduce load times and improve user experience.
# • Simulate a browser cache that stores the last N visited web pages.
# • Implement LRU (Least Recently Used) caching policy to evict the least-used page.
# • Analyse hit/miss rates for different cache sizes.

from collections import OrderedDict
import random

class LRUCache:
    def __init__(self, capacity):
        # Initialize the LRU cache with a given capacity
        self.cache = OrderedDict()  # Maintains insertion/access order
        self.capacity = capacity
        self.hits = 0  # Count of cache hits
        self.misses = 0  # Count of cache misses

    def visit(self, page):
        # Simulates visiting a web page
        if page in self.cache:
            # Page found in cache: HIT
            self.cache.move_to_end(page)  # Move page to the end (most recently used)
            self.hits += 1
        else:
            # Page not found in cache: MISS
            self.misses += 1
            if len(self.cache) >= self.capacity:
                # Cache full: remove least recently used (first item)
                self.cache.popitem(last=False)
            # Add new page to cache
            self.cache[page] = True

    def get_hit_miss_rates(self):
        # Compute and return cache performance stats
        total = self.hits + self.misses
        return {
            'Hits': self.hits,
            'Misses': self.misses,
            'Hit Rate': self.hits / total if total else 0,
            'Miss Rate': self.misses / total if total else 0
        }

def simulate_browser_cache(page_sequence, cache_sizes):
    # Simulate LRU cache behavior for various cache sizes
    for size in cache_sizes:
        lru = LRUCache(size)  # Create LRU cache with current size
        for page in page_sequence:
            lru.visit(page)  # Visit each page in the sequence
        stats = lru.get_hit_miss_rates()
        
        # Display results
        print(f"\nCache Size: {size}")
        print(f"Total Requests: {len(page_sequence)}")
        print(f"Hits: {stats['Hits']}, Misses: {stats['Misses']}")
        print(f"Hit Rate: {stats['Hit Rate']:.2%}, Miss Rate: {stats['Miss Rate']:.2%}")

if __name__ == "__main__":
    # Generate a list of 100 page visits with random page IDs from 1 to 20
    pages = [f"page{random.randint(1, 20)}" for _ in range(100)]
    
    # Test with different cache sizes
    cache_sizes = [2, 5, 10, 20]
    
    # Run the simulation
    simulate_browser_cache(pages, cache_sizes)
