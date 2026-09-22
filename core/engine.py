import numpy as np
import matplotlib.pyplot as plt
from nasa_stream import fetch_nasa_gibs_tile
from trajectory_cone import generate_forecast_cone
from threat_matrix import evaluate_coastal_threat_matrix, print_threat_table

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
        v_knots = v_mps * 1.94384
        return v_mps, v_knots

    def calculate_critical_radii(self, r_km, v_kts):
        max_idx = np.argmax(v_kts)
        out_r, out_v = r_km[max_idx:], v_kts[max_idx:]
        radii = {}
        for th in [64.0, 50.0, 34.0]:
            idx = np.where(out_v >= th)[0]
            radii[f"R{int(th)}"] = round(float(out_r[idx[-1]]), 2) if len(idx) > 0 else None
        return radii

class StormSurgeModel:
    def __init__(self, p_central_hpa, p_env_hpa, v_max_knots):
        self.P_c = float(p_central_hpa)
        self.P_env = float(p_env_hpa)
        self.v_max_mps = float(v_max_knots) / 1.94384
        self.rho_w = 1025.0
        self.rho_a = 1.15
        self.g = 9.80665
        self.c_d = 2.6e-3

    def compute(self, shelf_length_km=80.0, avg_depth_m=25.0):
        delta_p = (self.P_env - self.P_c) * 100.0
        eta_ib = delta_p / (self.rho_w * self.g)
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

def compute_spatial_buffer_circle(center_lat, center_lon, radius_km, num_points=150):
    r_earth = 6371.0
    lat_rad, lon_rad = np.radians(center_lat), np.radians(center_lon)
    d_div_r = radius_km / r_earth
    thetas = np.linspace(0, 2 * np.pi, num_points)
    circle_lats = np.arcsin(np.sin(lat_rad) * np.cos(d_div_r) + np.cos(lat_rad) * np.sin(d_div_r) * np.cos(thetas))
    circle_lons = lon_rad + np.arctan2(np.sin(thetas) * np.sin(d_div_r) * np.cos(lat_rad), np.cos(d_div_r) - np.sin(lat_rad) * np.sin(circle_lats))
    return np.degrees(circle_lats), np.degrees(circle_lons)

def run_project_arnab_pipeline():
    center_lat, center_lon = 17.50, 88.20
    p_central, p_env = 960.0, 1013.25
    
    forecast_hours = [0.0, 12.0, 24.0, 36.0, 48.0]
    forecast_lats  = [17.50, 18.70, 20.10, 21.40, 22.05]
    forecast_lons  = [88.20, 87.80, 87.40, 87.60, 88.30]

    s_lon, s_lat, cone_lon, cone_lat = generate_forecast_cone(forecast_hours, forecast_lats, forecast_lons)

    holland = HollandDynamics(center_lat, p_central, p_env)
    r_axis = np.linspace(1.0, 300.0, 600)
    _, v_kts = holland.gradient_wind_profile(r_axis)
    v_max = float(np.max(v_kts))
    radii = holland.calculate_critical_radii(r_axis, v_kts)

    surge_mod = StormSurgeModel(p_central, p_env, v_max)
    surge = surge_mod.compute()

    coast_lon = [80.27, 80.35, 80.85, 81.70, 82.25, 83.30, 84.10, 85.10, 86.70, 87.05, 87.55, 88.10, 89.15, 90.40, 91.80, 92.20, 92.80, 94.20]
    coast_lat = [13.08, 14.50, 16.00, 16.95, 17.00, 17.70, 18.30, 19.30, 20.30, 21.60, 21.65, 22.00, 21.75, 22.10, 22.35, 21.00, 20.15, 16.00]
    landmarks = [("Chennai", 13.08, 80.27), ("Visakhapatnam", 17.68, 83.21), ("Paradip", 20.31, 86.61), ("Digha", 21.62, 87.51), ("Kolkata", 22.57, 88.36), ("Chattogram", 22.35, 91.78)]

    # Compute Threat Matrix
    matrix = evaluate_coastal_threat_matrix(center_lat, center_lon, holland, surge_mod, landmarks)
    print_threat_table(matrix)

    fig, ax = plt.subplots(figsize=(11, 13), facecolor='#050b14')
    ax.set_facecolor('#081220')

    # NASA Satellite Raster
    nasa_tile = fetch_nasa_gibs_tile("2026-09-21", [79.0, 12.5, 94.0, 23.5])
    if nasa_tile:
        ax.imshow(nasa_tile, extent=[79.0, 94.0, 12.5, 23.5], origin='upper', alpha=0.55)

    ax.plot(coast_lon, coast_lat, color='#00b4d8', linewidth=2.0, label='Coastline')
    ax.fill(cone_lon, cone_lat, color='#ffffff', alpha=0.18, label='Cone of Uncertainty (48h)')
    ax.plot(cone_lon, cone_lat, color='#caf0f8', linestyle=':', linewidth=1.2, alpha=0.6)
    ax.plot(s_lon, s_lat, color='#ffd166', linewidth=2.5, linestyle='-', label='Cubic Spline Track', zorder=4)

    for t_idx, h in enumerate(forecast_hours):
        f_lat, f_lon = forecast_lats[t_idx], forecast_lons[t_idx]
        ax.scatter([f_lon], [f_lat], color='#ff006e', s=50, edgecolors='white', zorder=5)
        ax.text(f_lon + 0.18, f_lat, f"T+{int(h)}h", color='#ffbe0b', fontsize=8.5, family='monospace', weight='bold')

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

    # Plot Landmarks with Dynamic Risk Indicators
    for row in matrix:
        ax.scatter([row['lon']], [row['lat']], color=row['color'], s=65, edgecolors='white', zorder=6)
        label_txt = f"{row['name']} [{row['threat']}]"
        ax.text(row['lon'] + 0.18, row['lat'] - 0.05, label_txt, color='#ffffff', fontsize=8.2, family='monospace', weight='bold')

    hud_telemetry = (
        "PROJECT ARNAB // OPERATIONAL TRACK & CONE PREDICTION\n"
        "--------------------------------------------------\n"
        "Dynamic Model : Natural Cubic Spline + Expanding Error Cone\n"
        "Forecast Range: 00h -> 48h (Bay of Bengal Inbound)\n"
        "Landfall Zone : Sundarbans / Digha Corridor (~T+44h)\n"
        f"0h Core State : Lat {center_lat:.2f}°N, Lon {center_lon:.2f}°E | Pc: {p_central} hPa\n"
        f"Peak Surge Est: {surge['total_m']} m ({surge['total_ft']} ft)\n"
        "--------------------------------------------------\n"
        "Platform      : Android Termux (Edge Offline Compute)"
    )
    ax.text(0.03, 0.97, hud_telemetry, transform=ax.transAxes, color='#caf0f8', fontsize=8.0,
            family='monospace', verticalalignment='top',
            bbox=dict(boxstyle='square,pad=0.6', facecolor='#030712', edgecolor='#00b4d8', alpha=0.92))

    # Threat Matrix Table Overlay in Matplotlib
    threat_summary = "COASTAL THREAT INDEX:\n" + "\n".join([f"{r['name']:<13} : {r['wind_kts']:>4.1f}kt | Surge: {r['surge_m']:>3.1f}m -> {r['threat']}" for r in matrix])
    ax.text(0.03, 0.28, threat_summary, transform=ax.transAxes, color='#e0e1dd', fontsize=7.6,
            family='monospace', verticalalignment='top',
            bbox=dict(boxstyle='square,pad=0.5', facecolor='#030712', edgecolor='#f72585', alpha=0.88))

    ax.set_xlim(79.0, 94.0)
    ax.set_ylim(12.5, 23.5)
    ax.set_title("Cyclone Arnab Coastal Threat Matrix & Landfall Forecast", color='#e0e6ed', fontsize=12, pad=12)
    ax.set_xlabel("Longitude (°E)", color='#8ecae6')
    ax.set_ylabel("Latitude (°N)", color='#8ecae6')
    ax.tick_params(colors='#8ecae6')
    ax.grid(True, linestyle=':', alpha=0.25, color='#48cae4')
    ax.legend(loc='lower right', facecolor='#030712', edgecolor='#00b4d8', labelcolor='#e0e6ed', fontsize=8.0)

    plt.tight_layout()
    plt.savefig("assets/telemetry_map.png", dpi=300)
    print("[SUCCESS] Integrated Threat Matrix Map rendered -> assets/telemetry_map.png")

if __name__ == "__main__":
    run_project_arnab_pipeline()
