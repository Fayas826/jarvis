import sys
import asyncio
from tests.benchmark_runner import BenchmarkRunner

async def main():
    runner = BenchmarkRunner()
    metrics = await runner.evaluate_all()
    print("==================================================")
    print("🏆 PHASE 19 BENCHMARK RESULTS")
    print("==================================================")
    print(f"Total Samples: {metrics['total_samples']}")
    print(f"Evaluated: {metrics['evaluated_samples']}")
    print(f"Success Count: {metrics['successful_samples']}")
    print(f"Failed Count: {metrics['failed_samples']}")
    print(f"Unsupported Count: {metrics['unsupported_samples']}")
    print(f"Accuracy: {metrics['accuracy']:.1f}%")
    print(f"Avg Latency: {metrics['average_latency_ms']:.1f}ms")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
