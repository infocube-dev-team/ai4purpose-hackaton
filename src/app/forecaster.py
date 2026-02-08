import sys
import os
import argparse
import pandas as pd
import xarray as xr
from geopy.geocoders import Nominatim

# Adjust path to import modules from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data.fetcher import WeatherFetcher
from src.analysis.risk_engine import RiskAnalyzer

def get_location_bounds(location_name, buffer_deg=1.0):
    """
    Geocodes a location name and returns a bounding box.
    Returns: [North, West, South, East] or None
    """
    geolocator = Nominatim(user_agent="ai4purpose_risk_forecaster")
    location = geolocator.geocode(location_name)
    
    if location:
        lat = location.latitude
        lon = location.longitude
        print(f"Location found: {location.address} ({lat}, {lon})")
        
        # Create a simple bounding box around the point
        # N, W, S, E
        return [lat + buffer_deg, lon - buffer_deg, lat - buffer_deg, lon + buffer_deg]
    else:
        print(f"Location '{location_name}' not found.")
        return None

def run_forecast(location_name, hours=48):
    print(f"--- Starting Forecast for {location_name} (Next {hours} hours) ---")
    
    # 1. Geocode
    bounds = get_location_bounds(location_name)
    if not bounds:
        return
    
    # 2. Fetch Data
    fetcher = WeatherFetcher()
    # We pass area in kwargs just in case fetcher uses it (e.g. for CDS), 
    # but for Open Data we'll manually crop.
    fetcher.kwargs = {'area': bounds} 
    
    steps = list(range(0, hours + 1, 3)) # 3-hour intervals
    ds_reader = fetcher.fetch_forecast(steps=steps)
    
    # Convert to xarray
    ds = ds_reader.to_xarray()
    
    # 2.1 Crop Data (since Open Data doesn't support area request)
    print(f"Cropping data to bounds: {bounds}")
    # bounds = [N, W, S, E]
    # Latitude in ECMWF is typically Descending (90 to -90)
    # Longitude is -180 to 180 or 0 to 360.
    # We use .sel(latitude=slice(N, S), longitude=slice(W, E))
    # Note: slice(start, stop) includes start and stop.
    # If standard is N->S, slice(MaxLat, MinLat) works.
    
    try:
        ds = ds.sel(latitude=slice(bounds[0], bounds[2]), longitude=slice(bounds[1], bounds[3]))
        print(f"Data cropped. New shape: {ds.dims}")
    except Exception as e:
        print(f"Cropping failed (possibly grid mismatch): {e}")
        # Fallback to nearest if needed or just proceed
    
    # 3. Analyze Risk
    analyzer = RiskAnalyzer()
    risk_mask, details = analyzer.analyze(ds)
    
    # 4. Process Results for Kepler (CSV)
    # We need to extract the "Risky Points" into a DataFrame with Lat/Lon
    # The risk_mask is boolean (Time, Lat, Lon) or similar dimensions
    
    # Identify where risk is True
    # We will aggregate all risks for simplicity or keep them separate
    
    print("Analyzing risks...")
    
    # Determine which variables we have
    if 'time' not in risk_mask.dims and 'step' in risk_mask.dims:
         # Standardize dimension names if needed, or iterate steps
         pass
         
    # risk_mask likely has dims (step, lat, lon) or similar
    # Let's convert to DataFrame to handle it easily
    # We select only True values to keep file size small
    
    # We can use the details dictionary to be specific
    # Consolidate risks:
    total_risk = risk_mask
    
    # stacking to create a table: (step, lat, lon) -> rows
    # This might be heavy if area is large, but for a city it is fine.
    
    df = total_risk.to_dataframe(name='risk_flag').reset_index()
    df = df[df['risk_flag'] == True] # Filter only risky points
    
    if df.empty:
        print("No significant risks detected for this period.")
        # Create empty file to avoid errors in reading
        pd.DataFrame(columns=['lat', 'lon', 'risk_score']).to_csv("targeted_risks.csv", index=False)
        return

    # Add risk types
    # Iterate through details to flag which risk it is. 
    # This is a bit slow but effective for prototypes.
    
    # Initialize columns
    for risk_name in details.keys():
        df[risk_name] = False
        
    # Map back specific risks
    # This is robust: for each risk mask, convert to DF, filter True, and merge or update
    # Optimization: Just sample or assume if 'risk_flag' is true, check which detail caused it.
    
    # Let's just create a 'risk_type' column string
    # Better approach:
    # Merge all detail DataArrays into a Dataset
    risk_ds = xr.Dataset()
    for name, da in details.items():
        risk_ds[name] = da
        
    risk_df = risk_ds.to_dataframe().reset_index()
    # Filter where at least one risk is True
    mask = risk_df[list(details.keys())].any(axis=1)
    final_df = risk_df[mask].copy()
    
    # Clean up structure for Kepler
    # Kepler needs: lat, lon, timestamp? 
    # 'step' is usually timedelta or hours. We can convert to estimated datetime if we have valid_time.
    
    # Rename columns for clarity
    if 'latitude' in final_df.columns:
        final_df = final_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
    
    # Construct a readable 'risk_type' column
    def summarize_risk(row):
        active_risks = [col for col in details.keys() if row[col]]
        return ", ".join(active_risks)
        
    final_df['risk_type'] = final_df.apply(summarize_risk, axis=1)
    
    # Add a magnitude/score (fake for now, usually based on intensity)
    final_df['risk_score'] = 1.0 
    
    # Keep only relevant columns
    cols_to_keep = ['lat', 'lon', 'risk_type', 'risk_score']
    if 'valid_time' in final_df.columns:
        cols_to_keep.append('valid_time')
    elif 'time' in final_df.columns:
        cols_to_keep.append('time') # Use time if present
    elif 'step' in final_df.columns:
        # If valid_time is not there, we might just have steps relative to now.
        # Let's add a fake timestamp column for Kepler animation if needed
        # row['step'] is timedelta usually
        cols_to_keep.append('step')

    output_df = final_df[cols_to_keep]
    
    output_path = "targeted_risks.csv"
    output_df.to_csv(output_path, index=False)
    print(f"Targeted risk forecast saved to {output_path}")
    print(f"Total risky points identified: {len(output_df)}")
    print(output_df.head())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Targeted Risk Forecaster")
    parser.add_argument("location", type=str, help="City or Location Name")
    parser.add_argument("--hours", type=int, default=48, help="Hours forward to forecast")
    args = parser.parse_args()
    
    run_forecast(args.location, args.hours)
