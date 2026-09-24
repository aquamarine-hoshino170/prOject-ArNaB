# Project Arnab: High-Performance Tropical Cyclone Dynamics & Impact Engine

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