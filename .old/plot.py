from kivy.graphics.texture import Texture

from PIL    import Image
from io     import BytesIO
from buffer import buffer_manager

import numpy as np

def remove_padding(padded_array, pad_width=1):
    """
    Remove zero-padding from the edges of a 2D numpy array.
    
    :param padded_array: The padded 2D numpy array.
    :param pad_width: The width of the padding to remove around the image.
    :return: The unpadded 2D numpy array.
    """
    if pad_width < 0:
        raise ValueError("pad_width must be a non-negative integer")
    
    # Determine the slice indices
    if pad_width > 0:
        slices = (slice(pad_width, -pad_width), slice(pad_width, -pad_width))
    else:
        slices = (slice(None), slice(None))
    
    # Return the sliced array
    return padded_array[slices]

def add_padding(array, pad_width=1):
    """
    Add zero-padding around the edges of a 2D numpy array.
    
    :param array: The original 2D numpy array.
    :param pad_width: The width of the padding to add around the image.
    :return: The padded 2D numpy array.
    """
    return np.pad(array, pad_width, mode='edge')

def normalize_array(array):
    """
    Normalize the array to the range [0, 1] with clipping.
    """
    array_min = np.min(array)
    array_max = np.max(array)
    return np.clip((array - array_min) / (array_max - array_min), 0, 1)

def generate_gradient(colors, steps=256):
    """
    Generates a color gradient given a list of RGBA colors.
    
    :param colors: List of RGBA colors, each as a list of four integers [R, G, B, A].
    :param steps: Total number of gradient steps.
    :return: A NumPy array representing the gradient.
    """
    gradient = np.zeros((steps, 4), dtype=np.uint8)

    # Calculate the number of steps between each pair of colors
    segment_steps = steps // (len(colors) - 1)

    for i in range(len(colors) - 1):
        start_color = np.array(colors[i])
        end_color = np.array(colors[i + 1])
        
        for j in range(segment_steps):
            t = j / segment_steps
            gradient[i * segment_steps + j] = (1 - t) * start_color + t * end_color

    # Ensure the last color is set correctly (in case of rounding issues)
    gradient[-1] = colors[-1]

    return gradient

def grayscale(array, resize=False, **kwargs):
    """
    Create a PNG from a normalized numpy array with optional padding.
    Assumes each array point maps directly to one pixel.
    The input array is expected to be in float format.
    
    :param array: The input numpy array.
    :param pad_width: The width of the padding to add around the image.
    :return: PNG 16bit grayscale.
    """

    # Normalize the float array to the range [0, 65535] for 16-bit image
    array_min = np.min(array)
    array_max = np.max(array)
    normalized_array = ((array - array_min) / (array_max - array_min) * 65535).astype(np.uint16)
    
    # Ensure the array has the correct dimensions and format
    if normalized_array.ndim != 2:
        raise ValueError("Expected a 2D numpy array for grayscale images.")
    
    if resize:
        pass
        # resized_array = np.zeros(new_shape, dtype=np.uint16)

    # Create PIL Image from the normalized array
    image = Image.fromarray(normalized_array, mode='I;16')
 
    return image

def grayscale_centered(array, border_width=1, **kwargs):
    """
    Create a PNG from a normalized numpy array with optional padding.
    Assumes each array point maps directly to one pixel.
    The input array is expected to be in float format.
    
    :param array: The input numpy array.
    :param pad_width: The width of the padding to add around the image.
    :return: PNG 16bit grayscale; centered quarter
    """
    # Determine the central part of the terrain array
    height, width = array.shape
    center_start_x = 3 * width // 8
    center_start_y = 3 * height // 8
    center_end_x = 5 * width // 8
    center_end_y = 5 * height // 8
        
    # Crop the central part
    array = array[center_start_y:center_end_y, center_start_x:center_end_x]

    # Apply grayscale function
    image = grayscale(array, border_width=border_width, **kwargs)

    return image

def colored(array):
    """
    Numpy array to colored PNG using a custom colormap.
    :return: PNG 16bit colored RGBA.
    """
    # Unknown fix for array edge trash (TODO: fix)
    array = remove_padding(array)

    # Normalize the array to the range [0, 1]
    norm_array = normalize_array(array)

    # Define the color gradient: steps list
    i = int(51) # 1/5 of 255, 0-5i

    matplotlib_terrain = [
        [1*i, 1*i, 3*i, 5*i], # Dark blue   (deep water)
        [0*i, 3*i, 5*i, 5*i], # Blue        (shallow water)
        [0*i, 4*i, 2*i, 5*i], # Green       (lowlands)
        [5*i, 5*i, 3*i, 5*i], # Yellow      (higher elevation)
        [3*i, 2*i, 1*i, 5*i], # Brown       (mountains)
        [5*i, 5*i, 5*i, 5*i], # White       (snow-capped peaks)
    ]

    colors = generate_gradient(matplotlib_terrain)

    # Map array values to color indices
    colormap = np.array([colors[int(val * 255)] for val in norm_array.flatten()])
    colormap = colormap.reshape((array.shape[0], array.shape[1], 4))

    # Convert to PIL image
    image = Image.fromarray(colormap.astype('uint8'), 'RGBA')
    return image

def plot():
    """
    from buffer: numpy array to Kivy texture
    :return: Texture object
    """
    try: # Load terrain from buffer
        buffer = buffer_manager.get_buffer()
        buffer.seek(0)
        array = np.load(buffer)
    except Exception as e:
        print(f"Exception at plot: {str(e)}")

    image = colored(array)
    image_data = image.tobytes()

    texture = Texture.create(size=image.size, colorfmt='rgba')
    texture.blit_buffer(image_data, colorfmt='rgba', bufferfmt='ubyte')

    # Disable smoothing
    texture.mag_filter = 'nearest'
    texture.min_filter = 'nearest'

    texture.flip_vertical()

    return texture
