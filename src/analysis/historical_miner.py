import pandas as pd
import xarray as xr
from src.data.fetcher import WeatherFetcher
from src.analysis.risk_engine import RiskAnalyzer
import os

def mine_history(start_date, end_date, output_file="events_database.parquet"):
    print(f"--- Starting Event Mining: {start_date} to {end_date} ---")
    
    # Initialize Fetcher and Analyzer
    fetcher = WeatherFetcher(source="cds")
    # ERA5 variables are often named differently in GRIB from CDS vs Open Data
    # We might need to handle mapping in RiskAnalyzer or rename here.
    # RiskAnalyzer expects: '10u', '10v', 'tp', '2t' (shortNames)
    # ERA5 GRIB often has these shortNames too.
    
    analyzer = RiskAnalyzer()
    
    try:
        # Fetch Data
        # fetch_era5_history defined in updated fetcher (need to verify update applied)
        ds_earthkit = fetcher.fetch_era5_history(start_date, end_date)
        ds = ds_earthkit.to_xarray()
        
        print(f"Variables found: {list(ds.keys())}")
        
        # Rename ERA5 variables to match RiskAnalyzer which currently expects ECMWF Open Data conventions
        # Analyzer expects: '2t', '10u', '10v', 'tp'
        # ERA5 might provide: 't2m', 'u10', 'v10', 'tp'
        
        name_map = {
            't2m': '2t',
            'u10': '10u',
            'v10': '10v',
            'var167': '2t', # GRIB paramId
            'var165': '10u',
            'var166': '10v',
            'var228': 'tp'
        }
        
        # Create a renaming dict only for keys that exist
        rename_dict = {k: v for k, v in name_map.items() if k in ds.keys()}
        
        if rename_dict:
            print(f"Renaming variables: {rename_dict}")
            ds = ds.rename(rename_dict)
        
        print(f"Variables after processing: {list(ds.keys())}")

    except Exception as e:
        print(f"Error fetching/processing data: {e}")
        return

    print("Analyzing for risks...")
    risk_mask, details = analyzer.analyze(ds)
    
    # We want to extract "Events".
    # An event could be defined as a connected component of risky pixels, 
    # or simply a list of lat/lon/time points where risk is high.
    # For a database, a list of points or a summary per timestep/region is good.
    
    # Let's create a DataFrame of all risky points
    # This can be huge, so we might want to aggregate or filter heavily.
    
    events_list = []
    
    # Iterate over risk types
    for risk_type, mask in details.items():
        # Mask is a DataArray boolean
        # We can stack it to finding True indices
        risky_points = mask.where(mask, drop=True)
        
        if risky_points.count() == 0:
            continue
            
        print(f"Found {risky_points.count().values} points for {risk_type}")
        
        # Convert to dataframe
        # This gives a DF with MultiIndex (time, lat, lon)
        df = risky_points.to_dataframe(name="is_risky").reset_index()
        df = df[df["is_risky"] == True].drop(columns=["is_risky"])
        df["event_type"] = risk_type
        
        # Add values if possible (e.g. actual wind speed) - distinct step, keeping it simple
        events_list.append(df)

    if not events_list:
        print("No events found.")
        return

    all_events = pd.concat(events_list, ignore_index=True)
    
    # Save
    if output_file.endswith(".parquet"):
        all_events.to_parquet(output_file)
    else:
        all_events.to_csv(output_file, index=False)
        
    print(f"Saved {len(all_events)} event records to {output_file}")
    print(all_events.head())

if __name__ == "__main__":
    # Example usage: 2 days in the past (to avoid too much data for demo)
    mine_history("2023-01-01", "2023-01-02")
