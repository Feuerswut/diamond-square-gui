import threading

from store.buffer import buffer
from generate.ds.terrain import make
from settings.store import settings

# Internal state
_generate_lock = threading.Lock()
_generate_thread = None

def generate_ds():
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

    buffer.appendnd(terrain)

    # Release lock when done
    global _generate_thread
    with _generate_lock:
        _generate_thread = None


def generate_async():
    """Run terrain generation in background if not already running."""
    global _generate_thread

    with _generate_lock:
        if _generate_thread and _generate_thread.is_alive():
            print("[INFO] Generation already in progress, skipping new call.")
            return None  # Ignore duplicate call

        _generate_thread = threading.Thread(target=generate_ds, name="TerrainGeneratorThread")
        _generate_thread.start()
        return _generate_thread
