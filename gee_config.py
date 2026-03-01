"""
Central configuration for the La Guajira Flood Risk Assessment project.
All parameters, constants, and GEE asset paths are defined here.

Replicated from Antioquia framework — adapted for arid/semi-arid department.
Key changes:
  - Department: La Guajira (15 municipalities, ~20,848 km2)
  - 3 subregions: Alta Guajira, Media Guajira, Baja Guajira
  - Unimodal precipitation regime (peak Sep-Nov)
  - Reduced SAMPLES_PER_CLASS (2,500) for lower flood prevalence
  - Adjusted SAR thresholds for arid terrain (sand-water confusion)
  - Coastal/salt-flat masking considerations
"""

import os
import ee
from dotenv import load_dotenv

load_dotenv()

# --- GEE Initialization ---
try:
    ee.Initialize(project=os.getenv('GEE_PROJECT_ID', 'ee-maestria-tesis'))
except Exception:
    ee.Authenticate()
    ee.Initialize(project=os.getenv('GEE_PROJECT_ID', 'ee-maestria-tesis'))

# ============================================================================
# STUDY AREA: Department of La Guajira, Colombia
# ============================================================================

# Administrative boundaries from FAO GAUL Level 1
ADMIN_DATASET = 'FAO/GAUL/2015/level1'
DEPARTMENT_NAME = 'Guajira'  # FAO GAUL uses 'Guajira' (without 'La')
COUNTRY_NAME = 'Colombia'

# Municipal boundaries from FAO GAUL Level 2
MUNICIPAL_DATASET = 'FAO/GAUL/2015/level2'

# HydroSHEDS basin boundaries
HYDROBASINS_L5 = 'WWF/HydroSHEDS/v1/Basins/hybas_sa_lev05_v1c'
HYDROBASINS_L7 = 'WWF/HydroSHEDS/v1/Basins/hybas_sa_lev07_v1c'

# 3 Subregions of La Guajira with their municipalities
# Names MUST match FAO GAUL Level 2 exactly.
# NOTE: GAUL 2015 only has 11 of 15 municipalities for La Guajira.
#   Missing: Albania, Dibulla, Distraccion, La Jagua del Pilar
#   (these were created after GAUL 2015 or are grouped differently)
#   The pipeline uses the department boundary (Level 1) for the study area
#   and processes all pixels within it, regardless of municipal boundaries.
SUBREGIONS = {
    'Alta Guajira': [
        'Uribia', 'Manaure'
    ],
    'Media Guajira': [
        'Riohacha', 'Maicao', 'Dibulla'  # Dibulla not in GAUL L2
    ],
    'Baja Guajira': [
        'Albania', 'Barrancas', 'Distraccion', 'El Molino',  # Albania, Distraccion not in GAUL L2
        'Fonseca', 'Hato Nuevo', 'La Jagua del Pilar',  # La Jagua del Pilar not in GAUL L2
        'San Juan Del Cesar', 'Urumita', 'Villanueva'
    ],
}

# Municipality name mapping: our names -> GAUL Level 2 names
# Only includes municipalities that ARE in GAUL Level 2
GAUL_MUNICIPALITY_NAMES = [
    'Barrancas', 'El Molino', 'Fonseca', 'Hato Nuevo',
    'Maicao', 'Manaure', 'Riohacha', 'San Juan Del Cesar',
    'Uribia', 'Urumita', 'Villanueva'
]

# Municipalities NOT in GAUL Level 2 (will use department-level boundary)
GAUL_MISSING_MUNICIPALITIES = ['Albania', 'Dibulla', 'Distraccion', 'La Jagua del Pilar']

# Department statistics (for quality control validation)
EXPECTED_AREA_KM2 = 20848
EXPECTED_MUNICIPALITY_COUNT = 15
DEPARTMENT_POPULATION_2020 = 964067  # DANE projection

# ============================================================================
# TEMPORAL CONFIGURATION
# ============================================================================

# Full analysis period: 2015-2025 (Sentinel-1 era)
ANALYSIS_START = '2015-01-01'
ANALYSIS_END = '2025-12-31'

# Sentinel-1 availability
S1_START = '2014-10-03'  # Sentinel-1A launch
S1B_FAILURE = '2021-12-23'  # Sentinel-1B failure
S1C_LAUNCH = '2024-04-25'  # Sentinel-1C launch

# Seasonal periods for La Guajira (predominantly UNIMODAL precipitation)
# Peak rainfall: September-November; Dry: December-March
# Minor transitional rains in April-June (weak, unreliable)
SEASONS = {
    'Dry': {'months': [12, 1, 2, 3], 'label': 'Dry season (Verano)'},
    'Transition': {'months': [4, 5, 6], 'label': 'Minor rains / transition'},
    'Veranillo': {'months': [7, 8], 'label': 'Mid-year dry spell (Veranillo)'},
    'Wet': {'months': [9, 10, 11], 'label': 'Main wet season (peak floods)'},
}

# Annual analysis windows
ANNUAL_WINDOWS = {year: {
    'start': f'{year}-01-01',
    'end': f'{year}-12-31',
} for year in range(2015, 2026)}

# ENSO classification for study period (2015-2025)
# Source: NOAA ONI (Oceanic Nino Index)
# La Guajira is extremely sensitive: El Nino = severe drought, La Nina = flooding
ENSO_YEARS = {
    'El Nino': [2015, 2016, 2023, 2024],
    'La Nina': [2020, 2021, 2022],
    'Neutral': [2017, 2018, 2019, 2025],
}

# ============================================================================
# SATELLITE DATA SOURCES
# ============================================================================

# Sentinel-1 SAR GRD (Ground Range Detected)
S1_COLLECTION = 'COPERNICUS/S1_GRD'
S1_PARAMS = {
    'instrumentMode': 'IW',  # Interferometric Wide swath
    'resolution': 10,  # meters
    'polarization': ['VV', 'VH'],  # Dual-pol
    'orbitProperties_pass': 'DESCENDING',  # Morning pass: calmer winds, better water detection
    'resolution_meters': 10,
}

# Water detection thresholds for SAR (VV polarization)
# ADJUSTED FOR ARID/SEMI-ARID TERRAIN:
# - Sand-water backscatter confusion is a key challenge
# - Dry sand and calm water both produce low backscatter in C-band
# - Narrower valid range to reduce false positives from sand
# - Larger min water area to filter noise from arroyos and salt pans
SAR_WATER_THRESHOLDS = {
    'otsu_adaptive': True,  # Use Otsu automatic thresholding
    'vv_default': -16.0,  # dB, slightly lower than Antioquia (-15) to avoid sand confusion
    'vv_range': (-21.0, -13.0),  # Valid range for water detection (narrower)
    'vh_default': -23.0,  # dB, fallback for VH
    'min_water_area_ha': 2.0,  # 2 ha minimum (larger than Antioquia's 1 ha) to filter tidal/arroyo noise
    'speckle_filter_radius': 50,  # meters, focal median radius
}

# Sand Exclusion Layer (SEL) parameters
# Critical for arid La Guajira: exclude persistent low-backscatter sand surfaces
SAND_EXCLUSION = {
    'enabled': True,
    'min_backscatter_threshold': -18.0,  # dB, pixels below this in >80% of dry-season scenes = sand
    'dry_season_months': [12, 1, 2, 3],  # Months to compute sand baseline
    'temporal_persistence': 0.80,  # Fraction of scenes pixel must be low to classify as sand
}

# Coastal/tidal mask parameters
COASTAL_MASK = {
    'enabled': True,
    'salt_flat_regions': ['Manaure', 'Uribia'],  # Municipalities with extensive salt pans
    'buffer_coastline_m': 500,  # Buffer from coastline to mask tidal flats
}

# JRC Global Surface Water v1.4
JRC_GSW = 'JRC/GSW1_4/GlobalSurfaceWater'
JRC_GSW_MONTHLY = 'JRC/GSW1_4/MonthlyHistory'
JRC_GSW_YEARLY = 'JRC/GSW1_4/YearlyHistory'

# JRC GLOFAS Flood Hazard
GLOFAS_FLOOD_HAZARD = 'JRC/CEMS_GLOFAS/FloodHazard/v1'

# SRTM Digital Elevation Model (30m)
SRTM = 'USGS/SRTMGL1_003'

# MERIT Hydro (90m) - pre-computed hydrological layers
MERIT_HYDRO = 'MERIT/Hydro/v1_0_1'

# HAND (Height Above Nearest Drainage) - derived from SRTM
HAND_DATASET = 'users/gaborimbre/HAND_30m_SA'  # South America HAND

# CHIRPS Daily Precipitation (5.5km)
CHIRPS = 'UCSB-CHG/CHIRPS/DAILY'

# ERA5-Land Monthly (11km)
ERA5_LAND = 'ECMWF/ERA5_LAND/MONTHLY_AGGR'

# MODIS LST (1km)
MODIS_LST = 'MODIS/061/MOD11A2'

# WorldPop Population Density (100m)
WORLDPOP = 'WorldPop/GP/100m/pop'

# ESA WorldCover (10m land cover)
WORLDCOVER = 'ESA/WorldCover/v200'

# OpenStreetMap-based roads (via GEE community)
GRIP_ROADS = 'projects/sat-io/open-datasets/GRIP4/Africa-Caribbean'

# ============================================================================
# FLOOD RISK MODEL PARAMETERS
# ============================================================================

# HAND thresholds for flood susceptibility
# La Guajira is relatively flat in lowlands — HAND <10 m appropriate for broader floodplains
HAND_CLASSES = {
    'very_high': {'range': (0, 5), 'label': 'Very High', 'color': '#d73027'},
    'high': {'range': (5, 15), 'label': 'High', 'color': '#fc8d59'},
    'moderate': {'range': (15, 30), 'label': 'Moderate', 'color': '#fee08b'},
    'low': {'range': (30, 60), 'label': 'Low', 'color': '#d9ef8b'},
    'very_low': {'range': (60, 9999), 'label': 'Very Low', 'color': '#1a9850'},
}

# Flood frequency classes (based on JRC occurrence)
# ADJUSTED: Lower thresholds for arid regions with less frequent flooding
FLOOD_FREQUENCY_CLASSES = {
    'permanent': {'range': (75, 100), 'label': 'Permanent water', 'color': '#08306b'},
    'very_frequent': {'range': (50, 75), 'label': 'Very frequent', 'color': '#2171b5'},
    'frequent': {'range': (15, 50), 'label': 'Frequent flooding', 'color': '#6baed6'},
    'occasional': {'range': (5, 15), 'label': 'Occasional flooding', 'color': '#bdd7e7'},
    'rare': {'range': (1, 5), 'label': 'Rare flooding', 'color': '#eff3ff'},
}

# Training label criteria — ADJUSTED FOR ARID REGION
# Per REPLICATION_GUIDE: fewer flood events = lower thresholds
TRAINING_LABELS = {
    'flood_positive': {
        'jrc_occurrence_min': 10,  # >= 10% (lowered from 25% for arid region)
        'hand_max': 5,  # < 5 m
        'condition': 'OR',  # JRC >= 10% OR HAND < 5 m
    },
    'flood_negative': {
        'jrc_occurrence_max': 3,  # < 3% (lowered from 5%)
        'hand_min': 30,  # >= 30 m
        'slope_min': 10,  # > 10 deg
        'condition': 'AND',  # All conditions must be met
    },
}

# ML Model parameters (same as Antioquia — robust across regions)
ML_PARAMS = {
    'random_forest': {
        'n_estimators': 500,
        'max_depth': 15,
        'min_samples_split': 10,
        'min_samples_leaf': 5,
        'random_state': 42,
        'n_jobs': -1,
    },
    'xgboost': {
        'n_estimators': 500,
        'max_depth': 8,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'eval_metric': 'auc',
    },
    'lightgbm': {
        'n_estimators': 500,
        'max_depth': 8,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'metric': 'auc',
        'verbose': -1,
    },
}

# Flood susceptibility features (predictors)
SUSCEPTIBILITY_FEATURES = [
    'elevation',            # SRTM 30m
    'slope',                # Derived from SRTM
    'aspect',               # Derived from SRTM
    'curvature',            # Plan curvature
    'hand',                 # Height Above Nearest Drainage
    'twi',                  # Topographic Wetness Index
    'spi',                  # Stream Power Index
    'dist_rivers',          # Distance to nearest river
    'dist_roads',           # Distance to nearest road
    'drainage_density',     # River density per unit area
    'rainfall_annual',      # Mean annual precipitation (CHIRPS)
    'rainfall_max_monthly', # Max monthly precipitation
    'land_cover',           # ESA WorldCover 2021
    'ndvi_mean',            # Mean annual NDVI
    'soil_moisture',        # ERA5-Land soil moisture
    'pop_density',          # WorldPop 100m
    'flood_frequency_jrc',  # JRC water occurrence
    'sar_water_frequency',  # Sentinel-1 derived water frequency
]

# Samples per class — REDUCED for arid region with fewer flood events
SAMPLES_PER_CLASS = 2500  # Down from 5000 in Antioquia

# Cross-validation parameters
# Spatial CV: 5 folds grouped by subregion
# With only 3 subregions, we split Baja Guajira into 3 geographic groups
CV_PARAMS = {
    'n_splits': 5,  # Stratified spatial K-fold
    'test_size': 0.3,
    'random_state': 42,
}

# Spatial CV fold assignments (5 folds from 3 subregions)
# Baja Guajira (10 municipalities) split into 3 groups for better spatial CV
SPATIAL_CV_FOLDS = {
    0: ['Uribia', 'Manaure'],  # Alta Guajira
    1: ['Riohacha', 'Maicao', 'Dibulla'],  # Media Guajira
    2: ['Albania', 'Barrancas', 'Hatonuevo', 'Fonseca'],  # Baja Guajira - North
    3: ['Distraccion', 'El Molino', 'San Juan del Cesar'],  # Baja Guajira - Central
    4: ['La Jagua del Pilar', 'Urumita', 'Villanueva'],  # Baja Guajira - South
}

# Risk class thresholds (same as Antioquia)
RISK_CLASSES = {
    'Very Low': (0.0, 0.2),
    'Low': (0.2, 0.4),
    'Moderate': (0.4, 0.6),
    'High': (0.6, 0.8),
    'Very High': (0.8, 1.0),
}

# Flood Risk Index weights
FRI_WEIGHTS = {
    'population': 0.4,
    'pct_high_area': 0.3,
    'mean_susceptibility': 0.3,
}

# ============================================================================
# VISUALIZATION PARAMETERS
# ============================================================================

# Color palettes
WATER_PALETTE = ['#ffffff', '#bdd7e7', '#6baed6', '#2171b5', '#08306b']
RISK_PALETTE = ['#1a9850', '#91cf60', '#d9ef8b', '#fee08b',
                '#fc8d59', '#d73027']
SUBREGION_PALETTE = ['#e41a1c', '#377eb8', '#4daf4a']  # 3 subregions

# Map center for La Guajira
# Centered to capture the flood-prone Rancheria corridor
MAP_CENTER = {'lat': 11.35, 'lon': -72.70}
MAP_ZOOM = 9

# Figure DPI for publication
FIGURE_DPI = 600
FIGURE_FORMAT = ['pdf', 'png']

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Export scale (meters)
EXPORT_SCALE = 30

# Google Drive export folder
EXPORT_FOLDER = 'guajira_flood_risk'

# GEE asset path for susceptibility map
SUSCEPTIBILITY_ASSET = 'projects/ee-flood-risk-guajira/assets/guajira_flood_susceptibility_ensemble'

# Project paths
import pathlib
PROJECT_ROOT = pathlib.Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
FIGURES_DIR = OUTPUTS_DIR / 'figures'
TABLES_DIR = OUTPUTS_DIR / 'tables'
OVERLEAF_DIR = PROJECT_ROOT / 'overleaf'
LOGS_DIR = PROJECT_ROOT / 'logs'
