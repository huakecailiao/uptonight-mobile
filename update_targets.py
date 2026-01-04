import os
import requests

# Base URL for the upstream repository's targets directory (master branch)
BASE_URL = "https://raw.githubusercontent.com/mawinkler/uptonight/master/targets/"

# Local targets directory
LOCAL_TARGETS_DIR = os.path.join(os.path.dirname(__file__), "targets")

# List of known target files to update
# Based on the contents of the uptonight/targets folder
TARGET_FILES = [
    "GaryImm.yaml",
    "Herschel400.yaml",
    "LBN.yaml",
    "LDN.yaml",
    "Messier.yaml",
    "OpenIC.yaml",
    "OpenNGC.yaml",
    "Pensack500.yaml"
]

def update_targets():
    """Downloads the latest target files from GitHub."""
    print(f"Updating targets from {BASE_URL}...")
    
    if not os.path.exists(LOCAL_TARGETS_DIR):
        print(f"Error: Local targets directory '{LOCAL_TARGETS_DIR}' does not exist.")
        return

    success_count = 0
    
    for filename in TARGET_FILES:
        url = BASE_URL + filename
        local_path = os.path.join(LOCAL_TARGETS_DIR, filename)
        
        print(f"Downloading {filename}...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raise an error for bad status codes
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            print(f"  -> Saved to {local_path}")
            success_count += 1
            
        except requests.exceptions.RequestException as e:
            print(f"  !! Failed to download {filename}: {e}")
        except Exception as e:
            print(f"  !! Error processing {filename}: {e}")

    print("-" * 30)
    print(f"Update complete. {success_count}/{len(TARGET_FILES)} files updated.")

from skyfield.api import Loader, load
from skyfield.data import mpc

def update_comets():
    """Forces an update of the comet data from MPC using Skyfield."""
    print("Updating comets from MPC...")
    try:
        # Define the loader path explicitly to match uptonight's default if possible, 
        # or rely on default ~/skyfield-data
        load_path = "~/skyfield-data"
        loader = Loader(load_path)
        
        # Reload the comet data
        # processing_comet_data logic from uptonight might be needed if we want to pre-process,
        # but for now we just want to ensure the file is downloaded.
        # uptonight/comets.py just does: with load.open(mpc.COMET_URL) as f:
        # We add reload=True to force download.
        print(f"Downloading comet data to {load_path}...")
        with loader.open(mpc.COMET_URL, reload=True) as f:
            comets = mpc.load_comets_dataframe(f)
        
        print(f"  -> Comet data updated. Loaded {len(comets)} comets.")
        return True
    except Exception as e:
        print(f"  !! Failed to update comets: {e}")
        return False

def update_all():
    """Updates both DSOs and Comets."""
    print("Starting full data update...")
    update_targets()
    update_comets()
    print("Full update process finished.")

if __name__ == "__main__":
    update_all()
