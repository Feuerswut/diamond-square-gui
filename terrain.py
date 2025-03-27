import random
import math
import numpy as np
import opensimplex

from terrain_edges  import *
from PIL            import Image, ImageFilter

def add_noise(heightmap, ttype='simplex', scale=0.01, strength=0.4, seed=0):
    new_map = np.copy(heightmap)
    if ttype == 'perlin':
        np.random.seed(seed)
        noise_map = np.random.normal(0, 1, new_map.shape)
        new_map += noise_map * scale
    elif ttype == 'simplex':
        noise_gen = opensimplex.OpenSimplex(seed)
        for i in range(new_map.shape[0]):
            for j in range(new_map.shape[1]):
                new_map[i][j] += strength * noise_gen.noise2(i * scale, j * scale)
    return new_map

def hydraulic_erosion(
    heightmap:                np.ndarray,
    iterations:               int = 5,
    rain_amount:              float = 0.05,
    evaporation_rate:         float = 0.01,
    erosion_rate:             float = 0.5,
    sediment_capacity_factor: float = 0.05
) -> np.ndarray:

    """
    Simulate hydraulic erosion on the heightmap.
    
    :param heightmap: 2D numpy array representing the terrain.
    :param iterations: Number of erosion iterations.
    :param rain_amount: Amount of water added each iteration.
    :param evaporation_rate: Rate at which water evaporates.
    :param erosion_rate: Rate at which terrain is eroded.
    :param sediment_capacity_factor: Maximum amount of sediment water can carry, relative to the water amount.
    :return: Modified heightmap after hydraulic erosion.
    """

    water = np.zeros_like(heightmap)
    sediment = np.zeros_like(heightmap)
    
    for iteration in range(iterations):
        # Step 1: Rainfall, adding water uniformly to all cells
        water += rain_amount
        
        # Step 2: Erosion and sediment transport
        for y in range(1, heightmap.shape[0] - 1):
            for x in range(1, heightmap.shape[1] - 1):
                # Calculate height differences with neighbors
                dh = np.array([
                    heightmap[y, x] - heightmap[y-1, x],  # up
                    heightmap[y, x] - heightmap[y+1, x],  # down
                    heightmap[y, x] - heightmap[y, x-1],  # left
                    heightmap[y, x] - heightmap[y, x+1],  # right
                ])
                
                # Only consider positive slopes (downhill)
                positive_dh = np.maximum(dh, 0)
                total_dh = np.sum(positive_dh)
                
                if total_dh > 0:
                    # Calculate flow proportionally to the height differences
                    flow = erosion_rate * positive_dh / total_dh
                    
                    for i, (dy, dx) in enumerate([(-1, 0), (1, 0), (0, -1), (0, 1)]):
                        # Water flow to neighboring cells
                        amount = flow[i] * water[y, x]
                        water[y, x] -= amount
                        water[y + dy, x + dx] += amount
                        
                        # Erode heightmap and carry sediment proportionally to flow
                        erosion_amount = min(amount * erosion_rate, heightmap[y, x])
                        heightmap[y, x] -= erosion_amount
                        sediment[y, x] += erosion_amount
                        
                        # Calculate sediment capacity and transport sediment
                        max_sediment_capacity = amount * sediment_capacity_factor
                        sediment_to_carry = min(sediment[y, x], max_sediment_capacity)
                        sediment[y, x] -= sediment_to_carry
                        sediment[y + dy, x + dx] += sediment_to_carry

            print(f"[INFO] hydraulic_erosion [{iteration + 1}/{iterations}] [{y}/{heightmap.shape[0] - 1}]           ", end='\r')

        # Step 3: Evaporation - some water evaporates
        water *= (1 - evaporation_rate)
        
        # Step 4: Sedimentation - deposit sediment back onto the heightmap
        deposition = np.minimum(sediment, water)
        heightmap += deposition
        sediment -= deposition  # Remove deposited sediment

    return heightmap

def thermal_erosion(heightmap, iterations=12, talus_angle=0.06, thermal_coefficient=0.5):
    """
    Simulate thermal erosion on the heightmap to modify terrain features.
    :param heightmap: 2D numpy array representing the terrain.
    :param iterations: Number of erosion iterations. Typical range is 5 to 50, where more iterations result in more pronounced erosion.
    :param talus_angle: Critical slope angle above which material will be moved. Typical range is 0.01 to 1.0, where smaller values lead to more erosion.
    :param thermal_coefficient: Proportion of height difference to move per iteration. Typical range is 0.1 to 1.0, where larger values cause more aggressive erosion.
    :return: Modified heightmap after applying thermal erosion.
    """
    heightmap = heightmap.astype(float)  # Ensure floating-point precision

    for iteration in range(iterations):
        # Iterate over each cell, except for the border
        for y in range(1, heightmap.shape[0] - 1):
            for x in range(1, heightmap.shape[1] - 1):
                center_height = heightmap[y, x]

                # Calculate height differences with neighbors
                neighbors = {
                    'up': heightmap[y-1, x],
                    'down': heightmap[y+1, x],
                    'left': heightmap[y, x-1],
                    'right': heightmap[y, x+1]
                }

                for direction, neighbor_height in neighbors.items():
                    height_diff = center_height - neighbor_height

                    if height_diff > talus_angle:
                        move_amount = thermal_coefficient * (height_diff - talus_angle)
                        
                        # Update heightmap based on direction
                        if direction == 'up':
                            heightmap[y, x] -= move_amount
                            heightmap[y-1, x] += move_amount
                        elif direction == 'down':
                            heightmap[y, x] -= move_amount
                            heightmap[y+1, x] += move_amount
                        elif direction == 'left':
                            heightmap[y, x] -= move_amount
                            heightmap[y, x-1] += move_amount
                        elif direction == 'right':
                            heightmap[y, x] -= move_amount
                            heightmap[y, x+1] += move_amount
            print(f"[INFO] thermal_erosion: [{iteration + 1}/{iterations}] [{y}/{heightmap.shape[0]+1}]          ", end='\r')

    return heightmap

def gaussian_smoothing(array, sigma=2, scale=4):
    # Convert array to PIL Image
    image = Image.fromarray(np.uint8(array * 255 / np.max(array)))  # Normalize array for image conversion
    image = image.resize((array.shape[1] * scale, array.shape[0] * scale), Image.NEAREST)  # Scale image
    image = image.filter(ImageFilter.GaussianBlur(radius=sigma))  # Apply Gaussian blur
    array = np.array(image)  # Convert back to numpy array
    array = array.astype(float) / 255.0  # Normalize back to [0, 1]
    return array

def single_diamond_square_step(d, w, s, avg, step=0, steps=0):
    n = d.shape[0]
    v = w // 2

    diamond = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
    square = [(-1, 0), (0, -1), (1, 0), (0, 1)]

    for i in range(v, n, w):
        for j in range(v, n, w):
            d[i, j] = avg(d, i, j, v, diamond) + random.uniform(-s, s)
        print(f"[INFO] diamond_square: [{step}/{steps}] diamond [{i}/{n+1}]                ", end='\r')

    for i in range(v, n, w):
        for j in range(0, n, w):
            d[i, j] = avg(d, i, j, v, square) + random.uniform(-s, s)
        print(f"[INFO] diamond_square: [{step}/{steps}] square1 [{i}/{n+1}]                ", end='\r')

    for i in range(0, n, w):
        for j in range(v, n, w):
            d[i, j] = avg(d, i, j, v, square) + random.uniform(-s, s)
        print(f"[INFO] diamond_square: [{step}/{steps}] square0 [{i}/{n+1}]                ", end='\r')

def make_diamond_square(corner_values, steps, boundary_type, roughness):
    array = np.zeros((steps, steps))

    # Set initial corner values
    array[ 0,  0] = corner_values[0][0]
    array[ 0, -1] = corner_values[0][1]
    array[-1,  0] = corner_values[1][0]
    array[-1, -1] = corner_values[1][1]

    # Translate Boundaries
    boundary_functions = {
        'clamped'       : clamp,
        'fixed'         : fixed,
        'mirrored'      : mirror,
        'periodic'      : periodic,
        'reflective'    : reflective,
        'wrap_around'   : wrap_around,
    }

    function = boundary_functions.get(boundary_type, NotImplementedError)
    # print(function)

    w, s = steps - 1, 1.0
    steps-=1; steps=int(math.log2(steps)); step = 0 # print logic
    while w > 1:
        single_diamond_square_step(array, w, s, function, step=step, steps=steps)
        w //= 2
        s *= roughness
        step+=1 # print logic
    print(f"['diamond_square'] Done                             ")
    return array

def rescale_array(array, new_shape, order=3):
    """
    Rescale the input array to a new shape using scipy.ndimage.zoom.
    
    :param array: 2D or 3D numpy array to be resized.
    :param new_shape: Tuple with the new shape of the array (height, width) or (depth, height, width).
    :param order: Interpolation order (0=nearest, 1=linear, 3=cubic, etc.).
    :return: Rescaled numpy array.
    """
    image = Image.fromarray(np.uint8(array * 255 / np.max(array)))  # Convert array to image
    image = image.resize(new_shape[::-1], Image.BICUBIC if order == 3 else Image.NEAREST)  # Resize image
    resized_array = np.array(image)  # Convert back to numpy array
    resized_array = resized_array.astype(float) / 255.0  # Normalize back to [0, 1]
    return resized_array

def make(
        size=129, roughness=0.7, boundary='fixed', seed=None, scale=None,
        corner_values   = [[2, 2], [2, 2]], 
        erosion         = [['thermal'], ['hydraulic']], 
        smoothing       = [[False]]
    ):

    # Set seed if not overwritten:
    if seed is None:
        seed = random.randint(0, 4294967295)

    print(f"[INFO] set seed: {seed}")
    random.seed(seed)
    np.random.seed(seed)
    opensimplex.seed(seed)

    a = make_diamond_square(corner_values, size, boundary, roughness)

    # Apply noise TODO stub
    a = add_noise(a)

    # Apply erosion from settings-list
    for setting in erosion:
        if setting == [False]:
            break
        elif isinstance(setting, list):
            method, *params = setting
            params_dict = {k: v for param in params if isinstance(param, dict) for k, v in param.items()}
            if method == 'thermal' and isinstance(params, list):
                a = thermal_erosion(a, **params_dict)
            elif method == 'hydraulic' and isinstance(params, list):
                a = hydraulic_erosion(a, **params_dict)
            else:
                print(f'[WARN] in terrain.make er: {method} not implemented or invalid params              ', end='\r')
        print(f"{setting} Done                                          ", end='\r')
        print()

    # Apply smoothing from settings-list
    smoothing = [smoothing] if isinstance(smoothing[0], str) else smoothing

    for setting in smoothing:
        if setting == [False]:
            break
        elif isinstance(setting, list):
            method, *params = setting
            params_dict = {k: v for param in params if isinstance(param, dict) for k, v in param.items()}
            if method == 'gauss' and isinstance(params, list):
                a = gaussian_smoothing(a, **params_dict)
            else:
                print(f'[WARN] in terrain.make sm: {method} not implemented or invalid params')
        print(f"{setting} Done                                          ", end='\r')
        print()

    # Rescale NumPy Array (optional)
    if scale is not None:
        a = rescale_array(a, new_shape=(scale,scale,), order=1)

    return a
