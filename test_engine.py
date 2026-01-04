
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from engine import calculate_best_targets
from datetime import datetime

def test_engine():
    print("Starting engine test...")
    try:
        # Simulate inputs from main.py default values
        lat = "31.17"
        lon = "115.01"
        date_str = datetime.now().strftime("%m/%d/%y")
        ignore_moon = True # Test both cases if needed, start with True

        print(f"Testing with Lat:{lat}, Lon:{lon}, Date:{date_str}, IgnoreMoon:{ignore_moon}")

        results = calculate_best_targets(
            longitude=lon,
            latitude=lat,
            date_str=date_str,
            ignore_moonlight=ignore_moon
        )

        print("Calculation complete.")
        
        # Verify results structure
        if not isinstance(results, dict):
             print(f"FAILED: Result is not a dict, got {type(results)}")
             return

        keys = ['targets', 'bodies', 'comets']
        for k in keys:
            if k in results:
                print(f"[{k}] Check: OK (Count: {len(results[k])})")
                if len(results[k]) > 0:
                    print(f"  First item in {k}: {results[k][0].get('id') or results[k][0].get('target name')}")
            else:
                print(f"[{k}] Check: MISSING key")

        print("Test finished successfully.")

    except Exception as e:
        print(f"Test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_engine()
