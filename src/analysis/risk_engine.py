import xarray as xr
import numpy as np

class RiskAnalyzer:
    """
    Analyzes weather data to identify risky conditions.
    """

    def __init__(self, thresholds=None):
        # Default thresholds
        # wind_speed: m/s (e.g., > 15 m/s is strong breeze/gale)
        # precipitation: mm (e.g., > 10mm in 3h is heavy)
        # temperature_high: Celsius (> 35 is very hot)
        # temperature_low: Celsius (< 0 is freezing)
        
        default_thresholds = {
            "wind_speed": 15.0, 
            "precipitation": 5.0,
            "temp_high": 35.0,
            "temp_low": 0.0
        }
        
        if thresholds:
            self.thresholds = {**default_thresholds, **thresholds}
        else:
            self.thresholds = default_thresholds

        # New Thresholds for WBGT and Hydro-Geo
        if 'wbgt_high' not in self.thresholds:
            self.thresholds['wbgt_high'] = 30.0 # Standard high risk for WBGT
        if 'rain_flash_flood' not in self.thresholds:
            self.thresholds['rain_flash_flood'] = 30.0 # mm instantaneous/hourly
        if 'rain_landslide' not in self.thresholds:
            self.thresholds['rain_landslide'] = 50.0 # mm accumulation (approx)

    def calculate_wind_speed(self, u, v):
        """Calculates wind speed magnitude from u and v components."""
        return np.sqrt(u**2 + v**2)

    def calculate_vapor_pressure(self, dewpoint_k):
        """
        Approximates vapor pressure (e) in hPa from Dewpoint (Kelvin).
        Using Magnus formula: e = 6.112 * exp(17.67 * Td / (Td + 243.5))
        where Td is in Celsius.
        """
        td_c = dewpoint_k - 273.15
        return 6.112 * np.exp((17.67 * td_c) / (td_c + 243.5))

    def calculate_wbgt(self, temp_k, dewpoint_k):
        """
        Calculates simplified Wet Bulb Globe Temperature (WBGT).
        Australian Bureau of Meteorology approx:
        WBGT = 0.567 * Ta + 0.393 * e + 3.94
        Ta = Air Temp (C), e = Vapor Pressure (hPa)
        """
        ta_c = temp_k - 273.15
        e = self.calculate_vapor_pressure(dewpoint_k)
        wbgt = 0.567 * ta_c + 0.393 * e + 3.94
        return wbgt

    def analyze(self, ds: xr.Dataset):
        """
        Analyzes the dataset and returns a risk map.
        Expects dataset to have standard ECMWF variable names or similar.
        """
        
        # Initialize risk masks (using one variable to get shape)
        # Use a variable that is guaranteed to exist or try '2t'
        target_var = '2t' if '2t' in ds else list(ds.data_vars)[0]
        risk_mask = xr.full_like(ds[target_var], False, dtype=bool)
        details = {}

        # 1. Wind Risk
        if '10u' in ds and '10v' in ds:
            wind_speed = self.calculate_wind_speed(ds['10u'], ds['10v'])
            wind_risk = wind_speed > self.thresholds['wind_speed']
            risk_mask = risk_mask | wind_risk
            details['wind_risk'] = wind_risk
            
        # 2. Hydro-geological Risk (Rain)
        if 'tp' in ds:
            # Convert m to mm
            rain_mm = ds['tp'] * 1000
            
            # Flash Flood Risk (high intensity)
            flash_flood_risk = rain_mm > self.thresholds['rain_flash_flood']
            
            # Landslide Risk (saturation - heavy accumulation)
            # In a real scenario, this would check previous steps or soil moisture ('swvl1'). 
            # For now, we use a higher rain threshold as a proxy.
            landslide_risk = rain_mm > self.thresholds['rain_landslide']
            
            risk_mask = risk_mask | flash_flood_risk | landslide_risk
            details['flash_flood_risk'] = flash_flood_risk
            details['landslide_risk'] = landslide_risk

        # 3. Temperature Risk & WBGT
        if '2t' in ds:
            temp_c = ds['2t'] - 273.15 # Kelvin to Celsius
            
            # Standard Env Risk
            heat_risk = temp_c > self.thresholds['temp_high']
            cold_risk = temp_c < self.thresholds['temp_low']
            
            # WBGT Risk
            wbgt_risk = xr.full_like(ds['2t'], False, dtype=bool)
            if '2d' in ds: # Dewpoint is needed
                wbgt = self.calculate_wbgt(ds['2t'], ds['2d'])
                wbgt_risk = wbgt > self.thresholds['wbgt_high']
            
            risk_mask = risk_mask | heat_risk | cold_risk | wbgt_risk
            details['heat_risk'] = heat_risk
            details['cold_risk'] = cold_risk
            details['wbgt_risk'] = wbgt_risk

        return risk_mask, details

if __name__ == "__main__":
    # Mock specific functionality or rely on integration test
    pass
