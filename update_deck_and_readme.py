import os
import json

base_dir = os.path.expanduser("~/project-arnab")
readme_path = os.path.join(base_dir, "README.md")
methodology_path = os.path.join(base_dir, "docs", "methodology.md")
summary_path = os.path.join(base_dir, "validation", "results", "validation_summary.json")

# 1. Update validation_summary.json with case-specific protocol wording
if os.path.exists(summary_path):
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data["validation_protocol"] = {
        "scope": "Single-Event Benchmark (Super Cyclonic Storm Amphan, May 2020)",
        "generalization_disclaimer": "Metrics validate performance against Bay of Bengal synoptic conditions for Amphan 2020; multi-basin and generalized cross-cyclone validation remains subject to future benchmarking."
    }
    data["validation_status"] = {
        "track_engine": "EVALUATED (Amphan Benchmark: 21.3 km mean track error)",
        "intensity_engine": "EVALUATED (Amphan Benchmark: +4.4 hPa / -5.4 kt error)",
        "storm_surge_engine": "EVALUATED (Amphan Benchmark: -0.18 m total surge error)",
        "precipitation_engine": "EVALUATED WITH RESIDUAL BIAS (Post-dampening: RMSE 2.95 mm, Kolkata bias -11.24 mm)"
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# 2. Update README.md with strictly scoped validation wording
readme_content = """# Project Arnab: High-Performance Tropical Cyclone Dynamics & Impact Engine

Project Arnab is a physics-based, numerical predictive modeling pipeline designed for tropical cyclone tracking, Holland wind-field decomposition, hydro-meteorological storm surge estimation, and satellite precipitation mapping across the North Indian Ocean basin.

---

## 🔬 Validation Protocol & Evidence Base

> **Scientific Boundary & Context:**  
> The quantitative evaluations presented herein are explicitly derived from the **Super Cyclonic Storm Amphan (May 2020)** historical benchmark in the Bay of Bengal. Reference comparisons against NOAA IBTrACS, IMD Best Track, GPM IMERG, and INCOIS/IIT-Delhi datasets demonstrate component feasibility; **these metrics do not claim universal generalization across all oceanic basins or differing mesoscale synoptic regimes.**

### Component Evaluation Summary (Amphan 2020 Benchmark)

| Engine / Component | Evaluation Status | Benchmark Metric | Reference Source |
| :--- | :--- | :--- | :--- |
| **Track Dynamics** | Evaluated against observation | Mean Track Error: `21.3 km` (Peak: `25.8 km`) | NOAA IBTrACS / IMD |
| **Intensity Modeling** | Evaluated against observation | Pressure Error: `+4.4 hPa` \| Wind Error: `-5.4 kt` | IMD Best Track |
| **Storm Surge ($\eta_{total}$)** | Evaluated against observation | Total Surge Error: `-0.18 m` (~3.29 m modeled vs 3.47 m ref) | INCOIS / IIT Delhi |
| **Precipitation Engine** | Evaluated with residual bias | Overall RMSE: `2.95 mm` \| Kolkata local bias: `-11.24 mm` | NASA GPM IMERG |

---

## 🌧️ Precipitation Anomaly Diagnostic Note
Initial pre-patch runs exhibited a localized urban over-accumulation artifact over Kolkata (+140.13 mm local bias). Root-cause analysis traced this to un-dampened convective feedback and accumulation scaling during coastal boundary transition. Application of aerodynamic boundary-layer dampening reduced this local bias to -11.24 mm. The full diagnostic trail is documented in [`docs/assumptions.md`](docs/assumptions.md).

---

## 📂 Repository Hierarchy
* `core/`: Atmospheric and hydrodynamic physics modules.
* `validation/`: Independent evaluation testbeds, scripts, and numerical artifacts (`results/`).
* `docs/`: NASA data provenance (`data_sources.md`), scientific assumptions (`assumptions.md`), and numerical methodology (`methodology.md`).
* `assets/`: Generated spatial maps and validation diagnostics.
"""
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme_content.strip())

# 3. Update docs/methodology.md
methodology_content = """# Methodology & Validation Framework — Project Arnab

## 1. Single-Event Benchmarking Protocol (Amphan 2020)
Project Arnab employs a deterministic verification harness comparing numerical forward-model outputs against authoritative observation datasets for Super Cyclonic Storm Amphan (16–21 May 2020).

### Evaluation Criteria:
1. **Track Validation:** Spherical and geodesic great-circle errors computed via Haversine equations against 6-hourly best-track coordinates.
2. **Wind-Pressure Equilibrium:** Radial profile integration evaluated using the empirical Holland B-parameter equation:
   $$V(r) = \\sqrt{\\frac{B}{\\rho} \\left(\\frac{R_{max}}{r}\\right)^B \\Delta P \\exp\\left(-\\left(\\frac{R_{max}}{r}\\right)^B\\right) + \\left(\\frac{r f}{2}\\right)^2} - \\frac{r f}{2}$$
3. **Surge Separation:** 
   $$\\eta_{total} = \\eta_{IB} + \\eta_{wind}$$
   Where hydrostatic rise ($\\eta_{IB} \\approx 0.01 \\Delta P$) is decoupled from shallow-water coastal wind setup ($\\eta_{wind}$).
4. **Precipitation Residual Mapping:** Model-simulated spatial precipitation fields mapped directly onto calibrated NASA GPM IMERG 0.1° grids.

## 2. Limitations & Boundary Conditions
* **Non-Generalizability:** Quantitative accuracy verified for Amphan (2020) reflects specific shelf bathymetry and post-monsoon atmospheric stratification of the northern Bay of Bengal.
* **Urban Convective Tuning:** The precipitation dampening parameter is tuned for deltaic-urban interfaces and requires regional recalibration when deployed outside the Ganges-Brahmaputra-Meghna delta.
"""
with open(methodology_path, "w", encoding="utf-8") as f:
    f.write(methodology_content.strip())

print("[✓] README, Methodology, and Validation Summary synchronized with contextualized evaluation wording.")
