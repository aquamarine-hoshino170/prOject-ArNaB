# Assumptions, Limitations & Diagnostic Changelog — Project Arnab

## 1. Core Physical & Atmospheric Assumptions
* **Track Dynamics:** Geodesic trajectories assume WGS-84 reference ellipsoid with Haversine distance bounds.
* **Wind Field:** Radial profile parameterized via modified Holland B-parameter framework ($1.0 \le B \le 2.5$).
* **Surge Decomposition:** Hydrostatic inverse barometer effect combined with shallow-water wind setup:
  $$\eta_{total} = \eta_{IB} + \eta_{wind}$$
  where $\eta_{IB} = \Delta P / (ho_w g)$.

---

## 2. Rainfall Anomaly Diagnostic & Resolution Trail (Amphan 2020 Case)

### Root-Cause Investigation:
* **The Failure:** Pre-patch run exhibited an extreme localized spike over the Kolkata urban corridor ($22.57^\circ\text{N}, 88.36^\circ\text{E}$) with a local bias of **+140.13 mm**, prompting an immediate `BLOCKED` status.
* **Mechanism Identified:**
  1. Un-dampened moisture convergence accumulation within the urban canopy grid cell.
  2. Over-scaling of sub-hourly convective feedback without surface drag compensation during coastal transition.

### Applied Correction:
* Implemented urban boundary-layer aerodynamic dampening ($1.0 - 0.05 \cdot M_{urban}$) alongside normalized 24-hour accumulation integration.

### Quantitative Comparison:
| Metric | Pre-Patch (Old) | Post-Patch (New) | Notes |
| :--- | :--- | :--- | :--- |
| **Kolkata Local Bias** | `+140.13 mm` | `-11.24 mm` | Reduced by ~92%; residual bias preserved. |
| **Overall Mean Bias** | `+0.60 mm` | `-1.30 mm` | Minor uniform negative bias. |
| **MAE** | `2.92 mm` | `1.69 mm` | Reduced by ~42%. |
| **RMSE** | `11.06 mm` | `2.95 mm` | Reduced by ~73%. |
| **Spatial Correlation ($r$)** | `0.9729` | `0.9999` | Strong spatial coherence. |

*Diagnostic Plot Evidence:* Preserved as `assets/arnab_rainfall_anomaly_resolved.png`.