#!/usr/bin/env python3
"""
Enhanced Browser Cache Simulator with LRU Policy

This module simulates a browser cache using the Least Recently Used (LRU) 
eviction policy and provides comprehensive analysis of cache performance
across different scenarios and cache sizes.
"""

from collections import OrderedDict
import random
import time
import statistics
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple, Optional
import json


class LRUCache:
    """
    Implements an LRU (Least Recently Used) cache for web page simulation.
    
    The cache maintains pages in order of access, with the most recently
    accessed pages at the end and least recently accessed at the beginning.
    """
    
    def __init__(self, capacity: int):
        """
        Initialize the LRU cache.
        
        Args:
            capacity (int): Maximum number of pages the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Cache capacity must be positive")
            
        self.cache = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0
        self.access_times = []
        self.evicted_pages = []
        
    def visit(self, page: str) -> bool:
        """
        Visit a web page, updating cache state.
        
        Args:
            page (str): The page identifier
            
        Returns:
            bool: True if cache hit, False if cache miss
        """
        start_time = time.perf_counter()
        
        if page in self.cache:
            # Cache hit: move to end (most recently used)
            self.cache.move_to_end(page)
            self.hits += 1
            hit = True
        else:
            # Cache miss: add new page
            self.misses += 1
            
            if len(self.cache) >= self.capacity:
                # Evict least recently used page
                evicted_page, _ = self.cache.popitem(last=False)
                self.evicted_pages.append(evicted_page)
            
            # Add new page to cache
            self.cache[page] = {
                'first_access': time.time(),
                'access_count': 1
            }
            hit = False
            
        # Record access time for performance analysis
        access_time = time.perf_counter() - start_time
        self.access_times.append(access_time)
        
        return hit
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dict: Dictionary containing various cache metrics
        """
        total_requests = self.hits + self.misses
        
        return {
            'capacity': self.capacity,
            'total_requests': total_requests,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / total_requests if total_requests > 0 else 0,
            'miss_rate': self.misses / total_requests if total_requests > 0 else 0,
            'current_size': len(self.cache),
            'evictions': len(self.evicted_pages),
            'avg_access_time': statistics.mean(self.access_times) if self.access_times else 0,
            'cached_pages': list(self.cache.keys())
        }
    
    def clear(self):
        """Reset the cache to initial state."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.access_times.clear()
        self.evicted_pages.clear()


class BrowserCacheSimulator:
    """
    Simulates browser cache behavior with various access patterns and scenarios.
    """
    
    def __init__(self):
        self.results = {}
        
    @staticmethod
    def generate_realistic_page_sequence(num_requests: int, 
                                       num_unique_pages: int,
                                       locality_factor: float = 0.7) -> List[str]:
        """
        Generate a realistic web page access sequence with temporal locality.
        
        Args:
            num_requests (int): Total number of page requests
            num_unique_pages (int): Number of unique pages
            locality_factor (float): Probability of accessing recently visited pages
            
        Returns:
            List[str]: Sequence of page requests
        """
        pages = [f"page_{i}" for i in range(1, num_unique_pages + 1)]
        sequence = []
        recent_pages = []
        
        for _ in range(num_requests):
            if recent_pages and random.random() < locality_factor:
                # Access a recently visited page (temporal locality)
                page = random.choice(recent_pages[-5:])  # Last 5 pages
            else:
                # Access a random page
                page = random.choice(pages)
            
            sequence.append(page)
            
            # Update recent pages list
            if page in recent_pages:
                recent_pages.remove(page)
            recent_pages.append(page)
            
            # Keep only last 10 pages in recent list
            if len(recent_pages) > 10:
                recent_pages.pop(0)
                
        return sequence
    
    @staticmethod
    def generate_zipf_distribution(num_requests: int, 
                                 num_unique_pages: int, 
                                 alpha: float = 1.0) -> List[str]:
        """
        Generate page sequence following Zipf distribution (common in web traffic).
        
        Args:
            num_requests (int): Total number of requests
            num_unique_pages (int): Number of unique pages
            alpha (float): Zipf parameter (higher = more skewed)
            
        Returns:
            List[str]: Page sequence following Zipf distribution
        """
        pages = [f"page_{i}" for i in range(1, num_unique_pages + 1)]
        
        # Generate Zipf probabilities
        ranks = np.arange(1, num_unique_pages + 1)
        probabilities = 1 / (ranks ** alpha)
        probabilities = probabilities / probabilities.sum()
        
        # Generate sequence
        sequence = np.random.choice(pages, size=num_requests, p=probabilities)
        return sequence.tolist()
    
    def simulate_cache_sizes(self, 
                           page_sequence: List[str], 
                           cache_sizes: List[int],
                           scenario_name: str = "default") -> Dict:
        """
        Simulate cache performance across different cache sizes.
        
        Args:
            page_sequence (List[str]): Sequence of page requests
            cache_sizes (List[int]): List of cache sizes to test
            scenario_name (str): Name for this simulation scenario
            
        Returns:
            Dict: Results for each cache size
        """
        results = {}
        unique_pages = len(set(page_sequence))
        
        print(f"\n{'='*70}")
        print(f"🌐 SIMULATING {scenario_name.upper().replace('_', ' ')} SCENARIO")
        print(f"{'='*70}")
        print(f"📊 Total requests: {len(page_sequence)}")
        print(f"📄 Unique pages: {unique_pages}")
        print(f"🔄 Access pattern preview: {' -> '.join(page_sequence[:10])}{'...' if len(page_sequence) > 10 else ''}")
        print()
        print(f"{'Cache Size':<12} {'Hit Rate':<10} {'Miss Rate':<11} {'Evictions':<11} {'Efficiency':<11}")
        print("-" * 70)

        for size in cache_sizes:
            cache = LRUCache(size)
            
            # Process all page requests
            for page in page_sequence:
                cache.visit(page)
            
            stats = cache.get_statistics()
            results[size] = stats
            
            # Calculate efficiency (hit rate per unit of cache size)
            efficiency = stats['hit_rate'] / size if size > 0 else 0
            
            # Display results in tabular format
            print(f"{size:<12} {stats['hit_rate']:<9.1%} {stats['miss_rate']:<10.1%} {stats['evictions']:<11} {efficiency:<11.3f}")
        
        # Add summary insights
        print("\n💡 INSIGHTS:")
        best_hit_rate = max(results.values(), key=lambda x: x['hit_rate'])
        best_efficiency = max(results.values(), key=lambda x: x['hit_rate'] / x['capacity'])
        
        best_hit_size = [size for size, stats in results.items() if stats == best_hit_rate][0]
        best_eff_size = [size for size, stats in results.items() if stats == best_efficiency][0]
        
        print(f"   • Best hit rate: {best_hit_rate['hit_rate']:.1%} (cache size: {best_hit_size})")
        print(f"   • Most efficient: {best_efficiency['hit_rate']:.1%} (cache size: {best_eff_size})")
        
        if unique_pages <= min(cache_sizes):
            print(f"   ⚠️  Cache size {min(cache_sizes)} can hold all {unique_pages} unique pages")
        
        self.results[scenario_name] = results
        return results
    
    def compare_scenarios(self, cache_size: int = 10):
        """
        Compare different access patterns for a given cache size.
        
        Args:
            cache_size (int): Cache size for comparison
        """
        # Generate different access patterns
        random.seed(42)  # For reproducible results
        np.random.seed(42)
        
        scenarios = {
            'Random Access': [f"page_{random.randint(1, 20)}" for _ in range(100)],
            'Sequential Access': self.generate_sequential_pattern(100, 15),
            'Cyclic Access': [f"page_{i % 8}" for i in range(100)],  # Small cycle
            'Realistic (High Locality)': self.generate_realistic_page_sequence(100, 20, 0.8),
            'Zipf Distribution': self.generate_zipf_distribution(100, 20, 1.5)
        }
        
        print(f"\n{'='*70}")
        print(f"SCENARIO COMPARISON (Cache Size: {cache_size})")
        print(f"{'='*70}")
        print(f"{'Scenario':<25} {'Hit Rate':<10} {'Unique Pages':<12} {'Evictions':<10} {'Efficiency':<10}")
        print("-" * 70)
        
        comparison_results = {}
        
        for scenario_name, sequence in scenarios.items():
            cache = LRUCache(cache_size)
            
            for page in sequence:
                cache.visit(page)
            
            stats = cache.get_statistics()
            comparison_results[scenario_name] = stats
            
            efficiency = stats['hit_rate'] / cache_size if cache_size > 0 else 0
            
            print(f"{scenario_name:<25} {stats['hit_rate']:<9.1%} {len(set(sequence)):<12} {stats['evictions']:<10} {efficiency:<10.3f}")
        
        return comparison_results
    
    @staticmethod
    def generate_sequential_pattern(num_requests: int, num_unique_pages: int) -> List[str]:
        """
        Generate a sequential access pattern with some randomness.
        
        Args:
            num_requests (int): Total number of requests
            num_unique_pages (int): Number of unique pages
            
        Returns:
            List[str]: Sequential page access pattern
        """
        sequence = []
        current_page = 1
        
        for i in range(num_requests):
            # 80% chance to access next page in sequence, 20% chance to jump
            if random.random() < 0.8:
                # Sequential access
                sequence.append(f"page_{current_page}")
                current_page = (current_page % num_unique_pages) + 1
            else:
                # Random jump to break perfect sequence
                jump_page = random.randint(1, num_unique_pages)
                sequence.append(f"page_{jump_page}")
                current_page = jump_page
        
        return sequence
    
    def plot_results(self, save_plot: bool = False):
        """
        Create visualizations of cache performance.
        
        Args:
            save_plot (bool): Whether to save plots to files
        """
        if not self.results:
            print("No results to plot. Run simulations first.")
            return
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Browser Cache Performance Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Hit Rate vs Cache Size
        for scenario, results in self.results.items():
            sizes = list(results.keys())
            hit_rates = [results[size]['hit_rate'] * 100 for size in sizes]
            ax1.plot(sizes, hit_rates, marker='o', linewidth=2, label=scenario)
        
        ax1.set_xlabel('Cache Size')
        ax1.set_ylabel('Hit Rate (%)')
        ax1.set_title('Hit Rate vs Cache Size')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Miss Rate vs Cache Size
        for scenario, results in self.results.items():
            sizes = list(results.keys())
            miss_rates = [results[size]['miss_rate'] * 100 for size in sizes]
            ax2.plot(sizes, miss_rates, marker='s', linewidth=2, label=scenario)
        
        ax2.set_xlabel('Cache Size')
        ax2.set_ylabel('Miss Rate (%)')
        ax2.set_title('Miss Rate vs Cache Size')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Evictions vs Cache Size
        for scenario, results in self.results.items():
            sizes = list(results.keys())
            evictions = [results[size]['evictions'] for size in sizes]
            ax3.plot(sizes, evictions, marker='^', linewidth=2, label=scenario)
        
        ax3.set_xlabel('Cache Size')
        ax3.set_ylabel('Number of Evictions')
        ax3.set_title('Evictions vs Cache Size')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Cache Efficiency (Hit Rate / Cache Size)
        for scenario, results in self.results.items():
            sizes = list(results.keys())
            efficiency = [results[size]['hit_rate'] / size for size in sizes]
            ax4.plot(sizes, efficiency, marker='d', linewidth=2, label=scenario)
        
        ax4.set_xlabel('Cache Size')
        ax4.set_ylabel('Efficiency (Hit Rate / Cache Size)')
        ax4.set_title('Cache Efficiency')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig('cache_performance_analysis.png', dpi=300, bbox_inches='tight')
            print("Plot saved as 'cache_performance_analysis.png'")
        
        plt.show()
    
    def export_results(self, filename: str = "cache_results.json"):
        """
        Export simulation results to JSON file.
        
        Args:
            filename (str): Output filename
        """
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj
        
        serializable_results = convert_numpy_types(self.results)
        
        try:
            with open(filename, 'w') as f:
                json.dump(serializable_results, f, indent=2, default=str)
            print(f"✅ Results successfully exported to {filename}")
        except Exception as e:
            print(f"❌ Error exporting results: {e}")
            # Fallback: save as readable text
            with open(filename.replace('.json', '.txt'), 'w') as f:
                for scenario, results in self.results.items():
                    f.write(f"\nScenario: {scenario}\n")
                    f.write("=" * 40 + "\n")
                    for cache_size, stats in results.items():
                        f.write(f"Cache Size {cache_size}:\n")
                        f.write(f"  Hit Rate: {stats['hit_rate']:.2%}\n")
                        f.write(f"  Miss Rate: {stats['miss_rate']:.2%}\n")
                        f.write(f"  Evictions: {stats['evictions']}\n")
                        f.write(f"  Total Requests: {stats['total_requests']}\n\n")
            print(f"📝 Fallback: Results saved as text file")


def main():
    """
    Main function to run comprehensive browser cache simulation.
    """
    print("🌐 Browser Cache Simulator with LRU Policy")
    print("=" * 50)
    
    simulator = BrowserCacheSimulator()
    
    # Set random seeds for reproducible results
    random.seed(42)
    np.random.seed(42)
    
    # Test different scenarios
    cache_sizes = [2, 5, 10, 15, 20, 30]
    
    # Scenario 1: Random access pattern
    print("\n🎲 Generating random access pattern...")
    random_sequence = [f"page_{random.randint(1, 25)}" for _ in range(200)]
    simulator.simulate_cache_sizes(random_sequence, cache_sizes, "random_access")
    
    # Scenario 2: Sequential access pattern  
    print("\n📝 Generating sequential access pattern...")
    sequential_sequence = simulator.generate_sequential_pattern(200, 25)
    simulator.simulate_cache_sizes(sequential_sequence, cache_sizes, "sequential_access")
    
    # Scenario 3: Realistic access with temporal locality
    print("\n🌍 Generating realistic access pattern...")
    realistic_sequence = simulator.generate_realistic_page_sequence(200, 25, 0.75)
    simulator.simulate_cache_sizes(realistic_sequence, cache_sizes, "realistic_access")
    
    # Scenario 4: Zipf distribution (popular pages accessed more frequently)
    print("\n📈 Generating Zipf distribution pattern...")
    zipf_sequence = simulator.generate_zipf_distribution(200, 25, 1.2)
    simulator.simulate_cache_sizes(zipf_sequence, cache_sizes, "zipf_distribution")
    
    # Compare different access patterns
    print("\n🔍 Comparing access patterns...")
    simulator.compare_scenarios(cache_size=10)
    
    # Generate visualizations
    print("\n📊 Generating visualizations...")
    try:
        simulator.plot_results(save_plot=True)
        print("✅ Plots generated successfully!")
    except ImportError:
        print("⚠️  Matplotlib not available. Install with: pip install matplotlib")
        print("📊 Simulation data is still available in JSON export.")
    except Exception as e:
        print(f"⚠️  Plot generation failed: {e}")
    
    # Export results
    print("\n💾 Exporting results...")
    simulator.export_results()
    
    # Print summary
    print("\n" + "=" * 70)
    print("✅ SIMULATION COMPLETED SUCCESSFULLY!")
    print("📁 Generated files:")
    print("   • cache_performance_analysis.png (if matplotlib available)")
    print("   • cache_results.json (detailed results)")
    print("📊 Check the generated files for detailed analysis.")
    print("=" * 70)


def test_basic_functionality():
    """
    Test basic functionality to ensure everything works correctly.
    """
    print("🧪 Running basic functionality tests...")
    
    # Test 1: Basic LRU Cache
    print("\n1️⃣ Testing LRU Cache basic operations...")
    cache = LRUCache(3)
    
    # Test sequence that should show clear LRU behavior
    test_pages = ["A", "B", "C", "A", "D", "B"]
    expected_results = [False, False, False, True, False, False]  # Hit/Miss pattern
    
    results = []
    for page in test_pages:
        hit = cache.visit(page)
        results.append(hit)
        print(f"   Visit {page}: {'HIT' if hit else 'MISS'} | Cache: {list(cache.cache.keys())}")
    
    stats = cache.get_statistics()
    print(f"   Final stats: {stats['hit_rate']:.1%} hit rate, {stats['evictions']} evictions")
    
    # Test 2: Sequential pattern
    print("\n2️⃣ Testing sequential access pattern...")
    simulator = BrowserCacheSimulator()
    seq_pattern = simulator.generate_sequential_pattern(20, 5)
    print(f"   Sequential pattern preview: {seq_pattern[:10]}...")
    
    # Test 3: JSON export
    print("\n3️⃣ Testing JSON export...")
    test_results = {
        'test_scenario': {
            5: {'hit_rate': 0.65, 'miss_rate': 0.35, 'evictions': 10, 'total_requests': 50},
            10: {'hit_rate': 0.78, 'miss_rate': 0.22, 'evictions': 5, 'total_requests': 50}
        }
    }
    simulator.results = test_results
    simulator.export_results("test_results.json")
    
    print("✅ Basic tests completed!")


if __name__ == "__main__":
    # Run tests first
    test_basic_functionality()
    
    # Ask user if they want to run full simulation
    print("\n" + "="*50)
    response = input("🚀 Run full simulation? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        main()
    else:
        print("👋 Exiting. Run again with 'y' to see full simulation results!")
