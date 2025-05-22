import threading
from kivy.clock import Clock

from store.buffer import data_buffer
from generate.ds.terrain import make
from settings.store import settings
from texture.plot import plot
from utils.update import update_widget

# Internal state
_generate_lock = threading.Lock()
_generate_thread = None

def generate_ds():
    data_buffer.clear()  # clear old buffer before storing new data

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

    thermal = settings.get('thermal') or False
    hydraulic = settings.get('hydraulic') or False

    # TODO: UI IMPLEMENT, now: Adapter -------------------------
    if thermal and hydraulic:
        erosion = [['thermal'], ['hydraulic']]
    elif thermal:
        erosion = [['thermal']]
    elif hydraulic:
        erosion = [['hydraulic']]
    else:
        erosion = [[False]]
    # ----------------------------------------------------------

    smoothing = settings.get('smoothing') or [False]

    print(f"[USER] generate_terrain @ {n}n {ds}ds with {boundary_type} [{corner_values}]")

    terrain = make(
        size=n,
        roughness=ds,
        boundary=boundary_type,
        corner_values=corner_values,
        erosion=[erosion],
        smoothing=smoothing,
        seed=None
    )

    # Store the full terrain numpy array directly (new buffer API)
    data_buffer.store(terrain)

    global _generate_thread
    with _generate_lock:
        _generate_thread = None

def generate_async(callback=None):
    """Run terrain generation in background if not already running.
    Calls `callback(texture)` on main thread when done.
    """
    global _generate_thread

    def run():
        generate_ds()

        def on_main_thread(dt):
            texture = plot()
            update_widget('asp_texture', 'update_texture', new_texture=texture)
            if callback:
                callback(texture)

        Clock.schedule_once(on_main_thread, 0)

    with _generate_lock:
        if _generate_thread and _generate_thread.is_alive():
            print("[INFO] Generation already in progress, skipping new call.")
            return None

        _generate_thread = threading.Thread(target=run, name="TerrainGeneratorThread")
        _generate_thread.start()
        return _generate_thread
