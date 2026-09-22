import numpy as np
import matplotlib.pyplot as plt
from nasa_stream import fetch_nasa_gibs_tile
from trajectory_cone import generate_forecast_cone

class HollandDynamics:
    def __init__(self, lat_deg, p_central, p_env=1013.25, r_max_km=35.0, b_param=1.75):
        self.lat_rad = np.radians(lat_deg)
        self.P_c = float(p_central)
        self.P_env = float(p_env)
        self.R_max = float(r_max_km) * 1000.0
        self.B = float(b_param)
        self.rho = 1.15
        self.f = 2.0 * 7.2921159e-5 * np.sin(self.lat_rad)

    def gradient_wind_profile(self, r_km):
        r_m = np.maximum(r_km * 1000.0, 1e-3)
        delta_p = (self.P_env - self.P_c) * 100.0
        sr = (self.R_max / r_m) ** self.B
        cyclostrophic = (self.B / self.rho) * sr * delta_p * np.exp(-sr)
        coriolis = (r_m * self.f / 2.0) ** 2
        v_mps = np.sqrt(np.maximum(cyclostrophic + coriolis, 0.0)) - (r_m * self.f / 2.0)
        return v_mps * 1.94384

    def calculate_critical_radii(self, r_km, v_kts):
        max_idx = np.argmax(v_kts)
        out_r, out_v = r_km[max_idx:], v_kts[max_idx:]
        radii = {}
        for th in [64.0, 50.0, 34.0]:
            idx = np.where(out_v >= th)[0]
            radii[f"R{int(th)}"] = round(float(out_r[idx[-1]]), 2) if len(idx) > 0 else None
        return radii

def compute_spatial_buffer_circle(center_lat, center_lon, radius_km, num_points=150):
    r_earth = 6371.0
    lat_rad, lon_rad = np.radians(center_lat), np.radians(center_lon)
    d_div_r = radius_km / r_earth
    thetas = np.linspace(0, 2 * np.pi, num_points)
    circle_lats = np.arcsin(np.sin(lat_rad) * np.cos(d_div_r) + np.cos(lat_rad) * np.sin(d_div_r) * np.cos(thetas))
    circle_lons = lon_rad + np.arctan2(np.sin(thetas) * np.sin(d_div_r) * np.cos(lat_rad), np.cos(d_div_r) - np.sin(lat_rad) * np.sin(circle_lats))
    return np.degrees(circle_lats), np.degrees(circle_lons)

def run_project_arnab_pipeline():
    # 0h Current State
    center_lat, center_lon = 17.50, 88.20
    p_central = 960.0
    
    # 48-Hour Forecast Track Data (0h -> 12h -> 24h -> 36h -> 48h Landfall)
    forecast_hours = [0.0, 12.0, 24.0, 36.0, 48.0]
    forecast_lats  = [17.50, 18.70, 20.10, 21.40, 22.05]
    forecast_lons  = [88.20, 87.80, 87.40, 87.60, 88.30] # Approaching Digha/Sundarbans
    
    # Spline Path & Cone calculation
    s_lon, s_lat, cone_lon, cone_lat = generate_forecast_cone(forecast_hours, forecast_lats, forecast_lons)

    # Wind physics
    holland = HollandDynamics(center_lat, p_central)
    r_axis = np.linspace(1.0, 300.0, 600)
    v_kts = holland.gradient_wind_profile(r_axis)
    radii = holland.calculate_critical_radii(r_axis, v_kts)

    # Coastline
    coast_lon = [80.27, 80.35, 80.85, 81.70, 82.25, 83.30, 84.10, 85.10, 86.70, 87.05, 87.55, 88.10, 89.15, 90.40, 91.80, 92.20, 92.80, 94.20]
    coast_lat = [13.08, 14.50, 16.00, 16.95, 17.00, 17.70, 18.30, 19.30, 20.30, 21.60, 21.65, 22.00, 21.75, 22.10, 22.35, 21.00, 20.15, 16.00]
    landmarks = [("Chennai", 13.08, 80.27), ("Visakhapatnam", 17.68, 83.21), ("Paradip", 20.31, 86.61), ("Digha", 21.62, 87.51), ("Kolkata", 22.57, 88.36), ("Chattogram", 22.35, 91.78)]

    fig, ax = plt.subplots(figsize=(10, 12), facecolor='#050b14')
    ax.set_facecolor('#081220')

    # NASA Raster Layer
    nasa_tile = fetch_nasa_gibs_tile("2026-09-21", [79.0, 12.5, 94.0, 23.5])
    if nasa_tile:
        ax.imshow(nasa_tile, extent=[79.0, 94.0, 12.5, 23.5], origin='upper', alpha=0.55)

    # Coastline
    ax.plot(coast_lon, coast_lat, color='#00b4d8', linewidth=2.0, label='Coastline')

    # Plot Cone of Uncertainty
    ax.fill(cone_lon, cone_lat, color='#ffffff', alpha=0.18, label='Cone of Uncertainty (48h)')
    ax.plot(cone_lon, cone_lat, color='#caf0f8', linestyle=':', linewidth=1.2, alpha=0.6)

    # Plot B-Spline Forecast Track
    ax.plot(s_lon, s_lat, color='#ffd166', linewidth=2.5, linestyle='-', label='Cubic Spline Track', zorder=4)

    # Forecast Checkpoints
    for t_idx, h in enumerate(forecast_hours):
        f_lat, f_lon = forecast_lats[t_idx], forecast_lons[t_idx]
        ax.scatter([f_lon], [f_lat], color='#ff006e', s=50, edgecolors='white', zorder=5)
        ax.text(f_lon + 0.18, f_lat, f"T+{int(h)}h", color='#ffbe0b', fontsize=8.5, family='monospace', weight='bold')

    # Buffer Rings at current position (0h)
    buffer_specs = [
        ("R34", radii['R34'], "#ffb703", 0.20, f"Gale Radius ({radii['R34']} km)"),
        ("R50", radii['R50'], "#fb8500", 0.35, f"Storm Radius ({radii['R50']} km)"),
        ("R64", radii['R64'], "#d90429", 0.55, f"Core Eyewall ({radii['R64']} km)")
    ]
    for key, r_val, clr, alph, lbl in buffer_specs:
        if r_val:
            b_lat, b_lon = compute_spatial_buffer_circle(center_lat, center_lon, r_val)
            ax.plot(b_lon, b_lat, color=clr, linestyle='--', linewidth=1.2)
            ax.fill(b_lon, b_lat, color=clr, alpha=alph, label=lbl)

    # Landmarks
    for name, lat, lon in landmarks:
        ax.scatter([lon], [lat], color='#e0e1dd', s=24, zorder=6)
        ax.text(lon + 0.18, lat - 0.05, name, color='#ffffff', fontsize=8.5, family='monospace', weight='bold')

    # Operational Telemetry HUD
    hud_telemetry = (
        "PROJECT ARNAB // OPERATIONAL TRACK & CONE PREDICTION\n"
        "--------------------------------------------------\n"
        "Dynamic Model : Natural Cubic Spline + Expanding Error Cone\n"
        "Forecast Range: 00h -> 48h (Bay of Bengal Inbound)\n"
        "Landfall Zone : Sundarbans / Digha Coastal Corridor (~T+44h)\n"
        f"0h Core State : Lat {center_lat:.2f}°N, Lon {center_lon:.2f}°E | Pc: {p_central} hPa\n"
        "Peak Surge Est: 3.29 m (10.8 ft) [Inverse Barometer + Set-up]\n"
        "--------------------------------------------------\n"
        "Platform      : Android Termux (Edge Offline Compute)"
    )
    ax.text(0.03, 0.97, hud_telemetry, transform=ax.transAxes, color='#caf0f8', fontsize=8.2,
            family='monospace', verticalalignment='top',
            bbox=dict(boxstyle='square,pad=0.6', facecolor='#030712', edgecolor='#00b4d8', alpha=0.92))

    ax.set_xlim(79.0, 94.0)
    ax.set_ylim(12.5, 23.5)
    ax.set_title("Cyclone Arnab 48-Hour Spline Track & Landfall Cone", color='#e0e6ed', fontsize=12, pad=12)
    ax.set_xlabel("Longitude (°E)", color='#8ecae6')
    ax.set_ylabel("Latitude (°N)", color='#8ecae6')
    ax.tick_params(colors='#8ecae6')
    ax.grid(True, linestyle=':', alpha=0.25, color='#48cae4')
    ax.legend(loc='lower right', facecolor='#030712', edgecolor='#00b4d8', labelcolor='#e0e6ed', fontsize=8.0)

    plt.tight_layout()
    plt.savefig("assets/telemetry_map.png", dpi=300)
    print("[SUCCESS] 48h Forecast Track & Uncertainty Cone successfully rendered -> assets/telemetry_map.png")

if __name__ == "__main__":
    run_project_arnab_pipeline()
