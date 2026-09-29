#!/usr/bin/env python3
"""
PROJECT ARNAB: Edge-Computing Tropical Cyclone Diagnostic & Trajectory Pipeline
NASA Space Apps Challenge 2026.
Pure Physics, Mathematical Modeling, and Edge Ingestion.
"""

import sys
import os
import argparse
import numpy as np

# Ensure core directory is discoverable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from engine import HollandDynamics
from trajectory_cone import generate_forecast_cone
from threat_matrix import evaluate_coastal_threat_matrix, print_threat_table

class CoastalSurgeModel:
    """Hydrodynamic storm surge proxy using Inverse Barometer & Shallow Water Wind Setup."""
    def __init__(self, wind_speed_mps: float, central_pressure_hpa: float, ambient_pressure_hpa: float = 1013.25):
        self.v_wind = float(wind_speed_mps)
        self.p_c = float(central_pressure_hpa)
        self.p_env = float(ambient_pressure_hpa)
        self.rho_water = 1025.0
        self.g = 9.80665

    def compute(self, shelf_length_km: float = 80.0, avg_depth_m: float = 25.0):
        # Inverse Barometer Effect (Pa to water head)
        delta_p = (self.p_env - self.p_c) * 100.0
        eta_ib = delta_p / (self.rho_water * self.g)

        # Wind-stress setup: tau = rho_air * Cd * U^2
        rho_air = 1.15
        cd = 0.0026
        tau_s = rho_air * cd * (self.v_wind ** 2)
        L = shelf_length_km * 1000.0
        H = max(avg_depth_m, 1.0)
        eta_wind = (tau_s * L) / (self.rho_water * self.g * H)

        total = eta_ib + eta_wind
        return {
            'barometric_m': round(eta_ib, 2),
            'wind_setup_m': round(eta_wind, 2),
            'total_m': round(total, 2)
        }

def run_diagnostics(lat: float, lon: float, p_central: float, date_str: str, offline: bool = False):
    print("=" * 72)
    print("      PROJECT ARNAB :: NASA SPACE APPS CHALLENGE 2026")
    print("      Edge-Computing Cyclone Trajectory & Threat Estimator")
    print("=" * 72)
    print(f"[*] Core Coordinate:    Lat {lat:.2f}°N, Lon {lon:.2f}°E")
    print(f"[*] Central Pressure:   {p_central:.1f} hPa")
    print(f"[*] Timestamp:          {date_str}")
    print("-" * 72)

    # 1. Holland Dynamics Gradient Wind Field
    print("[+] Calculating Holland Gradient Wind Profile...")
    holland = HollandDynamics(lat_deg=lat, p_central=p_central, p_env=1013.25, r_max_km=35.0, b_param=1.75)
    r_samples = np.array([10.0, 35.0, 60.0, 100.0, 150.0])
    v_mps, v_knots = holland.gradient_wind_profile(r_samples)
    
    print("    Radius (km) | Wind Speed (m/s) | Wind Speed (kts)")
    for r, vm, vk in zip(r_samples, v_mps, v_knots):
        print(f"    {r:10.1f}  | {vm:15.2f}  | {vk:15.2f}")

    # 2. Kinematic B-Spline Trajectory & Forecast Cone
    print("\n[+] Computing Kinematic Natural Cubic Spline Trajectory & Cone...")
    # Time history / projected track (hours, lat, lon)
    time_steps = np.array([0.0, 6.0, 12.0, 18.0, 24.0, 30.0])
    lats = np.array([lat - 1.8, lat - 1.1, lat - 0.5, lat, lat + 0.6, lat + 1.2])
    lons = np.array([lon - 0.9, lon - 0.5, lon - 0.2, lon, lon + 0.3, lon + 0.7])
    
    lon_smooth, lat_smooth, cone_poly_lon, cone_poly_lat = generate_forecast_cone(time_steps, lats, lons)
    print(f"    [✓] Generated trajectory spline ({len(lat_smooth)} evaluation points).")
    print(f"    [✓] Computed uncertainty polygon bounds ({len(cone_poly_lat)} envelope vertices).")

    # 3. Coastal Surge Model & Threat Matrix
    print("\n[+] Evaluating Coastal Impact Threat Matrix...")
    max_v_mps = float(np.max(v_mps))
    surge_model = CoastalSurgeModel(wind_speed_mps=max_v_mps, central_pressure_hpa=p_central)

    landmarks = [
        ("Digha Coast", 21.62, 87.50),
        ("Sagar Island", 21.65, 88.08),
        ("Kolkata Metro", 22.57, 88.36),
        ("Sundarbans Delta", 21.94, 89.18),
        ("Bakkhali Beach", 21.56, 88.24)
    ]

    matrix = evaluate_coastal_threat_matrix(
        center_lat=lat,
        center_lon=lon,
        holland_model=holland,
        surge_model=surge_model,
        landmarks=landmarks
    )
    print_threat_table(matrix)

    print("=" * 72)
    print("[✓] Pipeline execution finished cleanly in local edge environment.")
    print("=" * 72)

def main():
    parser = argparse.ArgumentParser(description="Project Arnab Edge Runner")
    parser.add_argument("--demo", action="store_true", help="Run Amphan supercyclone benchmark profile")
    parser.add_argument("--lat", type=float, default=21.65, help="Core Latitude")
    parser.add_argument("--lon", type=float, default=88.35, help="Core Longitude")
    parser.add_argument("--pressure", type=float, default=907.0, help="Central Pressure (hPa)")
    parser.add_argument("--date", type=str, default="2020-05-20", help="Date (YYYY-MM-DD)")
    parser.add_argument("--offline", action="store_true", help="Bypass remote fetch")

    args = parser.parse_args()

    if args.demo:
        run_diagnostics(lat=21.65, lon=88.35, p_central=907.0, date_str="2020-05-20", offline=True)
    else:
        run_diagnostics(lat=args.lat, lon=args.lon, p_central=args.pressure, date_str=args.date, offline=args.offline)

if __name__ == "__main__":
    main()
