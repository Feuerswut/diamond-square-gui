import random
import math
import numpy as np
import opensimplex

from generate.ds.terrain_edges  import *
from PIL            import Image, ImageFilter

from generate.erosion.hydraulic_fast import hydraulic_erosion
from generate.erosion.thermal_legacy import thermal_erosion

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
            if not all(isinstance(param, dict) for param in params):
                raise TypeError(f"Invalid parameter format in setting: {setting}. Expected list of dicts.")

            params_dict = {k: v for param in params for k, v in param.items()}

            if method == 'thermal':
                a = thermal_erosion(a, **params_dict)
            elif method == 'hydraulic':
                a = hydraulic_erosion(a, **params_dict)
            else:
                raise ValueError(f"Unsupported erosion method: {method}")
        else:
            raise TypeError(f"Invalid erosion setting type: {type(setting)}. Expected list.")

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
