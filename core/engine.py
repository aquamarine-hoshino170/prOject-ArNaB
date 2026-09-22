import numpy as np
import matplotlib.pyplot as plt
from nasa_stream import fetch_nasa_gibs_tile

class HollandDynamics:
    def __init__(self, lat_deg: float, p_central: float, p_env: float = 1013.25, r_max_km: float = 35.0, b_param: float = 1.75):
        self.lat_rad = np.radians(lat_deg)
        self.P_c = float(p_central)
        self.P_env = float(p_env)
        self.R_max = float(r_max_km) * 1000.0
        self.B = float(b_param)
        self.rho = 1.15
        self.omega = 7.2921159e-5
        self.f = 2.0 * self.omega * np.sin(self.lat_rad)

    def gradient_wind_profile(self, r_km: np.ndarray):
        r_m = np.maximum(r_km * 1000.0, 1e-3)
        delta_p_pa = (self.P_env - self.P_c) * 100.0
        scale_ratio = (self.R_max / r_m) ** self.B
        cyclostrophic_term = (self.B / self.rho) * scale_ratio * delta_p_pa * np.exp(-scale_ratio)
        coriolis_term = (r_m * self.f / 2.0) ** 2
        v_mps = np.sqrt(np.maximum(cyclostrophic_term + coriolis_term, 0.0)) - (r_m * self.f / 2.0)
        v_knots = v_mps * 1.94384
        return v_mps, v_knots

    def calculate_critical_radii(self, r_km: np.ndarray, v_kts: np.ndarray):
        max_idx = np.argmax(v_kts)
        outward_r = r_km[max_idx:]
        outward_v = v_kts[max_idx:]
        radii = {}
        for threshold in [64.0, 50.0, 34.0]:
            idx = np.where(outward_v >= threshold)[0]
            radii[f"R{int(threshold)}"] = round(float(outward_r[idx[-1]]), 2) if len(idx) > 0 else None
        return radii

class StormSurgeModel:
    def __init__(self, p_central_hpa: float, p_env_hpa: float, v_max_knots: float):
        self.P_c = float(p_central_hpa)
        self.P_env = float(p_env_hpa)
        self.v_max_mps = float(v_max_knots) / 1.94384
        self.rho_w = 1025.0
        self.rho_a = 1.15
        self.g = 9.80665
        self.c_d = 2.6e-3

    def compute(self, shelf_length_km: float = 80.0, avg_depth_m: float = 25.0):
        delta_p_pa = (self.P_env - self.P_c) * 100.0
        eta_ib = delta_p_pa / (self.rho_w * self.g)
        L = shelf_length_km * 1000.0
        H = np.maximum(avg_depth_m, 5.0)
        tau_w = self.rho_a * self.c_d * (self.v_max_mps ** 2)
        eta_wind = (tau_w * L) / (self.rho_w * self.g * H)
        total = eta_ib + eta_wind
        return {
            "p_drop": round(self.P_env - self.P_c, 2),
            "eta_ib": round(eta_ib, 2),
            "eta_wind": round(eta_wind, 2),
            "total_m": round(total, 2),
            "total_ft": round(total * 3.28084, 2)
        }

def compute_spatial_buffer_circle(center_lat: float, center_lon: float, radius_km: float, num_points: int = 150):
    r_earth = 6371.0
    lat_rad = np.radians(center_lat)
    lon_rad = np.radians(center_lon)
    d_div_r = radius_km / r_earth
    thetas = np.linspace(0, 2 * np.pi, num_points)
    circle_lats_rad = np.arcsin(np.sin(lat_rad) * np.cos(d_div_r) + np.cos(lat_rad) * np.sin(d_div_r) * np.cos(thetas))
    circle_lons_rad = lon_rad + np.arctan2(np.sin(thetas) * np.sin(d_div_r) * np.cos(lat_rad), np.cos(d_div_r) - np.sin(lat_rad) * np.sin(circle_lats_rad))
    return np.degrees(circle_lats_rad), np.degrees(circle_lons_rad)

def run_project_arnab_pipeline():
    center_lat, center_lon = 17.50, 88.20
    p_central = 960.0
    p_env = 1013.25
    bbox = [79.0, 12.5, 94.0, 23.5]
    date_query = "2026-09-21"

    # Physics calculations
    holland = HollandDynamics(center_lat, p_central, p_env)
    r_axis = np.linspace(1.0, 300.0, 600)
    _, v_kts = holland.gradient_wind_profile(r_axis)
    v_max = float(np.max(v_kts))
    radii = holland.calculate_critical_radii(r_axis, v_kts)

    surge_mod = StormSurgeModel(p_central, p_env, v_max)
    surge = surge_mod.compute()

    # Coastline geometry
    coast_lon = [80.27, 80.35, 80.85, 81.70, 82.25, 83.30, 84.10, 85.10, 86.70, 87.05, 87.55, 88.10, 89.15, 90.40, 91.80, 92.20, 92.80, 94.20]
    coast_lat = [13.08, 14.50, 16.00, 16.95, 17.00, 17.70, 18.30, 19.30, 20.30, 21.60, 21.65, 22.00, 21.75, 22.10, 22.35, 21.00, 20.15, 16.00]
    landmarks = [("Chennai", 13.08, 80.27), ("Visakhapatnam", 17.68, 83.21), ("Paradip", 20.31, 86.61), ("Digha", 21.62, 87.51), ("Kolkata", 22.57, 88.36), ("Chattogram", 22.35, 91.78)]

    fig, ax = plt.subplots(figsize=(10, 11), facecolor='#050b14')
    ax.set_facecolor('#091322')

    # Fetch NASA Satellite Raster
    nasa_tile = fetch_nasa_gibs_tile(date_query, bbox)
    if nasa_tile:
        ax.imshow(nasa_tile, extent=[79.0, 94.0, 12.5, 23.5], origin='upper', alpha=0.55)

    ax.plot(coast_lon, coast_lat, color='#00b4d8', linewidth=2.0, label='Coastline Geometry')

    # Geodesic buffer rings
    buffer_specs = [
        ("R34", radii['R34'], "#ffb703", 0.22, f"Gale Radius (R34: {radii['R34']} km)"),
        ("R50", radii['R50'], "#fb8500", 0.35, f"Storm Radius (R50: {radii['R50']} km)"),
        ("R64", radii['R64'], "#e63946", 0.55, f"Core Hurricane (R64: {radii['R64']} km)")
    ]

    for key, r_val, clr, alph, lbl in buffer_specs:
        if r_val:
            b_lat, b_lon = compute_spatial_buffer_circle(center_lat, center_lon, r_val)
            ax.plot(b_lon, b_lat, color=clr, linestyle='--', linewidth=1.3)
            ax.fill(b_lon, b_lat, color=clr, alpha=alph, label=lbl)

    ax.scatter([center_lon], [center_lat], color='#06d6a0', s=130, edgecolors='white', zorder=6, label='Eye Center (960 hPa)')

    for name, lat, lon in landmarks:
        ax.scatter([lon], [lat], color='#e0e1dd', s=22, zorder=5)
        ax.text(lon + 0.18, lat - 0.05, name, color='#ffffff', fontsize=8.5, family='monospace', weight='bold')

    hud_telemetry = (
        "PROJECT ARNAB // NASA GIBS TELEMETRY PIPELINE\n"
        "--------------------------------------------------\n"
        f"Sensor Base  : Suomi NPP / VIIRS Corrected Reflectance\n"
        f"Position     : {center_lat:.2f}°N, {center_lon:.2f}°E\n"
        f"Max Sustained: {v_max:.2f} kts | Central: {p_central:.1f} hPa\n"
        "--------------------------------------------------\n"
        "HYDRODYNAMIC STORM SURGE PREDICTION\n"
        f"Inverse Barometer: +{surge['eta_ib']:.2f} m\n"
        f"Wind Shear Set-up: +{surge['eta_wind']:.2f} m\n"
        f"TOTAL SURGE RISE : {surge['total_m']:.2f} m ({surge['total_ft']:.1f} ft)\n"
        "--------------------------------------------------\n"
        "Architecture : Pure Python/NumPy (Termux Edge)"
    )

    ax.text(0.03, 0.97, hud_telemetry, transform=ax.transAxes, color='#caf0f8', fontsize=8.2,
            family='monospace', verticalalignment='top',
            bbox=dict(boxstyle='square,pad=0.6', facecolor='#030712', edgecolor='#00b4d8', alpha=0.92))

    ax.set_xlim(79.0, 94.0)
    ax.set_ylim(12.5, 23.5)
    ax.set_title("Cyclone Arnab - NASA GIBS Satellite Underlay & Buffer Rings", color='#e0e6ed', fontsize=12, pad=12)
    ax.set_xlabel("Longitude (°E)", color='#8ecae6')
    ax.set_ylabel("Latitude (°N)", color='#8ecae6')
    ax.tick_params(colors='#8ecae6')
    ax.grid(True, linestyle=':', alpha=0.25, color='#48cae4')
    ax.legend(loc='lower right', facecolor='#030712', edgecolor='#00b4d8', labelcolor='#e0e6ed', fontsize=8.2)

    plt.tight_layout()
    plt.savefig("assets/telemetry_map.png", dpi=300)
    print("[SUCCESS] Master Map updated with NASA GIBS raster -> assets/telemetry_map.png")

if __name__ == "__main__":
    run_project_arnab_pipeline()
