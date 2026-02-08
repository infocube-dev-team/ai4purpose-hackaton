import geopandas as gpd
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import os

def map_naples_risk():
    # Paths (Hardcoded base on exploration)
    base_dir = "data_raw"
    
    # Satellite Image (Visual RGB)
    # Using the one found in exploration: 2025-05-24 Visual
    sat_image_path = os.path.join(base_dir, "data_naples_raw_satellites_sample (2)/data_naples_raw_satellites_sample/sentinel-s2/20250524T100919-Naples-sentinels2/20250524T100919_Naples_sentinels2__visual.tif")
    
    # Risk Data (Buildings Flood Risk)
    risk_data_path = os.path.join(base_dir, "data_naples_raw_analysis_sample/data_naples_raw_analysis_sample/flooding-risk-l40/010000/Naples-floodingriskl40/Naples_floodingriskl40_buildings_risk.geojson")
    
    # Save to project root explicitly
    output_image = os.path.join(os.getcwd(), "naples_flood_risk_map.png")
    
    print(f"Loading Satellite Image: {sat_image_path}")
    if not os.path.exists(sat_image_path):
        print("Satellite image not found! Check paths.")
        return

    print(f"Loading Risk Data: {risk_data_path}")
    if not os.path.exists(risk_data_path):
        print("Risk data not found! Check paths.")
        return

    # Load Data
    try:
        gdf = gpd.read_file(risk_data_path)
        print(f"Loaded {len(gdf)} building features.")
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        return
        
    # Open Satellite Image
    try:
        src = rasterio.open(sat_image_path)
        print(f"Satellite CRS: {src.crs}")
        print(f"Vector CRS: {gdf.crs}")
        
        # Reproject Vector to match Raster if needed
        if gdf.crs != src.crs:
            print("Reprojecting vector data to match satellite CRS...")
            gdf = gdf.to_crs(src.crs)
            
    except Exception as e:
        print(f"Error loading Raster: {e}")
        return

    # Plotting
    print("Generating Map...")
    fig, ax = plt.subplots(figsize=(15, 15))
    
    # 1. Plot Satellite Image
    show(src, ax=ax, title="Naples Flood Risk (2050 - SSP5-8.5)")
    
    # 2. Plot Risk Overlay
    # Filter for significant risk if needed, or just plot all
    # Let's plot based on '2050-SSP5_8_5-RISK-INDEX'
    column_to_plot = '2050-SSP5_8_5-RISK-INDEX'
    
    if column_to_plot in gdf.columns:
        gdf.plot(column=column_to_plot, 
                 ax=ax, 
                 cmap='RdYlGn_r', # Red for high risk, Green for low
                 alpha=0.6, 
                 legend=True,
                 legend_kwds={'label': "Risk Index (0-10)"})
    else:
        print(f"Column {column_to_plot} not found. Plotting geometry only.")
        gdf.plot(ax=ax, color='red', alpha=0.5)

    # Save
    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    print(f"Map saved to {output_image}")
    plt.close()

if __name__ == "__main__":
    map_naples_risk()
