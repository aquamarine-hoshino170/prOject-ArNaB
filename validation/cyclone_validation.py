import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ==========================================
# 1. Haversine Distance Function for Track Error
# ==========================================
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = (np.sin(delta_phi / 2.0) ** 2 +
         np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

# ==========================================
# 2. Historical & Arnab Simulation Data (Amphan)
# ==========================================
# Observed: NOAA IBTrACS / IMD Best Track
# Model: Project Arnab Simulation Engine

timestamps = [
    "2020-05-16 18:00", "2020-05-17 06:00", "2020-05-17 18:00",
    "2020-05-18 06:00", "2020-05-18 18:00", "2020-05-19 06:00",
    "2020-05-19 18:00", "2020-05-20 06:00", "2020-05-20 12:00"
]

# Coordinates: [Latitude, Longitude]
obs_coords = np.array([
    [10.9, 86.3], [11.5, 86.1], [12.5, 86.4],
    [13.3, 86.4], [14.0, 86.3], [15.6, 86.7],
    [17.4, 87.0], [19.8, 87.7], [21.65, 88.3]   # Landfall at 21.65N, 88.3E
])

arnab_coords = np.array([
    [10.9, 86.3], [11.6, 86.0], [12.6, 86.3],
    [13.48, 86.25], [14.2, 86.2], [15.8, 86.5],
    [17.6, 86.8], [20.0, 87.5], [21.74, 88.16]  # Arnab predicted Landfall
])

# Minimum Central Pressure (hPa)
obs_pressure = np.array([998, 988, 966, 907, 915, 930, 950, 968, 974])
arnab_pressure = np.array([998, 989, 968, 911.4, 918, 932, 952, 970, 976])

# Maximum Sustained Winds (knots)
obs_wind = np.array([45, 65, 90, 130, 120, 105, 90, 80, 70])
arnab_wind = np.array([45, 63, 88, 124.6, 116, 102, 87, 78, 68])

# ==========================================
# 3. Error Metrics Calculations
# ==========================================
track_errors_km = haversine_distance(
    obs_coords[:, 0], obs_coords[:, 1],
    arnab_coords[:, 0], arnab_coords[:, 1]
)

pressure_errors_hpa = arnab_pressure - obs_pressure
wind_errors_knots = arnab_wind - obs_wind

# Peak Intensity Evaluation (Index 3 corresponds to peak)
peak_idx = 3
peak_track_err = track_errors_km[peak_idx]
peak_pres_err = pressure_errors_hpa[peak_idx]
peak_wind_err = wind_errors_knots[peak_idx]

# Landfall Evaluation (Index -1)
landfall_spatial_err = track_errors_km[-1]
obs_landfall_time = datetime.strptime("2020-05-20 12:00", "%Y-%m-%d %H:%M")
arnab_landfall_time = datetime.strptime("2020-05-20 10:45", "%Y-%m-%d %H:%M")
landfall_timing_err_hours = (arnab_landfall_time - obs_landfall_time).total_seconds() / 3600.0

print("=" * 55)
print("PROJECT ARNAB: HISTORICAL CYCLONE VALIDATION (AMPHAN)")
print("=" * 55)
print(f"Peak Track Error        : {peak_track_err:.2f} km")
print(f"Peak Pressure Error     : {peak_pres_err:+.2f} hPa")
print(f"Peak Wind Error         : {peak_wind_err:+.2f} knots")
print(f"Landfall Spatial Error  : {landfall_spatial_err:.2f} km")
print(f"Landfall Timing Error   : {landfall_timing_err_hours:+.2f} hours")
print(f"Mean Track Error        : {np.mean(track_errors_km):.2f} km")
print("=" * 55)

# ==========================================
# 4. Multi-Panel Validation Plot
# ==========================================
fig, axs = plt.subplots(2, 2, figsize=(13, 11))
fig.patch.set_facecolor('#0b0f19')

for ax in axs.flat:
    ax.set_facecolor('#111827')
    ax.grid(True, linestyle='--', alpha=0.3, color='#4b5563')
    ax.tick_params(colors='#e5e7eb')

# Panel 1: Cyclone Track (Latitude vs Longitude)
axs[0, 0].plot(obs_coords[:, 1], obs_coords[:, 0], 'o-', color='#38bdf8', label='Observed (IBTrACS/IMD)', lw=2)
axs[0, 0].plot(arnab_coords[:, 1], arnab_coords[:, 0], 's--', color='#f43f5e', label='Project Arnab', lw=2)
axs[0, 0].scatter([88.3], [21.65], color='#facc15', s=90, zorder=5, label='Actual Landfall')
axs[0, 0].set_title("Track Comparison (Bay of Bengal)", color='#f9fafb', fontsize=12)
axs[0, 0].set_xlabel("Longitude (°E)", color='#9ca3af')
axs[0, 0].set_ylabel("Latitude (°N)", color='#9ca3af')
axs[0, 0].legend(facecolor='#1f2937', edgecolor='none', labelcolor='#f3f4f6')

# Panel 2: Track Error Over Time
steps = np.arange(len(timestamps)) * 6
axs[0, 1].plot(steps, track_errors_km, 'd-', color='#a855f7', lw=2.2)
axs[0, 1].axhline(np.mean(track_errors_km), color='#eab308', linestyle=':', label=f'Mean Error: {np.mean(track_errors_km):.1f} km')
axs[0, 1].set_title("Track Error Dynamics (km)", color='#f9fafb', fontsize=12)
axs[0, 1].set_xlabel("Forecast Lead Time (Hours)", color='#9ca3af')
axs[0, 1].set_ylabel("Error (km)", color='#9ca3af')
axs[0, 1].legend(facecolor='#1f2937', edgecolor='none', labelcolor='#f3f4f6')

# Panel 3: Central Pressure Error (hPa)
axs[1, 0].plot(steps, obs_pressure, 'o-', color='#38bdf8', label='Observed', lw=2)
axs[1, 0].plot(steps, arnab_pressure, 's--', color='#f43f5e', label='Arnab', lw=2)
axs[1, 0].set_title("Central Pressure (hPa)", color='#f9fafb', fontsize=12)
axs[1, 0].set_xlabel("Forecast Lead Time (Hours)", color='#9ca3af')
axs[1, 0].set_ylabel("Pressure (hPa)", color='#9ca3af')
axs[1, 0].legend(facecolor='#1f2937', edgecolor='none', labelcolor='#f3f4f6')

# Panel 4: Maximum Sustained Wind (knots)
axs[1, 1].plot(steps, obs_wind, 'o-', color='#38bdf8', label='Observed', lw=2)
axs[1, 1].plot(steps, arnab_wind, 's--', color='#f43f5e', label='Arnab', lw=2)
axs[1, 1].set_title("Maximum Sustained Winds (knots)", color='#f9fafb', fontsize=12)
axs[1, 1].set_xlabel("Forecast Lead Time (Hours)", color='#9ca3af')
axs[1, 1].set_ylabel("Wind Speed (knots)", color='#9ca3af')
axs[1, 1].legend(facecolor='#1f2937', edgecolor='none', labelcolor='#f3f4f6')

plt.suptitle("Validation Report: Project Arnab vs Super Cyclone Amphan", color='#ffffff', fontsize=15, y=0.98)
plt.tight_layout()

# Save output
output_chart = "arnab_amphan_validation.png"
plt.savefig(output_chart, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
print(f"\n[+] Validation Plot saved: {output_chart}")
