# DATA_SOURCES.md — Project Arnab Data Provenance & Methodology

This document outlines the authoritative datasets, remote sensing products, and operational atmospheric models ingested into **Project Arnab**, strictly compliant with the NASA Space Apps / Earth Science Data Systems (ESDS) open-access provenance guidelines.

---

## 1. Primary Datasets Ingestion Matrix

| Field | Dataset 1: Tropical Cyclone Best Track | Dataset 2: Satellite Precipitation (GPM) | Dataset 3: Ocean Surface Winds & SST | Dataset 4: Global Elevation & Bathymetry |
| :--- | :--- | :--- | :--- | :--- |
| **Dataset Name** | **IBTrACS** (International Best Track Archive for Climate Stewardship) | **GPM IMERG Final Run** (Global Precipitation Measurement) | **NASA MUR SST & CYGNSS Winds** | **GEBCO / SRTM Bathymetry & Topography** |
| **Provider** | NOAA NCEI / WMO Tropical Cyclone Programme | NASA Goddard Space Flight Center (GSFC) / PMM | NASA JPL PO.DAAC | GEBCO Compilation Group / NASA JPL |
| **Dataset Version** | Version v04r00 | Version 07B (GPM_3IMERGM) | MUR v4.1 / CYGNSS v3.2 | GEBCO 2023 Grid / SRTM v3 |
| **Acquisition Date** | May 16, 2020 – May 21, 2020 (Event-specific query) | May 16, 2020 – May 21, 2020 | May 15, 2020 – May 20, 2020 | Static Reference Base (Acquired: 2026-09) |
| **Spatial Resolution**| Point coordinates (0.1° equivalent tracking) | 0.1° × 0.1° (~10 km × 10 km) | 0.01° (SST) / 25 km (CYGNSS Wind) | 15 arc-second (~450 m at equator) |
| **Temporal Resolution**| 3-hourly / 6-hourly best-track intervals | Half-hourly (0.5 hr) & Daily Accumulations | Daily (SST) / Sub-daily passes (CYGNSS) | Static Geodetic Grid |
| **Variables Used** | `lat`, `lon`, `nature`, `wmo_wind`, `wmo_pres`, `storm_dir`, `storm_speed`, `r34`, `r50`, `r64` | `precipitationCal`, `precipitationQualityIndex`, `probabilityLiquidPrecipitation` | `analysed_sst`, `surface_wind_speed` | `elevation`, `bathymetric_depth` |
| **Processing Applied**| 1. Geodesic distance tracking via WGS-84 Haversine equations.<br>2. Spline temporal interpolation to 1-hr intervals.<br>3. Quadrant wind radii decomposition (NE, SE, SW, NW). | 1. Cropped to Bay of Bengal bounding box (`[20°N–25°N, 85°E–91°E]`).<br>2. Unit conversion to total accumulated depth ($mm$).<br>3. Bias correction against regional anomalies. | 1. Sea Surface Temperature ($SST$) gradient extraction for Tropical Cyclone Heat Potential ($TCHP$).<br>2. Marine boundary wind stress calculation. | 1. Bilinear spatial interpolation matching coastal surge zones.<br>2. Bathymetric slope integration for wind-setup surge modeling ($\eta_{wind}$). |
| **License / Terms** | Open Data (Creative Commons Zero / Public Domain) | NASA Open Data Policy (Free and open access) | NASA Open Data Policy (Free and open access) | Open Access (Creative Commons Attribution 4.0 International) |

---

## 2. Pipeline Processing & Quality Assurance (QA)

### A. Track & Wind Buffer Validation (Holland & Geodesic Models)
* **Model Base:** Holland B-parameter radial velocity profiles combined with ellipsoidal geodesic buffering.
* **Ground Truth Source:** NOAA IBTrACS North Indian Ocean (NI) basin records (specifically Super Cyclonic Storm Amphan).
* **Reference Metrics:** Validated against operational JTWC and IMD (India Meteorological Department) reported radii ($R_{34}$, $R_{50}$, $R_{64}$).

### B. Precipitation & Anomaly Resolution
* **Observation Baseline:** NASA GPM IMERG calibrated precipitation product (`precipitationCal`).
* **Error Correction Framework:** Evaluated using Mean Bias (MB), MAE, RMSE, and Spatial Pearson Correlation ($r$).
* **Urban Convective Adjustment:** Addressed localized moisture convergence over-estimations in urban/delta areas (e.g., Kolkata metropolitan corridor) via boundary-layer dampening.

### C. Storm Surge Formulation
* **Atmospheric Drivers:** Inverse Barometer contribution ($\eta_{IB}$) derived from atmospheric pressure deficits relative to the ambient field ($P_{ambient} - P_c$).
* **Oceanographic Drivers:** Shallow-water coastal wind setup ($\eta_{wind}$) computed across the regional bathymetric shelf using GEBCO terrain depth.

---

## 3. Data Citations

1. **NOAA/NCEI IBTrACS:**
   > Knapp, K. R., et al. (2018). *International Best Track Archive for Climate Stewardship (IBTrACS) Project, Version 4*. NOAA National Centers for Environmental Information. https://doi.org/10.25921/82ty-9e16
2. **NASA GPM IMERG:**
   > Huffman, G. J., et al. (2023). *GPM IMERG Final Precipitation L3 Half Hourly 0.1 degree x 0.1 degree V07*, Greenbelt, MD, Goddard Earth Sciences Data and Information Services Center (GES DISC). https://doi.org/10.5067/GPM/IMERG/3B-HH/07
3. **GEBCO Bathymetry:**
   > GEBCO Compilation Group (2023). *GEBCO 2023 Grid*. doi:10.5285/f98b0f41-b17c-47ff-e053-6c86abc0f30f