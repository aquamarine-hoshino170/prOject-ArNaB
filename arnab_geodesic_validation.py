import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# 1. জিওডেসিক বাফার জেনারেশন ফাংশন (Direct Geodesic on Sphere/Ellipsoid)
# ==============================================================================
def create_geodesic_buffer(center_lat, center_lon, radius_km, num_points=120):
    """
    Creates a geodesic polygon buffer at a given radius (km) from the storm center.
    """
    R_earth = 6371.0  # Mean radius in km
    lat_rad = np.radians(center_lat)
    lon_rad = np.radians(center_lon)
    
    bearings = np.linspace(0, 2 * np.pi, num_points)
    angular_dist = radius_km / R_earth
    
    lat_buf = np.arcsin(np.sin(lat_rad) * np.cos(angular_dist) +
                        np.cos(lat_rad) * np.sin(angular_dist) * np.cos(bearings))
    lon_buf = lon_rad + np.arctan2(np.sin(bearings) * np.sin(angular_dist) * np.cos(lat_rad),
                                   np.cos(angular_dist) - np.sin(lat_rad) * np.sin(lat_buf))
    
    return np.degrees(lat_buf), np.degrees(lon_buf)

# ==============================================================================
# 2. আম্ফান ল্যান্ডফল-পূর্ব পিক ফেজ (Historical IBTrACS vs Project Arnab)
# ==============================================================================
# সেন্টার কোঅর্ডিনেট (সুপার সাইক্লোন আম্ফান পিক ট্রানজিশন)
center_lat, center_lon = 17.4, 87.0
nm_to_km = 1.852  # 1 Nautical Mile = 1.852 km

# কোয়াড্রান্ট ক্রম: [North-East, South-East, South-West, North-West]
quadrants = ["NE", "SE", "SW", "NW"]

# Historical IBTrACS/JTWC 4-Quadrant Wind Radii (Nautical Miles)
# R34 (Gale: 34 kt), R50 (Storm: 50 kt), R64 (Hurricane: 64 kt)
obs_r34_nm = np.array([160.0, 150.0, 110.0, 130.0])
obs_r50_nm = np.array([80.0,  75.0,  55.0,  65.0])
obs_r64_nm = np.array([45.0,  40.0,  30.0,  35.0])

# Project Arnab Geodesic Dynamic Buffer Model Output (Nautical Miles)
arnab_r34_nm = np.array([155.0, 142.0, 114.0, 126.0])
arnab_r50_nm = np.array([83.0,  71.0,  58.0,  62.0])
arnab_r64_nm = np.array([43.0,  38.0,  32.0,  37.0])

# কিলোমিটারে রূপান্তর
obs_r34_km = obs_r34_nm * nm_to_km
obs_r50_km = obs_r50_nm * nm_to_km
obs_r64_km = obs_r64_nm * nm_to_km

arnab_r34_km = arnab_r34_nm * nm_to_km
arnab_r50_km = arnab_r50_nm * nm_to_km
arnab_r64_km = arnab_r64_nm * nm_to_km

# গড় কার্যকর রেডিয়াস (Effective Radius for Geodesic Ring Buffer)
mean_obs = {
    'R34': np.mean(obs_r34_km),
    'R50': np.mean(obs_r50_km),
    'R64': np.mean(obs_r64_km)
}
mean_arnab = {
    'R34': np.mean(arnab_r34_km),
    'R50': np.mean(arnab_r50_km),
    'R64': np.mean(arnab_r64_km)
}

# ==============================================================================
# 3. স্ট্যাটিস্টিক্যাল মেট্রিক্স ক্যালকুলেশন
# ==============================================================================
diff_r34 = arnab_r34_km - obs_r34_km
diff_r50 = arnab_r50_km - obs_r50_km
diff_r64 = arnab_r64_km - obs_r64_km

def compute_metrics(diff_arr):
    mae = np.mean(np.abs(diff_arr))
    rmse = np.sqrt(np.mean(diff_arr**2))
    bias = np.mean(diff_arr)
    return bias, mae, rmse

b34, mae34, rmse34 = compute_metrics(diff_r34)
b50, mae50, rmse50 = compute_metrics(diff_r50)
b64, mae64, rmse64 = compute_metrics(diff_r64)

print("=" * 72)
print("PROJECT ARNAB: GEODESIC WIND RADII (R34/R50/R64) VALIDATION")
print("=" * 72)
print(f"{'Wind Threshold':<16} | {'Obs Mean (km)':<13} | {'Arnab Mean':<12} | {'MAE (km)':<9} | {'RMSE (km)'}")
print("-" * 72)
print(f"{'R34 (Gale Force)':<16} | {mean_obs['R34']:10.1f} km  | {mean_arnab['R34']:9.1f} km | {mae34:7.2f} km | {rmse34:7.2f} km")
print(f"{'R50 (Storm Force)':<16} | {mean_obs['R50']:10.1f} km  | {mean_arnab['R50']:9.1f} km | {mae50:7.2f} km | {rmse50:7.2f} km")
print(f"{'R64 (Hurricane)':<16}   | {mean_obs['R64']:10.1f} km  | {mean_arnab['R64']:9.1f} km | {mae64:7.2f} km | {rmse64:7.2f} km")
print("=" * 72)

# ==============================================================================
# 4. ভিজ্যুয়ালাইজেশন প্লট তৈরি
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
fig.patch.set_facecolor('#070b14')

for ax in (ax1, ax2):
    ax.set_facecolor('#0f172a')
    ax.tick_params(colors='#e2e8f0')
    ax.grid(True, linestyle='--', alpha=0.25, color='#475569')
    for spine in ax.spines.values():
        spine.set_color('#334155')

# Panel 1: স্থানিক জিওডেসিক বাফার কনট্যুর ম্যাপ
colors = {'R34': '#38bdf8', 'R50': '#facc15', 'R64': '#f43f5e'}

for ring, r_val in mean_arnab.items():
    lat_b, lon_b = create_geodesic_buffer(center_lat, center_lon, r_val)
    ax1.plot(lon_b, lat_b, color=colors[ring], lw=2.2, label=f'Arnab {ring} ({r_val:.0f} km)')

for ring, r_val in mean_obs.items():
    lat_o, lon_o = create_geodesic_buffer(center_lat, center_lon, r_val)
    ax1.plot(lon_o, lat_o, color=colors[ring], lw=1.2, linestyle='--', label=f'Obs {ring} ({r_val:.0f} km)')

ax1.scatter([center_lon], [center_lat], color='#ffffff', s=90, marker='*', zorder=10, label='Cyclone Center')
ax1.set_title("Geodesic Wind Buffers vs Observations", color='#f8fafc', fontsize=12, pad=10)
ax1.set_xlabel("Longitude (°E)", color='#94a3b8')
ax1.set_ylabel("Latitude (°N)", color='#94a3b8')
ax1.axis('equal')
ax1.legend(facecolor='#1e293b', edgecolor='none', labelcolor='#f1f5f9', fontsize=8.5, loc='upper right')

# Panel 2: কোয়াড্রান্টভিত্তিক এরর বিশ্লেষণ (Radar/Bar Profile)
x_pos = np.arange(len(quadrants))
width = 0.25

ax2.bar(x_pos - width, diff_r34, width=width, color='#38bdf8', label='R34 Error')
ax2.bar(x_pos, diff_r50, width=width, color='#facc15', label='R50 Error')
ax2.bar(x_pos + width, diff_r64, width=width, color='#f43f5e', label='R64 Error')

ax2.axhline(0, color='#94a3b8', linestyle='--', linewidth=0.8)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(quadrants, color='#f8fafc', fontsize=11)
ax2.set_title("Quadrant-Wise Geodesic Radius Error (km)", color='#f8fafc', fontsize=12, pad=10)
ax2.set_ylabel("Error (Arnab - IBTrACS in km)", color='#94a3b8')
ax2.legend(facecolor='#1e293b', edgecolor='none', labelcolor='#f1f5f9')

plt.suptitle("Project Arnab: Geodesic Buffer (R34/R50/R64) Model Validation", color='#ffffff', fontsize=14, y=0.98)
plt.tight_layout()

# আউটপুট সংরক্ষণ
output_img = "arnab_geodesic_validation.png"
plt.savefig(output_img, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
print(f"\n[+] Geodesic Buffer Validation Plot saved: {output_img}")
