import logging
import sys
import os

# Configure logging to show everything
logging.basicConfig(level=logging.DEBUG)

print(" Importing engine...")
try:
    from engine import calculate_best_targets
    print(" Import successful.")
except Exception as e:
    print(f" Import failed: {e}")
    sys.exit(1)

print(" Starting test calculation...")
try:
    results = calculate_best_targets(
        longitude="115.01",
        latitude="31.17",
        date_str=None, # Use today
        ignore_moonlight=True
    )
    
    print("\n Calculation finished.")
    print(f" Targets found: {len(results.get('targets', []))}")
    print(f" Bodies found: {len(results.get('bodies', []))}")
    print(f" Comets found: {len(results.get('comets', []))}")
    
    if results.get('targets'):
        print(f" First Target: {results['targets'][0]}")

except Exception as e:
    print(f" CRITICAL ERROR during calculation: {e}")
    import traceback
    traceback.print_exc()
