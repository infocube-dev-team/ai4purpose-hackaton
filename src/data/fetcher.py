import earthkit.data
import xarray as xr

class WeatherFetcher:
    """
    A class to fetch weather data using earthkit-data.
    Defaults to ECMWF Open Data (operative forecast).
    """

    def __init__(self, source="ecmwf-open-data"):
        self.source = source

    def fetch_forecast(self, param_list=None, steps=None):
        """
        Fetch forecast data for specified parameters and steps.
        
        Args:
            param_list (list): List of parameter short names (e.g., ['2t', 'tp', '10u', '10v']).
                             Defaults to ['2t' (temp), 'tp' (precip), '10u', '10v' (wind)].
            steps (list): List of forecast steps in hours. Defaults to [0, 3, 6, ..., 24].
        
        Returns:
            earthkit.data.core.Reader: The data object needed for further processing.
        """
        if param_list is None:
            # 2t: 2m temperature
            # tp: Total precipitation
            # 2d: 2m dewpoint temperature (needed for WBGT)
            # 10u, 10v: 10m wind components
            param_list = ["2t", "tp", "10u", "10v", "2d"]
        
        if steps is None:
            # Default to first 24 hours in 3-hour intervals
            steps = list(range(0, 25, 3))

        print(f"Fetching {param_list} for steps {steps} from {self.source}...")
        
        if self.source == "cds":
            # For ERA5, we usually fetch by date/time, not "step" relative to a forecast.
            # However, earthkit can abstract this. 
            # But usually for CDS we use retrieve() or similar.
            # Let's keep it simple: if source is 'cds', we assume the user wants ERA5 reanalysis
            # and might need to pass different args, or we map 'steps' to times.
            # For simplicity in this prototype, we'll assume the caller knows to pass expected kwargs 
            # if they want specific control, or we default to a standard ERA5-Land or similar request.
            
            # Example ERA5 request structure (often needs years, months, days, times)
            # Here we wrap earthkit's from_source which handles the cdsapi call.
            
            # Note: ERA5 data on CDS is usually "reanalysis-era5-single-levels"
            req = {
                "variable": param_list,
                "product_type": "reanalysis",
                "year": "2023", # Default or passed via kwargs in a real app
                "month": "01",
                "day": "01",
                "time": ["12:00"],
            }
            if hasattr(self, 'kwargs'):
                 req.update(self.kwargs)
            if 'area' in self.kwargs:
                req['area'] = self.kwargs['area']
                
            ds = earthkit.data.from_source(
                "cds",
                "reanalysis-era5-single-levels",
                **req
            )
        else:
            # For Open Data (operative), handling area often means cropping AFTER fetch or passing request params if supported.
            # earthkit-data open-data source might support 'area' if the underlying implementation passes it.
            # However, simpler to just pass it and let earthkit warn or handle it.
            # If not supported, we can crop the returned object.
            
            req_params = {
                "param": param_list,
                "step": steps,
            }
            # ECMWF Open Data (operative) often does not support 'area' in the request for all streams.
            # We will ignore it here and let the caller handle cropping via xarray.

            ds = earthkit.data.from_source(
                self.source,
                **req_params
            )
        
        return ds

    def fetch_era5_history(self, date_start, date_end):
        """
        Dedicated method for fetching historical ERA5 data.
        """
        # Parsing dates is needed for robust impl, passing strings for now
        # param_list specific for ERA5 (names can differ from open data)
        # ERA5 names: '2m_temperature', 'total_precipitation', '10m_u_component_of_wind', ...
        
        request = {
            "product_type": "reanalysis",
            "format": "grib",
            "variable": [
                "2m_temperature",
                "2m_dewpoint_temperature",
                # "total_precipitation", # TP causes dimension issues in GRIB to Xarray conversion due to accumulation steps
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
            ],
            "date": f"{date_start}/{date_end}",
            "time": [
                "00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"
            ],
        }
        
        print(f"Fetching ERA5 history for {date_start} to {date_end}...")
        ds = earthkit.data.from_source("cds", "reanalysis-era5-single-levels", request)
        return ds

    def to_xarray(self, data_object):
        """
        Convert earthkit data object to xarray Dataset for analysis.
        """
        return data_object.to_xarray()

if __name__ == "__main__":
    # Simple test
    fetcher = WeatherFetcher()
    data = fetcher.fetch_forecast(steps=[0, 3])
    print("Data fetched successfully.")
    print(data.summary())
    
    xr_data = fetcher.to_xarray(data)
    print("\nConverted to Xarray:")
    print(xr_data)
