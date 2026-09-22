import numpy as np

def natural_cubic_spline(x_points, y_points, num_eval=150):
    """
    Pure NumPy Implementation of Natural Cubic Spline Interpolation.
    Solves tridiagonal matrix equation without scipy/GIS overhead.
    """
    x = np.array(x_points, dtype=float)
    y = np.array(y_points, dtype=float)
    n = len(x)
    
    h = np.diff(x)
    alpha = np.zeros(n)
    for i in range(1, n - 1):
        alpha[i] = (3.0 / h[i]) * (y[i+1] - y[i]) - (3.0 / h[i-1]) * (y[i] - y[i-1])
        
    l = np.ones(n)
    mu = np.zeros(n)
    z = np.zeros(n)
    
    for i in range(1, n - 1):
        l[i] = 2.0 * (x[i+1] - x[i-1]) - h[i-1] * mu[i-1]
        mu[i] = h[i] / l[i]
        z[i] = (alpha[i] - h[i-1] * z[i-1]) / l[i]
        
    b = np.zeros(n - 1)
    c = np.zeros(n)
    d = np.zeros(n - 1)
    
    for j in range(n - 2, -1, -1):
        c[j] = z[j] - mu[j] * c[j+1]
        b[j] = (y[j+1] - y[j]) / h[j] - h[j] * (c[j+1] + 2.0 * c[j]) / 3.0
        d[j] = (c[j+1] - c[j]) / (3.0 * h[j])
        
    x_eval = np.linspace(x[0], x[-1], num_eval)
    y_eval = np.zeros_like(x_eval)
    
    for k, xv in enumerate(x_eval):
        # find segment
        idx = np.searchsorted(x, xv) - 1
        idx = np.clip(idx, 0, n - 2)
        dx = xv - x[idx]
        y_eval[k] = y[idx] + b[idx] * dx + c[idx] * (dx ** 2) + d[idx] * (dx ** 3)
        
    return x_eval, y_eval

def generate_forecast_cone(time_steps, lats, lons):
    """
    Computes smoothed spline trajectory and dynamically widening Cone of Uncertainty.
    Cone radius scales with forecast lead time: R(t) = R0 + alpha * t (NOAA baseline).
    """
    # Spline smoothing over time
    t_smooth, lat_smooth = natural_cubic_spline(time_steps, lats, num_eval=200)
    _, lon_smooth = natural_cubic_spline(time_steps, lons, num_eval=200)
    
    # Uncertainty expansion: 0h = 15km, 12h = 45km, 24h = 80km, 36h = 125km, 48h = 175km
    cone_radii_km = 15.0 + 3.33 * t_smooth  # Linear expanding error envelope
    
    left_boundary_lon = []
    left_boundary_lat = []
    right_boundary_lon = []
    right_boundary_lat = []
    
    for i in range(len(t_smooth)):
        # Direction vector along track
        if i < len(t_smooth) - 1:
            dlon = lon_smooth[i+1] - lon_smooth[i]
            dlat = lat_smooth[i+1] - lat_smooth[i]
        else:
            dlon = lon_smooth[i] - lon_smooth[i-1]
            dlat = lat_smooth[i] - lat_smooth[i-1]
            
        track_angle = np.arctan2(dlat, dlon)
        perp_angle_left = track_angle + np.pi / 2.0
        perp_angle_right = track_angle - np.pi / 2.0
        
        # Degree displacement approximation
        deg_dist = cone_radii_km[i] / 111.0
        
        left_boundary_lon.append(lon_smooth[i] + deg_dist * np.cos(perp_angle_left))
        left_boundary_lat.append(lat_smooth[i] + deg_dist * np.sin(perp_angle_left))
        
        right_boundary_lon.append(lon_smooth[i] + deg_dist * np.cos(perp_angle_right))
        right_boundary_lat.append(lat_smooth[i] + deg_dist * np.sin(perp_angle_right))
        
    # Create complete polygon envelope
    cone_poly_lon = left_boundary_lon + right_boundary_lon[::-1]
    cone_poly_lat = left_boundary_lat + right_boundary_lat[::-1]
    
    return lon_smooth, lat_smooth, cone_poly_lon, cone_poly_lat
