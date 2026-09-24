import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# 1. Holland Wind Profile Function
# ==============================================================================
def holland_wind_profile(r_km, delta_p_hpa, rmw_km, b_param=1.35, lat_deg=21.5):
    """
    Calculates gradient wind velocity (m/s) as a function of radial distance r (km).
    """
    r_m = r_km * 1000.0
    rmw_m = rmw_km * 1000.0
    delta_p_pa = delta_p_hpa * 100.0  # hPa to Pa
    rho_air = 1.15                    # kg/m^3 (marine boundary layer)
    
    # Coriolis parameter f
    omega = 7.2921e-5
    f = 2.0 * omega * np.sin(np.radians(lat_deg))
    
    # Avoid division by zero at r=0
    r_safe = np.where(r_m == 0, 1.0, r_m)
    term1 = (rmw_m / r_safe) ** b_param
    term2 = (b_param / rho_air) * term1 * delta_p_pa * np.exp(-term1)
    coriolis_term = (r_safe * f / 2.0) ** 2
    
    v = np.sqrt(term2 + coriolis_term) - (r_safe * f / 2.0)
    return np.where(r_km == 0, 0.0, v)

def calculate_danger_radius(r_km, v_ms, threshold_kt=34.0):
    """
    Computes Radius of 34-knot winds (Gale-force Danger Radius).
    """
    threshold_ms = threshold_kt * 0.514444
    indices = np.where((v_ms >= threshold_ms) & (r_km > r_km[np.argmax(v_ms)]))[0]
    if len(indices) > 0:
        return r_km[indices[-1]]
    return 0.0

# ==============================================================================
# 2. বেসলাইন প্যারামিটার এবং পারটার্বেশন সেটআপ
# ==============================================================================
r = np.linspace(1, 350, 700)  # ব্যাসার্ধ ১ কিমি থেকে ৩৫০ কিমি

# Baseline (Amphan coastal phase proxy)
base_p_amb = 1010.0
base_pc = 976.0
base_dp = base_p_amb - base_pc   # 34 hPa
base_rmw = 32.0                  # km
base_b = 1.32

# বেসলাইন প্রোফাইল রান
v_base = holland_wind_profile(r, base_dp, base_rmw, base_b)
base_vmax_kt = np.max(v_base) / 0.514444
base_r_danger = calculate_danger_radius(r, v_base)

# Sensitivity Perturbations
perturbations = {
    "Baseline": {"dp": base_dp, "rmw": base_rmw, "b": base_b, "color": "#f8fafc", "ls": "-"},
    "ΔP +5 hPa (P_c ↓)": {"dp": base_dp + 5.0, "rmw": base_rmw, "b": base_b, "color": "#ef4444", "ls": "--"},
    "ΔP -5 hPa (P_c ↑)": {"dp": base_dp - 5.0, "rmw": base_rmw, "b": base_b, "color": "#38bdf8", "ls": "--"},
    "RMW +10%": {"dp": base_dp, "rmw": base_rmw * 1.10, "b": base_b, "color": "#f59e0b", "ls": "-."},
    "RMW -10%": {"dp": base_dp, "rmw": base_rmw * 0.90, "b": base_b, "color": "#10b981", "ls": "-."},
    "Shape B +10%": {"dp": base_dp, "rmw": base_rmw, "b": base_b * 1.10, "color": "#a855f7", "ls": ":"},
}

# ==============================================================================
# 3. সেনসিটিভিটি টেবিল তৈরি ও কনসোল আউটপুট
# ==============================================================================
print("=" * 80)
print("PROJECT ARNAB: HOLLAND WIND MODEL SENSITIVITY TEST")
print("=" * 80)
print(f"{'Perturbation Case':<22} | {'Vmax (kt)':<10} | {'ΔVmax (%)':<11} | {'R_danger (km)':<14} | {'ΔR_dang (%)'}")
print("-" * 80)

results = {}
for name, p in perturbations.items():
    v = holland_wind_profile(r, p["dp"], p["rmw"], p["b"])
    vmax_kt = np.max(v) / 0.514444
    r_danger = calculate_danger_radius(r, v)
    
    dvmax_pct = ((vmax_kt - base_vmax_kt) / base_vmax_kt) * 100.0
    drange_pct = ((r_danger - base_r_danger) / base_r_danger) * 100.0
    
    results[name] = {"v": v, "vmax": vmax_kt, "danger": r_danger}
    print(f"{name:<22} | {vmax_kt:8.2f} kt | {dvmax_pct:+8.2f}%   | {r_danger:10.1f} km   | {drange_pct:+8.2f}%")

print("=" * 80)

# ==============================================================================
# 4. ভিজ্যুয়ালাইজেশন প্লট তৈরি
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
fig.patch.set_facecolor('#070b14')

for ax in (ax1, ax2):
    ax.set_facecolor('#0f172a')
    ax.tick_params(colors='#e2e8f0')
    ax.grid(True, linestyle='--', alpha=0.25, color='#475569')
    for spine in ax.spines.values():
        spine.set_color('#334155')

# Panel 1: রেডিয়াল উইন্ড ভেলোসিটি কার্ভ (সবগুলো পারটার্বেশন)
for name, p in perturbations.items():
    v_kt = results[name]["v"] / 0.514444
    lw = 2.4 if name == "Baseline" else 1.6
    ax1.plot(r, v_kt, color=p["color"], linestyle=p["ls"], label=name, lw=lw)

# 34-knot Gale Force Line
ax1.axhline(34.0, color='#94a3b8', linestyle=':', label='Gale Threshold (34 kt)')
ax1.set_title("Radial Wind Field Profile V(r)", color='#f8fafc', fontsize=12, pad=10)
ax1.set_xlabel("Radius from Center (km)", color='#94a3b8')
ax1.set_ylabel("Wind Velocity (knots)", color='#94a3b8')
ax1.set_xlim(0, 300)
ax1.legend(facecolor='#1e293b', edgecolor='none', labelcolor='#f1f5f9', fontsize=9)

# Panel 2: ডেঞ্জার রেডিয়াস এবং Vmax সেনসিটিভিটি রেসপন্স বার চার্ট
cases = [k for k in perturbations.keys() if k != "Baseline"]
vmax_deltas = [((results[c]["vmax"] - base_vmax_kt) / base_vmax_kt) * 100.0 for c in cases]
danger_deltas = [((results[c]["danger"] - base_r_danger) / base_r_danger) * 100.0 for c in cases]

y = np.arange(len(cases))
height = 0.35

ax2.barh(y - height/2, vmax_deltas, height, label='ΔVmax (%)', color='#f43f5e')
ax2.barh(y + height/2, danger_deltas, height, label='ΔDanger Radius (%)', color='#38bdf8')
ax2.axvline(0, color='#94a3b8', linestyle='--', linewidth=0.8)

ax2.set_yticks(y)
ax2.set_yticklabels(cases, color='#f8fafc', fontsize=10)
ax2.set_xlabel("Sensitivity Change (%)", color='#94a3b8')
ax2.set_title("Output Parameter Sensitivity Comparison", color='#f8fafc', fontsize=12, pad=10)
ax2.legend(facecolor='#1e293b', edgecolor='none', labelcolor='#f1f5f9')

plt.suptitle("Project Arnab: Holland Model Sensitivity Dynamics (ΔP, RMW, B-param)", color='#ffffff', fontsize=14, y=0.98)
plt.tight_layout()

# ইমেজ সেভ
output_img = "arnab_holland_sensitivity.png"
plt.savefig(output_img, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
print(f"\n[+] Sensitivity Report saved: {output_img}")
