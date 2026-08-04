import csv
import math
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent / "data"

BERLIN_ULAND = "11"
# Calibrated from real test points: Grunewald (0) to Potsdamer Platz (~22
# weighted risk points/150m/5yrs once combined — recheck after combining).
RISK_LOW = 0
RISK_HIGH = 150   # placeholder ceiling for 5 combined years; adjust after seeing real range

# Indexed by severity (UKATEGORIE 1-3); index 0 is unused padding so
# _WEIGHT_BY_SEVERITY[severity] works directly as a numpy fancy-index.
_WEIGHT_BY_SEVERITY = np.array([0, 3, 2, 1])

def _to_float(value):
    return float(value.replace(",", "."))

def load_berlin_accidents(csv_paths):
    """Load Berlin accidents into numpy arrays for fast vectorized lookups.

    Perf note: this used to return a plain list of (lat, lng, severity)
    tuples, and accident_risk() did a pure-Python loop computing a haversine
    distance to every one of ~61.7k loaded accidents, for every route sample
    point. Measured on real data: ~2.0s for a realistic 2-route/~30-sample
    request (part of the ~0.89s+ MCP latency seen in the get_safe_routes
    latency investigation, combined with the equally brute-force lighting
    lookup — see lighting_lookup.py). Loading into numpy arrays here lets
    accident_risk() compute the distance to every accident in one vectorized
    array op instead of a Python-level loop: same workload measured at
    ~0.1s combined with lighting after this change — see the benchmark this
    was based on for details.
    """
    lats, lngs, severities = [], [], []
    for path in csv_paths:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                if row["ULAND"] != BERLIN_ULAND:
                    continue
                lats.append(_to_float(row["YGCSWGS84"]))
                lngs.append(_to_float(row["XGCSWGS84"]))
                severities.append(int(row["UKATEGORIE"]))
    return {
        "lats": np.array(lats, dtype=np.float64),
        "lngs": np.array(lngs, dtype=np.float64),
        "severities": np.array(severities, dtype=np.int64),
    }

def haversine_m(lat1, lng1, lat2, lng2):
    """Scalar point-to-point distance (meters). Still used by
    mcp_server._sample_polyline for route-polyline sampling — NOT for the
    accident lookups below, which use the vectorized version instead."""
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * r * math.asin(math.sqrt(a))

def _haversine_m_vec(lat1, lng1, lats2, lngs2):
    """Vectorized distance (meters) from one point to a numpy array of points."""
    r = 6_371_000.0
    p1 = np.radians(lat1)
    p2 = np.radians(lats2)
    dphi = np.radians(lats2 - lat1)
    dlmb = np.radians(lngs2 - lng1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))

def normalize_score(value, lo, hi):
    pct = (value - lo) / (hi - lo)
    pct = max(0.0, min(1.0, pct))
    return round((1 - pct) * 100)  # invert: more/severer accidents = lower score

def accident_risk(lat, lng, accidents, radius_m=150):
    """accidents: the dict returned by load_berlin_accidents (lats/lngs/severities
    numpy arrays) — NOT the old list-of-tuples shape."""
    dists = _haversine_m_vec(lat, lng, accidents["lats"], accidents["lngs"])
    mask = dists <= radius_m
    nearby_severities = accidents["severities"][mask]
    risk_points = int(_WEIGHT_BY_SEVERITY[nearby_severities].sum())
    score = normalize_score(risk_points, RISK_LOW, RISK_HIGH)
    return {
        "accident_count": int(mask.sum()),
        "weighted_risk_points": risk_points,
        "accident_safety_score": score,
        "radius_m": radius_m,
    }

if __name__ == "__main__":

    csv_paths = [
        DATA_DIR /  "Unfallorte_2021_LinRef.txt",
        DATA_DIR / "Unfallorte2022_LinRef.csv",
        DATA_DIR / "Unfallorte2023_LinRef.csv",
        DATA_DIR /  "Unfallorte2024_LinRef.csv",
        DATA_DIR / "Unfallorte_2025_LR_BasisDLM.csv",
    ]
    print("Files loaded:", csv_paths)
    accidents = load_berlin_accidents(csv_paths)
    print(f"Loaded {len(accidents['lats'])} Berlin accidents across {len(csv_paths)} years")

    print("Alexanderplatz:", accident_risk(52.5219, 13.4132, accidents))
    print("Potsdamer Platz:", accident_risk(52.5096, 13.3759, accidents))
    print("Grunewald forest interior:", accident_risk(52.4740, 13.2170, accidents))
    print("Hackescher Markt:", accident_risk(52.5225, 13.4015, accidents))