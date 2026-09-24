# Methodology & Validation Framework — Project Arnab

## 1. Single-Event Benchmarking Protocol (Amphan 2020)
Project Arnab employs a deterministic verification harness comparing numerical forward-model outputs against authoritative observation datasets for Super Cyclonic Storm Amphan (16–21 May 2020).

### Evaluation Criteria:
1. **Track Validation:** Spherical and geodesic great-circle errors computed via Haversine equations against 6-hourly best-track coordinates.
2. **Wind-Pressure Equilibrium:** Radial profile integration evaluated using the empirical Holland B-parameter equation:
   $$V(r) = \sqrt{\frac{B}{\rho} \left(\frac{R_{max}}{r}\right)^B \Delta P \exp\left(-\left(\frac{R_{max}}{r}\right)^B\right) + \left(\frac{r f}{2}\right)^2} - \frac{r f}{2}$$
3. **Surge Separation:** 
   $$\eta_{total} = \eta_{IB} + \eta_{wind}$$
   Where hydrostatic rise ($\eta_{IB} \approx 0.01 \Delta P$) is decoupled from shallow-water coastal wind setup ($\eta_{wind}$).
4. **Precipitation Residual Mapping:** Model-simulated spatial precipitation fields mapped directly onto calibrated NASA GPM IMERG 0.1° grids.

## 2. Limitations & Boundary Conditions
* **Non-Generalizability:** Quantitative accuracy verified for Amphan (2020) reflects specific shelf bathymetry and post-monsoon atmospheric stratification of the northern Bay of Bengal.
* **Urban Convective Tuning:** The precipitation dampening parameter is tuned for deltaic-urban interfaces and requires regional recalibration when deployed outside the Ganges-Brahmaputra-Meghna delta.