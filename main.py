from src.data.fetcher import WeatherFetcher
from src.analysis.risk_engine import RiskAnalyzer
import xarray as xr
import matplotlib.pyplot as plt

def main():
    print("--- Weather Risk Prediction System ---")
    
    # 1. Fetch Data
    fetcher = WeatherFetcher(source="ecmwf-open-data")
    print("Fetching data...")
    # Getting a few steps to test
    try:
        ds_earthkit = fetcher.fetch_forecast(steps=[3, 6, 9, 12])
        ds = ds_earthkit.to_xarray()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    print("Data fetched successfully.")
    print(ds)

    # 2. Analyze Risks
    analyzer = RiskAnalyzer(thresholds={"wind_speed": 10.0, "precipitation": 1.0}) # Lower thresholds for testing
    print("Analyzing risks...")
    
    # Note: Dataset keys might differ slightly depending on the exact source version.
    # We should inspect `ds` in a real run. 
    # Earthkit generic GRIB often gives parameter names like '2t', '10u', '10v', 'tp'.
    
    try:
        overall_risk, risk_details = analyzer.analyze(ds)
    except KeyError as e:
        print(f"Key Error during analysis. Available variables: {list(ds.keys())}")
        print(f"Missing: {e}")
        return

    # 3. Report
    print("\n--- Risk Report ---")
    
    # Check if we found ANY risk anywhere
    total_risky_points = overall_risk.sum().values
    print(f"Total risky grid points detected (across all steps/members): {total_risky_points}")
    
    for r_type, r_mask in risk_details.items():
        count = r_mask.sum().values
        print(f"  - {r_type}: {count} points")

    if total_risky_points > 0:
        print("\nSaving visualizations...")
        from src.viz.plotter import RiskPlotter
        plotter = RiskPlotter()
        
        # Plot overall risk
        plotter.plot_risk_map(overall_risk, title="Combined Risk Map (Step 0)", filename="combined_risk_step0.png")
        
        # Plot individual risks (e.g., wind) if they exist
        if 'wind_risk' in risk_details and risk_details['wind_risk'].sum() > 0:
            plotter.plot_risk_map(risk_details['wind_risk'], title="Wind Risk (>15 m/s)", filename="wind_risk_step0.png")
            
        print("Visualizations saved.")
        
        # Save text report
        with open("risk_report.txt", "w") as f:
            f.write("Weather Risk Report\n")
            f.write("===================\n")
            f.write(f"Total Risky Points: {total_risky_points}\n")
            for r_type, r_mask in risk_details.items():
                f.write(f"{r_type}: {r_mask.sum().values}\n")
        print("Saved 'risk_report.txt'")

if __name__ == "__main__":
    main()
