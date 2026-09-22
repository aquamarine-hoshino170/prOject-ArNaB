import numpy as np

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Calculates spherical geodesic distance (km) using Haversine formula."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    
    a = np.sin(dphi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2.0)**2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return R * c

def evaluate_coastal_threat_matrix(center_lat, center_lon, holland_model, surge_model, landmarks):
    """
    Computes site-specific wind exposure, surge impact, and risk classification.
    """
    matrix = []
    
    for name, lat, lon in landmarks:
        dist_km = haversine_distance_km(center_lat, center_lon, lat, lon)
        
        # Local wind profile based on radial distance
        _, v_kts_local = holland_model.gradient_wind_profile(np.array([dist_km]))
        v_local = float(v_kts_local[0])
        
        # Site-specific surge attenuation based on distance from core
        surge_decay = np.exp(-dist_km / 150.0)
        surge_base = surge_model.compute(shelf_length_km=80.0, avg_depth_m=25.0)
        local_surge_m = round(surge_base['total_m'] * surge_decay, 2)
        
        # Risk classification
        if v_local >= 64.0 or local_surge_m >= 2.5:
            threat_level = "CRITICAL"
            color_code = "#d90429"
        elif v_local >= 50.0 or local_surge_m >= 1.5:
            threat_level = "HIGH"
            color_code = "#fb8500"
        elif v_local >= 34.0 or local_surge_m >= 0.8:
            threat_level = "MODERATE"
            color_code = "#ffb703"
        else:
            threat_level = "MINIMAL"
            color_code = "#06d6a0"
            
        matrix.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "dist_km": round(dist_km, 1),
            "wind_kts": round(v_local, 1),
            "surge_m": local_surge_m,
            "threat": threat_level,
            "color": color_code
        })
        
    return matrix

def print_threat_table(matrix):
    print("\n" + "="*70)
    print(" PROJECT ARNAB // AUTOMATED COASTAL THREAT MATRIX")
    print("="*70)
    print(f"{'Landmark':<16} | {'Dist (km)':<10} | {'Wind (kts)':<10} | {'Surge (m)':<10} | {'Threat Level':<10}")
    print("-" * 70)
    for row in matrix:
        print(f"{row['name']:<16} | {row['dist_km']:<10} | {row['wind_kts']:<10} | {row['surge_m']:<10} | {row['threat']}")
    print("="*70 + "\n")
