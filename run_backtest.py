#!/usr/bin/env python3
import asyncio
import json
from backend.backtest import run_backtest

async def main():
    print("=" * 60)
    print("ParallelShop Credibility Back-Test (Hold-Out Validation)")
    print("=" * 60)
    print("Running simulation against historical stockout event...\n")
    
    result = await run_backtest(sample_size_per_persona=25)
    
    print(f"Target Event: {result['event_name']}")
    print(f"Removed Product: {result['removed_product']}")
    print(f"Sample Size Evaluated: {result['shoppers_evaluated']} shoppers\n")
    
    print(f"{'Behavior':<26} | {'Actual %':<10} | {'Predicted %':<12} | {'Abs Error %':<12}")
    print("-" * 68)
    for row in result["comparison"]:
        print(f"{row['behavior']:<26} | {row['actual_historical_pct']:<10.1f} | {row['predicted_agent_pct']:<12.1f} | {row['absolute_error_pct']:<12.1f}")
    print("-" * 68)
    
    print(f"\nMean Absolute Error: {result['mean_absolute_error_pct']}%")
    print("\n" + "*" * 68)
    print(f"KILLER SLIDE STAT:")
    print(f"  \"{result['killer_slide_stat']}\"")
    print("*" * 68 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
