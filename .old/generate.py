import numpy as np

from buffer import buffer_manager
from settings import settings

from terrain import make

def generate():
    buffer = buffer_manager.get_buffer()

    n = settings.get('initial_terrain')  # Terrain size
    ds = settings.get('roughness_float')  # Roughness
    boundary_type = settings.get('boundary_type')  # Boundary type
    
    top_left = settings.get('initial_edges')[0][0]
    top_right = settings.get('initial_edges')[0][1]
    bottom_left = settings.get('initial_edges')[1][0]
    bottom_right = settings.get('initial_edges')[1][1]

    corner_values = [
        [top_left, top_right],
        [bottom_left, bottom_right]
    ]

    erosion   = settings.get('erosion')   or [False]
    smoothing = settings.get('smoothing') or [False]

    # Print debug information
    print(f"[USER] generate_terrain @ {n}n {ds}ds with {boundary_type}")

    # Generate terrain
    terrain = make(
        size=n, roughness=ds, boundary=boundary_type, 
        corner_values=corner_values, erosion=erosion, smoothing=smoothing, seed=None
    )
       
    buffer.seek(0)  # Move cursor to the beginning before writing
    np.save(buffer, terrain)
    buffer.seek(0)  # Move cursor to the beginning after writing