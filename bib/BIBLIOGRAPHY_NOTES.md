# Bibliographic Research Notes: La Guajira Flood Risk Study

## Research Gap Identified

**No ML-based flood susceptibility mapping has been published for La Guajira.** Only Riohacha has localized flood models (Perez-Montiel 2022, Nardini 2016). This study fills a clear gap.

---

## References by Theme (25 La Guajira-specific + 12 foundational = 37 total)

### 1. Flood Risk & Hydrology in La Guajira (3 refs)

| Ref | Key Finding |
|-----|-------------|
| Perez-Montiel et al. 2022 | MODCEL outperformed IBER for Riohacha flood modeling; low-resolution topographic data limits accuracy |
| Nardini & Gomes Miguez 2016 | Integrated urban flood plan for Riohacha using MODCEL + participatory data |
| Hoyos et al. 2013 | 2010-2011 La Nina: 4M Colombians affected, $7.8B losses, 1.6M ha additionally flooded in Caribbean |

### 2. Remote Sensing in Arid/Semi-Arid Regions (3 refs)

| Ref | Key Finding |
|-----|-------------|
| Garg et al. 2024 | **Critical**: VV coherence + amplitude fusion improves arid flood detection by ~50%. Global products EXCLUDE arid areas |
| Martinis et al. 2018 | **Sand Exclusion Layer (SEL)**: multi-temporal SAR statistics eliminate sand-water confusion. Tested in Somalia |
| Panahi et al. 2022 | Hybrid SVM + metaheuristic optimization for arid-zone flood monitoring using SAR in Iran |

### 3. Climate Variability (4 refs)

| Ref | Key Finding |
|-----|-------------|
| Gallego-Revilla et al. 2022 | CHIRPS-based extreme precipitation analysis across Colombia; El Nino = drier Caribbean |
| Mera-Gomez et al. 2021 | **La Guajira-specific**: SPI-6 most accurate for drought ID; central/southern areas most affected |
| Drought Projections 2025 | CNRM-CM6-1-HR model best matches CHIRPS for northern South America |
| Magdalena Precip 2024 | Neighboring department: decreasing annual trends but increasing wet-season monthly extremes |

### 4. ML for Flood Susceptibility in Arid/Semi-Arid (4 refs)

| Ref | Key Finding |
|-----|-------------|
| Abedi et al. 2022 | CART/RF/BRT/XGBoost comparison for flash-flood susceptibility |
| Bammou et al. 2024 | **Semi-arid Morocco**: XGBoost and RF most accurate in ensemble comparison |
| Ren et al. 2024 | RF (Acc=0.81, Kappa=0.89) slightly outperformed XGBoost; sampling strategy matters |
| Morocco SAR+ML 2024 | **SAR + ML in semi-arid**: RF (AUC=0.807) > XGBoost (0.727) in Morocco |

### 5. Colombian Caribbean Flood Risk (2 refs)

| Ref | Key Finding |
|-----|-------------|
| Sedano-Cruz et al. 2017 | 2010-2011 La Nina: 2.35M people affected; Caribbean lowlands = seasonal flooding hotspot |
| Alabbad et al. 2023 | Comprehensive review: flood risk poorly understood in arid/semi-arid areas |

### 6. Indigenous Communities & Disaster Risk (4 refs)

| Ref | Key Finding |
|-----|-------------|
| Contreras et al. 2020 | **La Guajira**: Child mortality 23.4/1000 during 2012-2016 drought; 90.4% in poorest households |
| Contreras et al. 2019 (spatial) | Geospatial patterns of child mortality among Wayuu population |
| Contreras Mojica 2019 | Wayuu adaptation strategies; water management policy failures |
| Fernandez Lopera et al. 2024 | La Guajira = highest climate vulnerability index in Colombia |

### 7. Water Resources (3 refs)

| Ref | Key Finding |
|-----|-------------|
| Gomez Arevalo 2020 | Groundwater model for Carraipia Basin (1,600 km2); saltwater intrusion risk |
| Wayuu Water Governance 2025 | Disconnect between governance programs and Wayuu water conceptualizations |
| Coastal Aquifer 2024 | Coastal aquifer hydrogeochemistry framework for Caribbean Colombia |

### 8. Cross-Cutting (2 refs)

| Ref | Key Finding |
|-----|-------------|
| Drought-Flood Monitoring 2024 | Dual-hazard framework combining remote sensing + SPI for arid regions (Syria) |
| SAR Flood Review 2024 | Comprehensive review of SAR techniques; C-band penetrates dry sand but not wet sand |

---

## Key Methodological Implications

1. **Sand Exclusion Layer is mandatory** (Martinis 2018, Garg 2024)
2. **Use both VV coherence AND amplitude** for flood detection (Garg 2024)
3. **RF may outperform XGBoost** in semi-arid contexts (Morocco SAR+ML 2024)
4. **SPI-6 is the most appropriate drought index** for La Guajira (Mera-Gomez 2021)
5. **Vulnerability analysis must include Wayuu-specific indicators** (Contreras 2020, Fernandez Lopera 2024)
6. **ENSO is the dominant inter-annual driver** — must stratify results by ENSO phase

---

## Comparison with Antioquia Study

| Aspect | Antioquia | La Guajira |
|--------|-----------|------------|
| Area | 63,612 km2 | 20,848 km2 |
| Municipalities | 125 | 15 |
| Population | 6.8 million | ~1.0 million |
| Climate | Humid tropical, bimodal | Arid/semi-arid, unimodal |
| Main flood type | River overflow, sustained | Flash floods, torrential |
| ENSO effect | Moderate amplification | Extreme amplification |
| SAR challenges | Forest double-bounce | Sand-water confusion |
| Indigenous factor | Moderate | Very high (Wayuu ~45%) |
| Drought risk | Low | Extreme |
| Key rivers | Cauca, Magdalena, Nechi | Rancheria, Cesar, Palomino |
