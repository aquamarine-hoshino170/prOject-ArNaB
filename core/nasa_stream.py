import urllib.request
import io
from PIL import Image
import numpy as np

def fetch_nasa_gibs_tile(date_str: str, bbox: list, width: int = 800, height: int = 800):
    """
    Direct REST integration with NASA GIBS (Global Imagery Browse Services) WMS API.
    BBOX format: [min_lon, min_lat, max_lon, max_lat] (EPSG:4326)
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # NASA GIBS WMS Endpoint (Suomi NPP / VIIRS Corrected Reflectance)
    base_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
    params = (
        f"?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0"
        f"&LAYERS=VIIRS_SNPP_CorrectedReflectance_TrueColor"
        f"&STYLES="
        f"&FORMAT=image/jpeg"
        f"&TIME={date_str}"
        f"&CRS=EPSG:4326"
        f"&BBOX={min_lat},{min_lon},{max_lat},{max_lon}"
        f"&WIDTH={width}&HEIGHT={height}"
    )
    
    full_url = base_url + params
    print(f"[FETCHING] Querying NASA GIBS Gateway for {date_str}...")
    
    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'NASA-SpaceApps-ProjectArnab/1.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            img_data = response.read()
            img = Image.open(io.BytesIO(img_data))
            print("[SUCCESS] NASA Satellite raster stream acquired successfully.")
            return img
    except Exception as e:
        print(f"[FALLBACK] NASA API stream connection timed out or offline: {e}")
        # Return blank ocean raster fallback if completely offline
        return None
