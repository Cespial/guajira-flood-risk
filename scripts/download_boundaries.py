#!/usr/bin/env python3
"""
download_boundaries.py
======================
Downloads and processes geographic boundary data for the La Guajira Flood Risk
Research Project.

This script downloads from authoritative public sources:
  - Administrative boundaries (department + 15 municipalities)
  - 3 official subregions of La Guajira
  - River basins / cuencas (HydroBASINS levels 5 and 7)
  - Natural Earth department-level context
  - Notes on additional data sources requiring manual access

Sources used:
  - GADM 4.1   : https://gadm.org
  - geoBoundaries: https://www.geoboundaries.org
  - Natural Earth: https://www.naturalearthdata.com
  - HydroSHEDS  : https://www.hydrosheds.org
  - Geofabrik OSM: https://download.geofabrik.de

Usage:
  python3 download_boundaries.py

Requirements:
  pip install requests geopandas shapely

Author: Flood Risk Research Project
Date: 2026-02-26
"""

import os
import sys
import json
import zipfile
import shutil
import requests
from pathlib import Path
from shapely.ops import unary_union

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
BOUNDARIES_DIR = BASE_DIR / "data" / "boundaries"
BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)

# Request timeout in seconds
TIMEOUT = 300

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def download_file(url: str, dest: Path, description: str = "") -> bool:
    """Download a file from URL to dest. Returns True on success."""
    label = description or dest.name
    print(f"  -> Downloading: {label}")
    print(f"     URL: {url}")
    try:
        resp = requests.get(url, stream=True, timeout=TIMEOUT)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                fh.write(chunk)
                downloaded += len(chunk)
        size_mb = downloaded / 1_048_576
        print(f"     OK  ({size_mb:.1f} MB saved to {dest.name})")
        return True
    except requests.exceptions.RequestException as exc:
        print(f"     FAILED: {exc}")
        if dest.exists():
            dest.unlink()
        return False


def unzip_to_dir(zip_path: Path, extract_dir: Path) -> None:
    """Unzip archive to extract_dir, creating it if needed."""
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
    print(f"     Extracted to {extract_dir.name}/")


def import_geopandas():
    """Import geopandas with a helpful error message if missing."""
    try:
        import geopandas as gpd
        return gpd
    except ImportError:
        print("ERROR: geopandas is required. Install with: pip install geopandas")
        sys.exit(1)


def save_geojson(gdf, path: Path, description: str = "") -> None:
    """Save a GeoDataFrame to GeoJSON."""
    gdf.to_file(path, driver="GeoJSON")
    size_kb = path.stat().st_size / 1024
    label = description or path.name
    print(f"     Saved {label} ({size_kb:.0f} KB, {len(gdf)} features)")

# ---------------------------------------------------------------------------
# Section 1 – Administrative Boundaries
# ---------------------------------------------------------------------------

def download_gadm_boundaries() -> dict:
    """
    Download GADM 4.1 boundaries for Colombia (levels 0, 1, 2).
    Returns dict with paths to downloaded files.
    """
    print("\n[1] GADM 4.1 – Colombia Administrative Boundaries")
    print("    Source: https://geodata.ucdavis.edu/gadm/gadm4.1/")

    base_url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json"
    files = {
        "level0": ("gadm41_COL_0.json", "GADM41_COL_level0_national.json", False),
        "level1": ("gadm41_COL_1.json.zip", "GADM41_COL_level1_departments.json.zip", True),
        "level2": ("gadm41_COL_2.json.zip", "GADM41_COL_level2_municipalities.json.zip", True),
    }

    paths = {}
    for level, (remote_name, local_name, is_zip) in files.items():
        dest = BOUNDARIES_DIR / local_name
        if dest.exists():
            print(f"  -> Already exists: {local_name}")
            paths[level] = dest
            continue
        success = download_file(f"{base_url}/{remote_name}", dest, local_name)
        if success:
            if is_zip:
                unzip_to_dir(dest, BOUNDARIES_DIR)
            paths[level] = dest

    return paths


def extract_guajira_gadm() -> None:
    """
    Extract La Guajira-specific GeoJSON files from GADM Colombia data:
      - Department boundary (level 1)
      - All 15 municipalities (level 2)
    """
    gpd = import_geopandas()
    print("\n[2] Extracting La Guajira boundaries from GADM data")

    # -- La Guajira department boundary --
    l1_path = BOUNDARIES_DIR / "gadm41_COL_1.json"
    dept_out = BOUNDARIES_DIR / "guajira_department_boundary_GADM41.geojson"
    if not dept_out.exists() and l1_path.exists():
        with open(l1_path) as fh:
            data = json.load(fh)
        guajira_feat = [f for f in data["features"]
                          if f["properties"].get("NAME_1") == "La Guajira"]
        if guajira_feat:
            with open(dept_out, "w") as fh:
                json.dump({"type": "FeatureCollection", "features": guajira_feat}, fh)
            print(f"  -> Saved {dept_out.name} (1 feature)")
        else:
            print("  WARNING: La Guajira not found in GADM L1 data")

    # -- La Guajira 15 municipalities --
    l2_path = BOUNDARIES_DIR / "gadm41_COL_2.json"
    muns_out = BOUNDARIES_DIR / "guajira_municipalities_15_GADM41.geojson"
    if not muns_out.exists() and l2_path.exists():
        with open(l2_path) as fh:
            data = json.load(fh)
        ant_muns = [f for f in data["features"]
                    if f["properties"].get("NAME_1") == "La Guajira"]
        print(f"  -> Found {len(ant_muns)} La Guajira municipalities in GADM L2")
        with open(muns_out, "w") as fh:
            json.dump({"type": "FeatureCollection", "features": ant_muns}, fh)
        print(f"  -> Saved {muns_out.name}")
    elif muns_out.exists():
        print(f"  -> Already exists: {muns_out.name}")


def download_geoboundaries() -> None:
    """
    Download geoBoundaries Colombia ADM1 and ADM2 from GitHub.
    These are open-source boundaries (CC-BY-SA).
    """
    print("\n[3] geoBoundaries – Colombia ADM1 & ADM2")
    print("    Source: https://www.geoboundaries.org / github.com/wmgeolab/geoBoundaries")

    base = "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/COL"
    downloads = [
        (f"{base}/ADM1/geoBoundaries-COL-ADM1.geojson",
         "geoBoundaries_COL_ADM1_departments.geojson",
         "geoBoundaries Colombia Departments (ADM1)"),
        (f"{base}/ADM2/geoBoundaries-COL-ADM2_simplified.geojson",
         "geoBoundaries_COL_ADM2_simplified.geojson",
         "geoBoundaries Colombia Municipalities simplified (ADM2)"),
    ]

    gpd = import_geopandas()
    for url, name, desc in downloads:
        dest = BOUNDARIES_DIR / name
        if not dest.exists():
            download_file(url, dest, desc)

    # Extract La Guajira from geoBoundaries ADM1
    adm1_path = BOUNDARIES_DIR / "geoBoundaries_COL_ADM1_departments.geojson"
    adm1_ant_out = BOUNDARIES_DIR / "guajira_department_boundary_geoBoundaries.geojson"
    if adm1_path.exists() and not adm1_ant_out.exists():
        with open(adm1_path) as fh:
            data = json.load(fh)
        feat = [f for f in data["features"]
                if f["properties"].get("shapeName") == "La Guajira"]
        if feat:
            with open(adm1_ant_out, "w") as fh:
                json.dump({"type": "FeatureCollection", "features": feat}, fh)
            print(f"  -> Extracted La Guajira from geoBoundaries ADM1")

    # Spatially extract La Guajira municipalities from ADM2
    adm2_path = BOUNDARIES_DIR / "geoBoundaries_COL_ADM2_simplified.geojson"
    adm2_ant_out = BOUNDARIES_DIR / "guajira_municipalities_geoBoundaries_simplified.geojson"
    ant_boundary_path = BOUNDARIES_DIR / "guajira_department_boundary_GADM41.geojson"

    if (adm2_path.exists() and ant_boundary_path.exists()
            and not adm2_ant_out.exists()):
        print("  -> Spatially extracting La Guajira municipalities from geoBoundaries ADM2...")
        gdf = gpd.read_file(adm2_path)
        guajira = gpd.read_file(ant_boundary_path)
        gdf_centroids = gdf.copy()
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gdf_centroids.geometry = gdf.geometry.centroid
        joined = gpd.sjoin(gdf_centroids, guajira[["geometry"]],
                           how="inner", predicate="within")
        result = gdf[gdf.index.isin(joined.index)]
        save_geojson(result, adm2_ant_out, "La Guajira municipalities (geoBoundaries simplified)")


def download_natural_earth() -> None:
    """
    Download Natural Earth 1:10m admin-1 shapefile and extract
    La Guajira + all Colombia departments.
    """
    print("\n[4] Natural Earth – Colombia Admin-1 Boundaries (1:10m)")
    print("    Source: https://www.naturalearthdata.com")

    url = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_1_states_provinces.zip"
    zip_dest = BOUNDARIES_DIR / "natural_earth_admin1_10m.zip"
    extract_dir = BOUNDARIES_DIR / "natural_earth_admin1_tmp"
    shp_path = extract_dir / "ne_10m_admin_1_states_provinces.shp"

    col_out = BOUNDARIES_DIR / "colombia_all_departments_naturalearth.geojson"
    ant_out = BOUNDARIES_DIR / "guajira_department_naturalearth.geojson"

    if not shp_path.exists():
        if not zip_dest.exists():
            download_file(url, zip_dest, "Natural Earth Admin-1 10m")
        if zip_dest.exists():
            unzip_to_dir(zip_dest, extract_dir)

    if shp_path.exists():
        gpd = import_geopandas()
        ne = gpd.read_file(shp_path)
        colombia = ne[ne["admin"] == "Colombia"]
        if not col_out.exists():
            save_geojson(colombia, col_out, "Colombia departments (Natural Earth)")
        guajira = colombia[colombia["name"] == "La Guajira"]
        if not ant_out.exists():
            save_geojson(guajira, ant_out, "La Guajira boundary (Natural Earth)")


# ---------------------------------------------------------------------------
# Section 2 – La Guajira Subregions
# ---------------------------------------------------------------------------

def create_guajira_subregions() -> None:
    """
    Build the 3 official subregions of La Guajira by dissolving GADM
    municipality polygons. Subregion classification follows Gobernacion
    de La Guajira / DANE official groupings.
    """
    print("\n[5] Creating La Guajira 3 Subregion Boundaries")

    out_path = BOUNDARIES_DIR / "guajira_3_subregions.geojson"
    if out_path.exists():
        print(f"  -> Already exists: {out_path.name}")
        return

    muns_path = BOUNDARIES_DIR / "guajira_municipalities_15_GADM41.geojson"
    if not muns_path.exists():
        print("  WARNING: GADM municipalities file not found. Run extract_guajira_gadm() first.")
        return

    gpd = import_geopandas()

    # Mapping: subregion name -> list of GADM NAME_2 values
    SUBREGIONS = {
        'Alta Guajira': ['Uribia', 'Manaure'],
        'Media Guajira': ['Riohacha', 'Maicao', 'Dibulla'],
        'Baja Guajira': [
            'Albania', 'Barrancas', 'Distraccion', 'El Molino',
            'Fonseca', 'Hatonuevo', 'La Jagua del Pilar',
            'San Juan del Cesar', 'Urumita', 'Villanueva'
        ],
    }

    muns = gpd.read_file(muns_path)
    mun_index = {row["NAME_2"]: idx for idx, row in muns.iterrows()}

    features = []
    for subregion_name, mun_list in SUBREGIONS.items():
        geoms = []
        matched, missing = [], []
        for mun in mun_list:
            if mun in mun_index:
                geoms.append(muns.loc[mun_index[mun], "geometry"])
                matched.append(mun)
            else:
                missing.append(mun)

        if missing:
            print(f"  WARNING [{subregion_name}] unmatched: {missing}")

        if geoms:
            dissolved = unary_union(geoms)
            features.append({
                "type": "Feature",
                "properties": {
                    "subregion": subregion_name,
                    "n_municipalities_expected": len(mun_list),
                    "n_municipalities_matched": len(matched),
                    "municipalities": ", ".join(matched),
                },
                "geometry": dissolved.__geo_interface__,
            })

    fc = {"type": "FeatureCollection", "features": features}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(fc, fh, ensure_ascii=False)

    total = sum(f["properties"]["n_municipalities_matched"] for f in features)
    print(f"  -> Saved {out_path.name} (3 subregions, {total} municipalities matched)")


# ---------------------------------------------------------------------------
# Section 3 – River Basins (HydroSHEDS / HydroBASINS)
# ---------------------------------------------------------------------------

def download_hydrobasins() -> None:
    """
    Download HydroBASINS South America at levels 5 and 7, then clip to
    La Guajira department boundary.

    HydroBASINS is published by WWF / HydroSHEDS project.
    License: free for academic and non-commercial use.
    Source: https://www.hydrosheds.org/products/hydrobasins
    """
    print("\n[6] HydroBASINS – River Basins for La Guajira")
    print("    Source: https://data.hydrosheds.org")

    ant_path = BOUNDARIES_DIR / "guajira_department_boundary_GADM41.geojson"
    if not ant_path.exists():
        print("  WARNING: La Guajira boundary not found. Run earlier steps first.")
        return

    gpd = import_geopandas()
    guajira = gpd.read_file(ant_path)

    for level in [5, 7]:
        zip_name = f"HydroBASINS_SA_level{level:02d}_basins.zip"
        zip_dest = BOUNDARIES_DIR / zip_name
        extract_dir = BOUNDARIES_DIR / f"hydrobasins_sa_l{level}_tmp"
        shp_name = f"hybas_sa_lev{level:02d}_v1c.shp"
        shp_path = extract_dir / shp_name
        out_name = f"guajira_river_basins_HydroSHEDS_L{level}.geojson"
        out_path = BOUNDARIES_DIR / out_name

        url = f"https://data.hydrosheds.org/file/hydrobasins/standard/hybas_sa_lev{level:02d}_v1c.zip"

        if out_path.exists():
            print(f"  -> Already exists: {out_name}")
            continue

        if not shp_path.exists():
            if not zip_dest.exists():
                download_file(url, zip_dest, f"HydroBASINS SA Level {level}")
            if zip_dest.exists():
                unzip_to_dir(zip_dest, extract_dir)

        if shp_path.exists():
            print(f"  -> Clipping HydroBASINS L{level} to La Guajira...")
            hb = gpd.read_file(shp_path)
            clipped = gpd.sjoin(hb, guajira[["geometry"]], how="inner",
                                predicate="intersects")
            clipped = clipped.drop(columns=["index_right"], errors="ignore")
            save_geojson(clipped, out_path,
                         f"La Guajira river basins HydroSHEDS L{level}")


# ---------------------------------------------------------------------------
# Section 4 – Road & River Networks (OSM via Geofabrik)
# ---------------------------------------------------------------------------

def download_osm_data() -> None:
    """
    Downloads Colombia OSM data from Geofabrik (640 MB shapefile or 296 MB PBF).
    This is large; the script downloads the Colombia PBF by default.
    After downloading, use osmium or ogr2ogr to clip to La Guajira.

    For a smaller targeted download, use the BBBike custom extract service:
      https://extract.bbbike.org/
    Define the La Guajira bounding box: W=-77.15, S=5.41, E=-73.87, N=8.89

    Geofabrik Colombia shapefiles include:
      - gis_osm_roads_free_1.shp  (road network)
      - gis_osm_waterways_free_1.shp  (rivers, streams)
      - gis_osm_water_a_free_1.shp  (water bodies)
      - gis_osm_natural_free_1.shp  (natural features)
    """
    print("\n[7] OSM Road & River Network (Geofabrik)")
    print("    Source: https://download.geofabrik.de/south-america/colombia.html")
    print("    NOTE: Colombia shapefile is ~640 MB. Skipping automatic download.")
    print("    To download manually:")
    print("      curl -L -o colombia-latest-free.shp.zip \\")
    print("        https://download.geofabrik.de/south-america/colombia-latest-free.shp.zip")
    print("")
    print("    For La Guajira-only OSM extract (recommended):")
    print("      Use BBBike custom extract: https://extract.bbbike.org/")
    print("      Bounding box: W=-77.15, S=5.41, E=-73.87, N=8.89")
    print("      Or use Overpass API to query by boundary:")
    print("      https://overpass-turbo.eu/")


# ---------------------------------------------------------------------------
# Section 5 – Flood Hazard Data (IDEAM / UNGRD)
# ---------------------------------------------------------------------------

def download_flood_hazard_info() -> None:
    """
    Prints information about flood hazard data sources for La Guajira.
    Direct programmatic download is not possible for most of these (login/WMS required).
    """
    print("\n[8] Flood Hazard Data Sources (IDEAM / UNGRD)")
    print("=" * 60)

    sources = [
        {
            "name": "IDEAM – Zonas Potencialmente Inundables (ZPI)",
            "url": "http://www.siac.gov.co/en/zonas-potencialmente-inundables-zpi",
            "format": "Shapefile / WMS",
            "access": "Manual download via SIAC portal or WMS viewer",
            "notes": "Flood-susceptible zones at 1:100,000 scale for 22 departments",
        },
        {
            "name": "IDEAM – Open Data / Datos Abiertos",
            "url": "https://visualizador.ideam.gov.co/CatalogoObjetos/geo-open-data",
            "format": "Shapefile, GeoJSON, WFS/WMS",
            "access": "Browse catalog and download via web portal",
            "notes": "Search for 'inundacion', 'susceptible', 'areas afectadas'",
        },
        {
            "name": "IDEAM – Hidrografia Colombiana (ArcGIS Hub)",
            "url": "https://hub.arcgis.com/datasets/89f6818e093f4b0faa99b456ad98018d",
            "format": "Shapefile / GeoJSON",
            "access": "Requires ArcGIS Online account (login required)",
            "notes": "River network for all of Colombia",
        },
        {
            "name": "UNGRD – Risk Management Data",
            "url": "https://repositorio.gestiondelriesgo.gov.co",
            "format": "PDF reports + some shapefiles",
            "access": "Manual search by event/municipality",
            "notes": "Historical flood event records by municipality",
        },
        {
            "name": "Colombia en Mapas – IGAC / DANE",
            "url": "https://www.colombiaenmapas.gov.co/?u=0&t=30&servicio=1465",
            "format": "Shapefile, PDF",
            "access": "Free download, requires web portal navigation",
            "notes": "Basic cartography at 1:500,000 scale (rivers, roads, admin)",
        },
        {
            "name": "Corguajira – Cuencas (ArcGIS REST)",
            "url": "https://geografico.corguajira.gov.co/arcgis/rest/services/Corguajira_Geoconsulta/MapServer/6",
            "format": "ArcGIS REST / GeoJSON",
            "access": "REST API (connection issues observed)",
            "notes": "Watershed delineation (Otto Pfafstetter NSS3 level) for Corguajira jurisdiction",
        },
        {
            "name": "Think Hazard – Colombia Flood Risk",
            "url": "https://www.thinkhazard.org/en/report/57-colombia/FL",
            "format": "Web viewer / PDF",
            "access": "Free, no download available",
            "notes": "Summary of river flood hazard at country/department level",
        },
        {
            "name": "Datos Abiertos Colombia – datos.gov.co",
            "url": "https://www.datos.gov.co",
            "format": "CSV, JSON, Shapefile",
            "access": "Free API at datos.gov.co/resource/<dataset_id>.json",
            "notes": "Search for 'inundaciones', 'eventos', 'emergencias La Guajira'",
        },
        {
            "name": "HDX (ReliefWeb) – Colombia Flood Events",
            "url": "https://data.humdata.org/dataset/cod-ab-col",
            "format": "Shapefile, GeoJSON",
            "access": "Free direct download",
            "notes": "Administrative boundaries used by humanitarian response",
        },
        {
            "name": "Geofabrik OSM – Road & River Network",
            "url": "https://download.geofabrik.de/south-america/colombia.html",
            "format": "Shapefile (.shp.zip), PBF",
            "access": "Free direct download (640 MB shapefile, 296 MB PBF)",
            "notes": "Contains: roads, waterways, water areas, natural features",
        },
    ]

    for i, s in enumerate(sources, 1):
        print(f"\n  [{i}] {s['name']}")
        print(f"      URL    : {s['url']}")
        print(f"      Format : {s['format']}")
        print(f"      Access : {s['access']}")
        print(f"      Notes  : {s['notes']}")


# ---------------------------------------------------------------------------
# Section 6 – Download Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    """Print a summary of all files in the boundaries directory."""
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"Boundaries directory: {BOUNDARIES_DIR}\n")

    files = sorted(BOUNDARIES_DIR.glob("*.geojson")) + \
            sorted(BOUNDARIES_DIR.glob("*.json")) + \
            sorted(BOUNDARIES_DIR.glob("*.zip"))

    total_size = 0
    for f in files:
        size = f.stat().st_size
        total_size += size
        size_str = f"{size / 1_048_576:.1f} MB" if size > 1_048_576 else f"{size / 1024:.0f} KB"
        print(f"  {f.name:<60} {size_str:>10}")

    print(f"\n  Total: {len(files)} files, {total_size / 1_048_576:.1f} MB")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("La Guajira Flood Risk Research – Geographic Boundary Downloader")
    print("=" * 70)
    print(f"Output directory: {BOUNDARIES_DIR}")

    # 1. GADM administrative boundaries
    download_gadm_boundaries()

    # 2. Extract La Guajira from GADM
    extract_guajira_gadm()

    # 3. geoBoundaries
    download_geoboundaries()

    # 4. Natural Earth
    download_natural_earth()

    # 5. Build subregions
    create_guajira_subregions()

    # 6. HydroBASINS river basins
    download_hydrobasins()

    # 7. OSM roads/rivers (info only - large file)
    download_osm_data()

    # 8. Flood hazard sources (info + manual download guide)
    download_flood_hazard_info()

    # Summary
    print_summary()

    print("\nDone.")


if __name__ == "__main__":
    main()
