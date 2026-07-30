import csv
import math
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

BERLIN_ULAND = "11"
# Calibrated from real test points: Grunewald (0) to Potsdamer Platz (~22
# weighted risk points/150m/5yrs once combined — recheck after combining).
RISK_LOW = 0
RISK_HIGH = 150   # placeholder ceiling for 5 combined years; adjust after seeing real range

def _to_float(value):
    return float(value.replace(",", "."))

def load_berlin_accidents(csv_paths):
    accidents = []
    for path in csv_paths:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                if row["ULAND"] != BERLIN_ULAND:
                    continue
                lat = _to_float(row["YGCSWGS84"])
                lng = _to_float(row["XGCSWGS84"])
                severity = int(row["UKATEGORIE"])
                accidents.append((lat, lng, severity))
    return accidents

def haversine_m(lat1, lng1, lat2, lng2):
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * r * math.asin(math.sqrt(a))

def normalize_score(value, lo, hi):
    pct = (value - lo) / (hi - lo)
    pct = max(0.0, min(1.0, pct))
    return round((1 - pct) * 100)  # invert: more/severer accidents = lower score

def accident_risk(lat, lng, accidents, radius_m=150):
    weight = {1: 3, 2: 2, 3: 1}
    nearby = [a for a in accidents if haversine_m(lat, lng, a[0], a[1]) <= radius_m]
    risk_points = sum(weight[a[2]] for a in nearby)
    score = normalize_score(risk_points, RISK_LOW, RISK_HIGH)
    return {
        "accident_count": len(nearby),
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
    print(f"Loaded {len(accidents)} Berlin accidents across {len(csv_paths)} years")

    print("Alexanderplatz:", accident_risk(52.5219, 13.4132, accidents))
    print("Potsdamer Platz:", accident_risk(52.5096, 13.3759, accidents))
    print("Grunewald forest interior:", accident_risk(52.4740, 13.2170, accidents))
    print("Hackescher Markt:", accident_risk(52.5225, 13.4015, accidents))