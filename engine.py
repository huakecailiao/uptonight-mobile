import os
import logging
import pandas as pd
from datetime import datetime, timedelta
import pytz
from astropy.time import Time
from astropy.coordinates import AltAz, SkyCoord
from uptonight import uptonight
from uptonight.const import (
    DEFAULT_ALTITUDE_CONSTRAINT_MIN,
    DEFAULT_ALTITUDE_CONSTRAINT_MAX,
    DEFAULT_AIRMASS_CONSTRAINT,
    DEFAULT_SIZE_CONSTRAINT_MIN,
    DEFAULT_SIZE_CONSTRAINT_MAX,
    DEFAULT_MOON_SEPARATION_MIN,
    DEFAULT_FRACTION_OF_TIME_OBSERVABLE_THRESHOLD,
    DEFAULT_MAX_NUMBER_WITHIN_THRESHOLD
)

# Set base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Targets folder copied to valid path
TARGETS_DIR = os.path.join(BASE_DIR, "targets")
DEFAULT_TARGET_LIST_PATH = os.path.join(TARGETS_DIR, "GaryImm")

# Ensure Assets paths for Skyfield/Astropy are finding their files
# Data dir
DATA_DIR = os.path.join(BASE_DIR, "assets", "data")

def calculate_best_targets(
    longitude,
    latitude,
    elevation=0,
    timezone="Asia/Shanghai", # Default to Shanghai for this user
    min_altitude=30,
    ignore_moonlight=True,
    date_str=None,
    calc_objects=True,
    calc_bodies=True,
    calc_comets=True
):
    """
    Calculate best targets for the given location and constraints.
    longitude: str (e.g. "11d34m51.50s" or "11.58")
    latitude: str (e.g. "48d08m10.77s" or "48.13")
    """
    
    # 1. Setup Location
    location = {
        "longitude": longitude,
        "latitude": latitude,
        "elevation": elevation,
        "timezone": timezone
    }
    
    # 2. Setup Constraints
    moon_sep_min = int(DEFAULT_MOON_SEPARATION_MIN)
    moon_sep_illumRequest = True
    
    if ignore_moonlight:
        moon_sep_min = 0
        moon_sep_illumRequest = False

    constraints = {
        "altitude_constraint_min": int(min_altitude),
        "altitude_constraint_max": int(DEFAULT_ALTITUDE_CONSTRAINT_MAX),
        "airmass_constraint": DEFAULT_AIRMASS_CONSTRAINT,
        "size_constraint_min": int(DEFAULT_SIZE_CONSTRAINT_MIN),
        "size_constraint_max": int(DEFAULT_SIZE_CONSTRAINT_MAX),
        "moon_separation_min": moon_sep_min,
        "moon_separation_use_illumination": moon_sep_illumRequest,
        "fraction_of_time_observable_threshold": 0.5, # Relaxed default
        "max_number_within_threshold": DEFAULT_MAX_NUMBER_WITHIN_THRESHOLD,
        "north_to_east_ccw": False,
    }

    # features = {"horizon": False, "objects": True, "bodies": True, "comets": True, "alttime": False}
    features = {
        "horizon": False, 
        "objects": calc_objects, 
        "bodies": calc_bodies, 
        "comets": calc_comets, 
        "alttime": False
    }
    
    # Dummy Environment
    environment = {"pressure": 0, "relative_humidity": 0, "temperature": 0}
    colors = {
        "ticks": "#F2F2F2",
        "text": "#FFFFFF",
        "axes": "#262626",
        "legend": "#262626",
        "figure": "#1C1C1C",
        "grid": "#404040",
        "alttime": "#00CCFF",
        "meridian": "#FF0000"
    }
    
    # 3. Initialize UpTonight
    # Creating a temporary output dir
    tmp_dir = os.path.join(BASE_DIR, "tmp_out")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    app = uptonight.UpTonight(
        location=location,
        features=features,
        colors=colors,
        constraints=constraints,
        environment=environment,
        target_list=DEFAULT_TARGET_LIST_PATH,
        observation_date=date_str, # Format MM/DD/YY usually expected by UpTonight
        output_dir=tmp_dir,
    )
    print(f"DEBUG: UpTonight initialized. Observer: {app._observer.location}")

    # 4. Perform Calculation
    try:
        print("DEBUG: Starting app.calc()...")
        result_tables = app.calc()
        print("DEBUG: app.calc() finished.")
    except Exception as e:
        print(f"ERROR in uptonight.calc: {e}")
        import traceback
        traceback.print_exc()
        return {}

    response = {
        "targets": [],
        "bodies": [],
        "comets": []
    }

    # 5. Process Results
    if result_tables.get("targets") is not None and len(result_tables["targets"]) > 0:
        df = result_tables["targets"].to_pandas()
        df = df.fillna("")
        response["targets"] = df.to_dict(orient="records")
            
    if result_tables.get("bodies") is not None and len(result_tables["bodies"]) > 0:
        df = result_tables["bodies"].to_pandas()
        df = df.fillna("")
        response["bodies"] = df.to_dict(orient="records")
            
    if result_tables.get("comets") is not None and len(result_tables["comets"]) > 0:
        df = result_tables["comets"].to_pandas()
        df = df.fillna("")
        response["comets"] = df.to_dict(orient="records")

    # 6. Calculate Altitude Curves
    # Calculate for 18:00 to 06:00
    try:
        tz = pytz.timezone(timezone)
        if date_str:
            # Helper to parse uptonight date format if strict
            try:
                ref_date = datetime.strptime(date_str, "%m/%d/%y").date()
            except:
                ref_date = datetime.now(tz).date()
        else:
            ref_date = datetime.now(tz).date()

        start_dt_naive = datetime.combine(ref_date, datetime.min.time().replace(hour=18))
        end_dt_naive = start_dt_naive + timedelta(hours=12)
        start_dt = tz.localize(start_dt_naive)
        end_dt = tz.localize(end_dt_naive)
        
        time_points = []
        current_dt = start_dt
        while current_dt <= end_dt:
            time_points.append(current_dt)
            current_dt += timedelta(minutes=30)
        
        # Astropy Observer
        astro_times = Time(time_points)
        altaz_frame = AltAz(obstime=astro_times, location=app._observer.location)

        # NEW: Calculate Moon Curve
        print("DEBUG: Calculating Moon Curve...")
        try:
            # Import get_body locally to avoid circular import or top-level issues if any
            from astropy.coordinates import get_body 
            moon_coord = get_body("moon", astro_times)
            moon_altaz = moon_coord.transform_to(altaz_frame)
            moon_alts = moon_altaz.alt.deg
            response["moon_curve"] = [round(a, 1) for a in moon_alts]
            print(f"DEBUG: Moon curve calculated: {response['moon_curve'][:5]}...")
        except Exception as e:
            print(f"Error calculating moon curve: {e}")
            import traceback
            traceback.print_exc()
            response["moon_curve"] = []

        def calculate_curve(target_list):
            for target in target_list:
                if 'hmsdms' in target and target['hmsdms']:
                    coord = SkyCoord(target['hmsdms'], frame='icrs')
                    altaz = coord.transform_to(altaz_frame)
                    alts = altaz.alt.deg
                    target['altitude_curve'] = [round(a, 1) for a in alts]
                    
                    # Duration
                    count_above = sum(1 for a in alts if a >= min_altitude)
                    target['imaging_duration'] = f"{count_above * 0.5}h"

        if response["targets"]: calculate_curve(response["targets"])
        if response["bodies"]: calculate_curve(response["bodies"]) # Approx
        if response["comets"]: calculate_curve(response["comets"]) # Approx

    except Exception as e:
        print(f"Error calculating curves: {e}")

    return response
