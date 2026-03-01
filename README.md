# Municipality-Scale Flood Risk Mapping in La Guajira, Colombia

**Using Sentinel-1 SAR and Ensemble Machine Learning (2015--2025)**

Cristian Espinal Maya [![ORCID](https://img.shields.io/badge/ORCID-0009--0000--1009--8388-green)](https://orcid.org/0009-0000-1009-8388) · Santiago Jimenez Londono [![ORCID](https://img.shields.io/badge/ORCID-0009--0007--9862--7133-green)](https://orcid.org/0009-0007-9862-7133)

School of Applied Sciences and Engineering, Universidad EAFIT, Medellin, Colombia

[![GitHub](https://img.shields.io/badge/GitHub-Cespial%2Fguajira--flood--risk-blue)](https://github.com/Cespial/guajira-flood-risk) · [![License: MIT](https://img.shields.io/badge/Code-MIT-yellow)](LICENSE) · [![License: CC BY 4.0](https://img.shields.io/badge/Manuscript-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

---

## Abstract

We present a reproducible, open-access framework that delivers municipality-level flood risk statistics for all 15 municipalities of the Department of La Guajira, Colombia (20,848 km²; ~1.0 million inhabitants). This study replicates and extends the methodology developed for the Department of Antioquia, adapting it to the unique challenges of an arid/semi-arid Caribbean department where the drought-flood paradox creates distinctive hazard dynamics.

La Guajira — Colombia's northernmost and most arid department — faces an extreme climate duality: severe droughts during El Nino years and catastrophic flash flooding during La Nina events. The Wayuu indigenous population (~45% of residents) is disproportionately vulnerable to both extremes. We process Sentinel-1 C-band SAR scenes (2015–2025) within Google Earth Engine using adaptive Otsu thresholding with a novel Sand Exclusion Layer (SEL) to address the critical sand-water backscatter confusion in arid terrain. Eighteen predictor variables are integrated into a weighted ensemble of Random Forest, XGBoost, and LightGBM under spatial five-fold cross-validation. ENSO-stratified analysis quantifies the amplification of flood extent during La Nina years relative to El Nino drought conditions.

## Study Area Context

La Guajira is divided into three subregions with markedly different characteristics:

| Subregion | Municipalities | Climate | Rainfall (mm/yr) | Terrain |
|-----------|---------------|---------|-------------------|---------|
| **Alta Guajira** | 2 (Uribia, Manaure) | Hyper-arid desert (BWh) | 125–400 | Dunes, salt flats, Serrania de Macuira |
| **Media Guajira** | 3 (Riohacha, Maicao, Dibulla) | Semi-arid (BSh) | 400–800 | Coastal plains, Rancheria delta |
| **Baja Guajira** | 10 (Albania, Barrancas, etc.) | Tropical savanna (Aw) | 800–2,500+ | Sierra Nevada foothills, river valleys |

### Key Flood Mechanisms

- **Rancheria River flooding**: Main threat. Torrential behavior from Sierra Nevada runoff (Sep-Nov)
- **Sierra Nevada flash floods**: Short, steep rivers (Palomino, Jerez) cause rapid flooding in Dibulla
- **Coastal flooding**: Storm surge from Caribbean hurricanes (2022 Julia, 2024 Rafael)
- **Arroyo flash floods**: Ephemeral streams in arid zones activate during intense rainfall

### Notable Flood Events

- **2010–2011 (La Nina)**: Catastrophic flooding across Caribbean Colombia
- **2022 (Hurricane Julia)**: 8 municipalities declared calamity
- **2024 (Hurricane Rafael)**: 195,000+ people affected

## Methodological Adaptations for Arid/Semi-Arid Terrain

This replication introduces several adaptations per the Antioquia framework's Replication Guide:

1. **Sand Exclusion Layer (SEL)**: Persistent low-backscatter sand surfaces are masked using multi-temporal SAR statistics to prevent sand-water confusion
2. **Reduced training samples**: 2,500 per class (vs. 5,000 in Antioquia) due to lower flood event frequency
3. **Lowered JRC threshold**: Flood-positive training labels use JRC occurrence >= 10% (vs. 25%)
4. **Larger minimum water area**: 2 ha minimum (vs. 1 ha) to filter tidal noise and arroyo artifacts
5. **Coastal/tidal masking**: Buffer masks for Manaure salt flats and tidal zones
6. **Unimodal seasonal analysis**: Peak wet season Sep-Nov (vs. bimodal Andean pattern)

## Repository Structure

```
.
├── gee_config.py              # Central configuration (La Guajira parameters)
├── scripts/
│   ├── 01_sar_water_detection.py
│   ├── 02_jrc_water_analysis.py
│   ├── 03_flood_susceptibility_features.py
│   ├── 04_ml_flood_susceptibility.py
│   ├── 05_population_exposure.py
│   ├── 06_climate_analysis.py
│   ├── 07_visualization.py
│   ├── 08_generate_tables.py
│   └── 09_quality_control.py
├── overleaf/                  # Manuscript (preprint format)
│   ├── main.tex
│   ├── references.bib         # 37 references (25 La Guajira-specific + 12 foundational)
│   └── figures/
├── bib/                       # Additional bibliography resources
├── data/                      # Downloaded data (auto-created)
├── outputs/                   # Results (auto-created)
└── README.md
```

## Data Sources

All data are open-access and processed via [Google Earth Engine](https://earthengine.google.com/):

- **Sentinel-1 GRD** (ESA/Copernicus) — 10 m SAR flood detection
- **JRC Global Surface Water** — 38-year water dynamics
- **SRTM DEM v3** — Topographic features (30 m)
- **MERIT Hydro** — HAND computation (90 m)
- **CHIRPS / ERA5-Land** — Precipitation and soil moisture
- **ESA WorldCover / Sentinel-2** — Land cover and NDVI
- **WorldPop** — Population density (100 m)
- **FAO GAUL** — Administrative boundaries

## Reproducing the Analysis

### Requirements

- Python 3.10+
- Google Earth Engine account ([sign up](https://signup.earthengine.google.com/))
- Libraries: `earthengine-api`, `scikit-learn`, `xgboost`, `lightgbm`, `shap`, `matplotlib`, `geopandas`

### Setup

```bash
# Create GEE project
# Go to console.cloud.google.com > Create project: ee-flood-risk-guajira
# Enable Earth Engine API

# Configure
echo "GEE_PROJECT_ID=ee-flood-risk-guajira" > .env

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Authenticate
earthengine authenticate
```

### Pipeline

```bash
# 1. SAR water detection (~3h on GEE — smaller area than Antioquia)
python scripts/01_sar_water_detection.py

# 2. JRC validation analysis (~20 min)
python scripts/02_jrc_water_analysis.py

# 3. Feature engineering (~1.5h)
python scripts/03_flood_susceptibility_features.py

# 4. ML model training (<30 min on laptop)
python scripts/04_ml_flood_susceptibility.py

# 5. Population exposure analysis (~45 min)
python scripts/05_population_exposure.py

# 6. ENSO and seasonal analysis (~45 min)
python scripts/06_climate_analysis.py

# 7. Generate all figures (~15 min)
python scripts/07_visualization.py

# 8. Generate tables (~5 min)
python scripts/08_generate_tables.py

# 9. Quality control (~10 min)
python scripts/09_quality_control.py
```

## Key Considerations

### Sand-Water Confusion in SAR

La Guajira's extensive desert and sand dune areas produce low C-band SAR backscatter that is spectrally similar to water surfaces. This study implements a Sand Exclusion Layer (SEL) following Martinis et al. (2018) to mitigate false flood detections.

### Drought-Flood Paradox

La Guajira experiences both extreme drought (El Nino) and catastrophic flooding (La Nina). Desiccated, compacted soils during drought periods reduce infiltration capacity, paradoxically increasing flash-flood risk during the transition to wet conditions. This dual-hazard dynamic is a unique contribution of this study.

### Wayuu Vulnerability

The Wayuu indigenous community (~45% of La Guajira's population) faces disproportionate exposure to climate extremes. Population exposure analysis specifically considers indigenous settlement patterns and access limitations documented by Contreras et al. (2020).

## Citation

```bibtex
@article{EspinalMaya2026guajira,
  author  = {Espinal Maya, Cristian and Jim\'enez Londo\~no, Santiago},
  title   = {Municipality-Scale Flood Risk Mapping in {La Guajira}, {Colombia},
             Using {Sentinel-1} {SAR} and Ensemble Machine Learning (2015--2025)},
  year    = {2026},
  note    = {Replicated from Antioquia framework}
}
```

## Related Work

- **Antioquia study**: [github.com/Cespial/antioquia-flood-risk](https://github.com/Cespial/antioquia-flood-risk)
- **Replication Guide**: See `REPLICATION_GUIDE.md` in the Antioquia repository

## License

Source code: [MIT License](LICENSE). Manuscript and figures: CC BY 4.0.
