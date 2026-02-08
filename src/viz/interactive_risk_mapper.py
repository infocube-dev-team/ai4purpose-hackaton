import pandas as pd
import geopandas as gpd
import folium
import joblib
import os
from shapely.geometry import Point

def generate_interactive_map():
    # Paths
    model_path = "src/ml/weather_risk_model.pkl" # Check if path is correct relative to execution
    dataset_path = "training_dataset.parquet"
    output_html = "interactive_risk_map.html"
    
    # 1. Load Model and Data
    print("Loading Model and Data...")
    if not os.path.exists(model_path):
        # Try adjusting path if run from root
        model_path = "weather_risk_model.pkl" 
        if not os.path.exists(model_path):
             print(f"Model not found at {model_path}")
             return

    try:
        clf = joblib.load(model_path)
        df = pd.read_parquet(dataset_path)
    except Exception as e:
        print(f"Error loading: {e}")
        return

    # 2. Prepare Features for Prediction
    # We need the same features used during training
    feature_cols = ['10u', '10v', '2t', 'latitude', 'longitude']
    
    # Check for missing columns
    if not all(col in df.columns for col in feature_cols):
        print(f"Dataset missing one of {feature_cols}")
        return

    # 3. Predict
    print("Running Predictions...")
    X = df[feature_cols]
    y_pred = clf.predict(X)
    
    # Add prediction to dataframe
    df['predicted_risk'] = y_pred
    
    # 4. Filter for Risky Points only (to avoid creating a map with millions of points)
    risky_df = df[df['predicted_risk'] == True].copy()
    print(f"Found {len(risky_df)} risky points (out of {len(df)} total).")
    
    if len(risky_df) > 5000:
        print("Too many points for interactive map. Sampling 5000...")
        risky_df = risky_df.sample(5000)
    
    # 5. Create GeoDataFrame
    geometry = [Point(xy) for xy in zip(risky_df['longitude'], risky_df['latitude'])]
    gdf = gpd.GeoDataFrame(risky_df, geometry=geometry, crs="EPSG:4326")
    
    # 6. Create Interactive Map
    print("Generating Folium Map...")
    # Center map on average location of risks
    center_lat = risky_df['latitude'].mean()
    center_lon = risky_df['longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=4)
    
    # Use explore() if available (easiest) or manual folium markers
    # We can visualize '2t' (Temperature) or Wind Speed as color
    gdf.explore(
        column='2t', # Color by temperature or wind
        cmap='coolwarm',
        legend=True,
        marker_type='circle_marker',
        marker_kwds={'radius': 5},
        m=m, # Add to existing map object
        name="Predicted Risks"
    )
    
    # Save
    m.save(output_html)
    print(f"Map saved to {output_html}")

if __name__ == "__main__":
    generate_interactive_map()
