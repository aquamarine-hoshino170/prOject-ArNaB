import matplotlib.pyplot as plt
import os

slides = [
    {
        "num": "01 / 07",
        "title": "PROJECT ARNAB: EDGE-NATIVE CYCLONE PIPELINE",
        "subtitle": "Autonomous Disaster Kinematics & Hydrodynamic Modeling on Termux",
        "points": [
            "Challenge: Tropical Cyclone Intensity & Coastal Inundation Diagnostics.",
            "Execution Platform: Android/Termux (Zero Cloud, Zero High-End Server Dependency).",
            "Core Goal: Lifesaving offline predictive compute directly at the tactical disaster frontline.",
            "Designed for: NASA International Space Apps Challenge 2026."
        ]
    },
    {
        "num": "02 / 07",
        "title": "THE PROBLEM: THE CLOUD COLLAPSE DILEMMA",
        "subtitle": "Why Traditional Cloud Met-Pipelines Fail During Severe Landfall",
        "points": [
            "Severe cyclonic winds (>100 kts) destroy cellular towers, optical fiber, and power grids.",
            "Centralized supercomputers and heavy GIS cloud dashboards become instantly inaccessible.",
            "Tactical evacuation officers on coastal ground lose real-time hydrodynamic predictions.",
            "Heavy dependencies (GDAL, PROJ, Docker) cannot deploy on field emergency terminals."
        ]
    },
    {
        "num": "03 / 07",
        "title": "THE SOLUTION: ZERO-DEPENDENCY EDGE COMPUTE",
        "subtitle": "Pure Mathematical Physics Running Locally on Mobile Terminals",
        "points": [
            "100% Client-Side Pure Python & NumPy Engine running inside Android Termux environment.",
            "Zero GIS Overhead: Geodesic coordinate transforms replaced with pure spherical trigonometry.",
            "Autonomous Execution: Generates high-res telemetry overlays in sub-second compute bursts.",
            "Offline-Resilient Architecture: Functions flawlessly across low-power offline edge nodes."
        ]
    },
    {
        "num": "04 / 07",
        "title": "SCIENTIFIC CORE: ATMOSPHERIC & KINEMATIC FORMULATION",
        "subtitle": "Holland Radial Profile & Geodesic Danger Radii Calculation",
        "points": [
            "Holland Wind-Pressure Model: V(r) = sqrt( (B/rho)*(Rmax/r)^B * dP * exp(-(Rmax/r)^B) + (r*f/2)^2 ) - (r*f/2)",
            "Dynamic Coriolis Parameter: f = 2 * Omega * sin(phi), adapting to instantaneous latitude.",
            "Kinematic ACE Engine: NOAA/WMO standard Accumulated Cyclone Energy (ACE = 10^-4 * sum(Vmax^2)).",
            "Geodesic Spherical Buffers: Precise extraction of R34, R50, and R64 danger zones on EPSG:4326."
        ]
    },
    {
        "num": "05 / 07",
        "title": "HYDRODYNAMIC FORMULATION: STORM SURGE COUPLING",
        "subtitle": "Inverse Barometer & Wind Stress Shallow-Shelf Set-up",
        "points": [
            "Inverse Barometer Effect (Pressure Bulge): eta_ib = (P_env - P_c) / (rho_w * g)  [~0.53 m rise]",
            "Wind Stress Set-up (Shallow Shelf): eta_wind = (tau_w * L) / (rho_w * g * H)  [~2.76 m rise]",
            "Coupled Total Surge Envelope: eta_total = eta_ib + eta_wind  [Total ~3.29 m / 10.8 ft surge]",
            "Calibrated for Bay of Bengal Continental Shelf (Sundarbans & Odisha coastlines)."
        ]
    },
    {
        "num": "06 / 07",
        "title": "DIRECT NASA OPEN-SCIENCE INTEGRATION",
        "subtitle": "Live Raster Stream Coupled with Local Edge Diagnostics",
        "points": [
            "NASA GIBS Integration: Direct REST ingestion from Global Imagery Browse Services WMS gateway.",
            "Sensor Stream: Suomi NPP / VIIRS Corrected Reflectance True-Color imagery.",
            "Plate Carrée Real-Time Alignment: Synchronous projection of math buffers over satellite rasters.",
            "Complete Offline Fallback: If network drops, pipeline switches seamlessly to vector-only mode."
        ]
    },
    {
        "num": "07 / 07",
        "title": "TACTICAL VALUE & GLOBAL DISASTER IMPACT",
        "subtitle": "Transforming Any Smartphone into a Self-Contained Weather Center",
        "points": [
            "Zero Cost & Hyper-Portable: Equips first-responders with supercomputer-level surge modeling.",
            "Transparent Open Science: Zero black-box ML hallucinations; 100% transparent fluid equations.",
            "Tested & Verified: Bay of Bengal Cyclone Simulation executing in milliseconds on mobile hardware.",
            "Open Source & Ready: Fully version-controlled and reproducible on GitHub."
        ]
    }
]

def generate_presentation_deck():
    os.makedirs("deck", exist_ok=True)
    
    for i, slide in enumerate(slides, 1):
        fig, ax = plt.subplots(figsize=(12, 6.75), facecolor='#050b14') # 16:9 Presentation Format
        ax.set_facecolor('#050b14')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Border Frame
        rect = plt.Rectangle((0.02, 0.03), 0.96, 0.94, fill=False, edgecolor='#00b4d8', linewidth=1.5, alpha=0.8)
        ax.add_patch(rect)
        
        # Header Metadata
        ax.text(0.06, 0.90, f"NASA SPACE APPS CHALLENGE 2026 // {slide['num']}", color='#00b4d8', fontsize=11, family='monospace', weight='bold')
        ax.text(0.06, 0.81, slide['title'], color='#ffffff', fontsize=18, family='sans-serif', weight='bold')
        ax.text(0.06, 0.74, slide['subtitle'], color='#90e0ef', fontsize=12, family='sans-serif', style='italic')
        
        # Divider
        ax.plot([0.06, 0.94], [0.70, 0.70], color='#1f3a5f', linewidth=1.5)
        
        # Content Points
        y_pos = 0.58
        for pt in slide['points']:
            # Bullet point circle
            ax.scatter([0.07], [y_pos + 0.01], color='#06d6a0', s=35, zorder=5)
            # Text line
            ax.text(0.09, y_pos, pt, color='#e0e1dd', fontsize=11, family='sans-serif', verticalalignment='center')
            y_pos -= 0.11
            
        # Footer
        ax.text(0.06, 0.07, "PROJECT ARNAB // ARCHITECTURE: PURE-EDGE NUMPY // REPO: github.com/aquamarine-hoshino170/prOject-ArNaB", 
                color='#415a77', fontsize=9, family='monospace')
        
        output_file = f"deck/slide_{i:02d}.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        print(f"[SUCCESS] Rendered -> {output_file}")

if __name__ == "__main__":
    generate_presentation_deck()
