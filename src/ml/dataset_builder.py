import pandas as pd
import xarray as xr
import numpy as np
from src.data.fetcher import WeatherFetcher
from src.analysis.risk_engine import RiskAnalyzer

def build_dataset(start_date, end_date, output_file="training_dataset.parquet", sample_fraction=0.01):
    """
    Fetches data, calculates risk labels, and creates a tabular dataset for ML.
    
    Args:
        sample_fraction: Fraction of 'non-risky' points to keep. 
                         Risky points are usually kept 100% to balance the dataset.
    """
    print(f"--- Building ML Dataset: {start_date} to {end_date} ---")
    
    fetcher = WeatherFetcher(source="cds")
    analyzer = RiskAnalyzer()
    
    try:
        ds_earthkit = fetcher.fetch_era5_history(start_date, end_date)
        ds = ds_earthkit.to_xarray()
        
        # Rename logic (copied from miner for consistency)
        name_map = {'t2m': '2t', 'u10': '10u', 'v10': '10v', 'var167': '2t', 'var165': '10u', 'var166': '10v'}
        rename_dict = {k: v for k, v in name_map.items() if k in ds.keys()}
        if rename_dict:
            ds = ds.rename(rename_dict)
            
    except Exception as e:
        print(f"Data fetch failed: {e}")
        return

    print("Generating Truth Labels (Risk Analysis)...")
    # risk_mask is boolean xarray (True if ANY risk)
    # details is dict of boolean xarrays for specific risks
    overall_risk_mask, details = analyzer.analyze(ds)
    
    # We want a dataframe with:
    # lat, lon, time, feature_1 (u), feature_2 (v), feature_3 (t), ..., TARGET (is_risky)
    
    print("Converting to Tabular Format...")
    
    # Convert entire dataset to dataframe (can be memory intensive!)
    # For prototype, we do it in memory. For scale, use Dask or process by chunks.
    df = ds.to_dataframe().reset_index()
    
    # Clean up columns (remove unnecessary coordinates if any)
    # We need to ensure we have the features.
    # Features: 10u, 10v, 2t
    # We also need the calculated risk labels.
    
    # Let's add the target from the mask
    # The mask should align perfectly if dimensions match.
    # Using xarray alignment is safer.
    
    ds['target_risk'] = overall_risk_mask
    
    # Also add specific targets if we want multi-label
    for key, mask in details.items():
        ds[f'target_{key}'] = mask

    # Now convert
    print("Flattening to DataFrame...")
    df = ds.to_dataframe().dropna().reset_index()
    
    print(f"Total raw samples: {len(df)}")
    
    # Downsampling Negative Class (Imbalance handling)
    positive_samples = df[df['target_risk'] == True]
    negative_samples = df[df['target_risk'] == False]
    
    print(f"Positive samples: {len(positive_samples)}")
    print(f"Negative samples: {len(negative_samples)}")
    
    if len(negative_samples) > 0:
        negative_sampled = negative_samples.sample(frac=sample_fraction, random_state=42)
        print(f"Downsampled negatives to: {len(negative_sampled)}")
        final_df = pd.concat([positive_samples, negative_sampled])
    else:
        final_df = positive_samples
        
    # Shuffle
    final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Final Dataset Size: {len(final_df)}")
    
    # Save
    final_df.to_parquet(output_file)
    print(f"Saved to {output_file}")
    print(final_df.head())

if __name__ == "__main__":
    # Test run
    build_dataset("2023-01-01", "2023-01-01")
