import threading

from generate.buffer import buffer
from generate.ds.terrain import make
from settings.store import settings

def generate():
    buffer.clear()

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

    print(f"[USER] generate_terrain @ {n}n {ds}ds with {boundary_type}")

    terrain = make(
        size=n,
        roughness=ds,
        boundary=boundary_type,
        corner_values=corner_values,
        erosion=erosion,
        smoothing=smoothing,
        seed=None
    )

    buffer.append(terrain)

def generate_async():
    """Run generate() in a separate thread."""
    thread = threading.Thread(target=generate, name="TerrainGeneratorThread")
    thread.start()
    return thread
