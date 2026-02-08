import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr

class RiskPlotter:
    """
    Handles visualization of weather risks.
    """

    def __init__(self, output_dir="."):
        self.output_dir = output_dir

    def plot_risk_map(self, risk_data: xr.DataArray, title="Risk Map", filename="risk_map.png"):
        """
        Plots a boolean or categorical risk map on a global map.
        """
        plt.figure(figsize=(15, 10))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        
        # Plot the risk data
        # check if it has 'step' dimension, if so, pick the first one or require specific slice
        if 'step' in risk_data.dims:
            print("Warning: Plotting first step of multi-step data.")
            data_to_plot = risk_data.isel(step=0)
        else:
            data_to_plot = risk_data

        # Plotting boolean mask
        # We mask False values to make them transparent
        masked_data = data_to_plot.where(data_to_plot > 0)
        
        masked_data.plot(
            ax=ax, 
            transform=ccrs.PlateCarree(),
            cmap='Reds', 
            add_colorbar=True,
            cbar_kwargs={'label': 'Risk Present'}
        )

        plt.title(title)
        out_path = f"{self.output_dir}/{filename}"
        plt.savefig(out_path)
        print(f"Saved plot to {out_path}")
        plt.close()

    def plot_weather_field(self, data: xr.DataArray, title="Weather Field", filename="weather.png", cmap='viridis'):
        """
        Plots a raw weather field (e.g., Temperature, Wind).
        """
        plt.figure(figsize=(15, 10))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE)
        
        if 'step' in data.dims:
             data = data.isel(step=0)

        data.plot(
            ax=ax, 
            transform=ccrs.PlateCarree(),
            cmap=cmap
        )
        
        plt.title(title)
        out_path = f"{self.output_dir}/{filename}"
        plt.savefig(out_path)
        plt.close()
