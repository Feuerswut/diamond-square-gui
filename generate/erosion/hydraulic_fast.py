import os

import numpy as np

import wgpu
# import wgpu.backends.rs  # Rust backend
from wgpu.utils.compute import compute_with_buffers

def hydraulic_erosion(
        heightmap: np.ndarray,
        iterations=5000,
        rainfall=0.05,
        evaporation=0.01,
        sediment_capacity=0.05,
        erosion=0.5,
        deposition=0.1,
        dt=1.0
) -> np.ndarray:
    assert heightmap.ndim == 2
    height, width = heightmap.shape
    size = width * height

    # Load WGSL compute shader
    shader_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "shaders",
        "hydraulic.wgsl"
    )
    with open(shader_path, "r") as f:
        shader_code = f.read()

    # Flattened float32 buffers
    heightmap_buf = heightmap.astype(np.float32).flatten()
    water_buf     = np.zeros_like(heightmap_buf)
    sediment_buf  = np.zeros_like(heightmap_buf)

    # Pack uniforms into raw bytes
    uniforms = np.array([
        width, height,
        dt, rainfall, evaporation,
        sediment_capacity, erosion, deposition
    ], dtype=np.float32).tobytes()

    # Main simulation loop
    for _ in range(iterations):
        # We tell compute_with_buffers:
        # - input_arrays: raw buffers (any buffer-protocol object)
        # - output_arrays: a dict binding index → (length, format_char)
        #   here format 'f' means f32, and length=size elements.
        result = compute_with_buffers(
            input_arrays={
                0: heightmap_buf,
                1: water_buf,
                2: sediment_buf,
                3: uniforms,
            },
            output_arrays={
                0: (size, 'f'),
            },
            shader=shader_code,
        )

        # Grab back the updated heightmap (a memoryview of f32)
        heightmap_buf = np.frombuffer(result[0], dtype=np.float32)
        
    print("[INFO] hydraulic_fast")
    return heightmap_buf.reshape(height, width)
