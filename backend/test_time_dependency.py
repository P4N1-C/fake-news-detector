#!/usr/bin/env python3
"""
Test script for time dependency feature
"""

import asyncio
import sys
from llm_utils import check_time_dependency

async def test_time_dependency():
    """Test time dependency detection with various claim types"""
    
    test_claims = [
        # Time-dependent claims
        "The stock market closed up 3% today",
        "It's currently raining in New York City",
        "The President announced new policies yesterday",
        "Bitcoin price reached $50,000 this morning",
        "The latest unemployment rate was released this week",
        
        # Non-time-dependent claims
        "The Earth is round",
        "Albert Einstein developed the theory of relativity", 
        "Water boils at 100 degrees Celsius at sea level",
        "The Great Wall of China was built over many centuries",
        "Shakespeare wrote Romeo and Juliet"
    ]
    
    print("Testing Time Dependency Detection")
    print("=" * 50)
    
    for i, claim in enumerate(test_claims, 1):
        print(f"\n{i}. Testing claim: '{claim}'")
        print("-" * 60)
        
        try:
            result = await check_time_dependency(claim)
            
            is_time_dependent = result.get("is_time_dependent", False)
            duration_days = result.get("dependency_duration_days", 0)
            
            print(f"Time Dependent: {is_time_dependent}")
            print(f"Duration (days): {duration_days}")
            
            # Validate results make sense
            if is_time_dependent and duration_days <= 0:
                print("⚠️  WARNING: Time-dependent claim has zero or negative duration!")
            elif not is_time_dependent and duration_days > 0:
                print("⚠️  WARNING: Non-time-dependent claim has positive duration!")
            else:
                print("✅ Result appears consistent")
                
        except Exception as e:
            print(f"❌ Error testing claim: {str(e)}")

if __name__ == "__main__":
    print("Time Dependency Feature Test")
    print("Make sure GOOGLE_API_KEY is set in your .env file")
    print()
    
    try:
        asyncio.run(test_time_dependency())
        print("\n" + "=" * 50)
        print("Test completed!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        sys.exit(1) 