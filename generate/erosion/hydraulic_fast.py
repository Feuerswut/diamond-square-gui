import wgpu
import wgpu.utils
import numpy as np
import os
import struct

DEFAULT_PARAMS = {
    "dt": 0.005,
    "rain_amount": 0.001,
    "evaporation_rate": 0.001,
    "gravity": 9.81,
    "min_slope_for_erosion": 0.05,
    "erosion_speed": 0.1,
    "deposition_speed": 0.1,
    "sediment_capacity_constant": 0.01,
    "pipe_area": 1.0,
    "pipe_length": 1.0,
    "smoothing_factor": 0.1,
    "tex_width": 0,
    "tex_height": 0,
    "max_iterations_hydro": 10,
    "padding0": 0.0,
    "padding1": 0.0,
}

PARAMS_LAYOUT = [
    ("dt", "f"), ("rain_amount", "f"), ("evaporation_rate", "f"), ("gravity", "f"),
    ("min_slope_for_erosion", "f"),("erosion_speed", "f"), ("deposition_speed", "f"),
    ("sediment_capacity_constant", "f"), ("pipe_area", "f"), ("pipe_length", "f"),
    ("smoothing_factor", "f"),
    ("tex_width", "I"), ("tex_height", "I"), ("max_iterations_hydro", "I"),
    ("padding0", "f"), ("padding1", "f")
]

def get_params_byte_size():
    return sum(struct.calcsize(fmt) for _, fmt in PARAMS_LAYOUT)

def pack_params(params_dict):
    packed_data = bytearray()
    for name, fmt in PARAMS_LAYOUT:
        packed_data.extend(struct.pack(fmt, params_dict[name]))
    return packed_data

def _create_texture_wgpu(device, width, height, texture_format, usage, label=""):
    return device.create_texture(
        label=label,
        size=(width, height, 1),
        format=texture_format,
        dimension="2d",
        usage=usage
    )

def _create_compute_pipeline_from_shader_file_wgpu(device, shader_full_path, bind_group_layouts, label=""):
    if not os.path.exists(shader_full_path):
        raise FileNotFoundError(f"Shader file not found: {shader_full_path}")
    
    with open(shader_full_path, 'r') as f:
        shader_code = f.read()
    
    shader_module_label = os.path.basename(shader_full_path)
    shader_module = device.create_shader_module(label=shader_module_label, code=shader_code)
    
    pipeline_layout = device.create_pipeline_layout(bind_group_layouts=bind_group_layouts)
    
    return device.create_compute_pipeline(
        label=label or shader_module_label + "_pipeline",
        layout=pipeline_layout,
        compute={"module": shader_module, "entry_point": "main"}
    )

def erode_terrain_wgpu(
    initial_terrain_numpy: np.ndarray,
    num_iterations: int = 1,
    shader_dir_path: str = "shaders",
    user_params: dict = None
) -> np.ndarray:
    if not isinstance(initial_terrain_numpy, np.ndarray) or initial_terrain_numpy.ndim != 2:
        raise ValueError("initial_terrain_numpy must be a 2D NumPy array.")
    if initial_terrain_numpy.dtype != np.float32:
        initial_terrain_numpy = initial_terrain_numpy.astype(np.float32)

    height, width = initial_terrain_numpy.shape

    adapter = wgpu.request_adapter(power_preference="high-performance")
    if adapter is None:
        raise RuntimeError("Could not get WGPU adapter.")
    device = adapter.request_device(label="erosion_device", required_features=[], required_limits={})

    sim_params = DEFAULT_PARAMS.copy()
    sim_params["tex_width"] = width
    sim_params["tex_height"] = height
    if user_params:
        sim_params.update(user_params)
    
    params_data_bytes = pack_params(sim_params)
    params_buffer_size = len(params_data_bytes)
    
    params_buffer = device.create_buffer_with_data(
        label="params_uniform_buffer",
        data=params_data_bytes,
        usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST
    )

    tex_usage_read_write = (
        wgpu.TextureUsage.STORAGE_BINDING | 
        wgpu.TextureUsage.TEXTURE_BINDING | 
        wgpu.TextureUsage.COPY_SRC | 
        wgpu.TextureUsage.COPY_DST
    )

    terrain_tex_a = _create_texture_wgpu(device, width, height, "r32float", tex_usage_read_write, "terrain_tex_a")
    terrain_tex_b = _create_texture_wgpu(device, width, height, "r32float", tex_usage_read_write, "terrain_tex_b")
    water_tex_a = _create_texture_wgpu(device, width, height, "r32float", tex_usage_read_write, "water_tex_a")
    water_tex_b = _create_texture_wgpu(device, width, height, "r32float", tex_usage_read_write, "water_tex_b")
    sediment_tex_a = _create_texture_wgpu(device, width, height, "r32float", tex_usage_read_write, "sediment_tex_a")
    sediment_tex_b = _create_texture_wgpu(device, width, height, "r32float", tex_usage_read_write, "sediment_tex_b")
    velocity_tex = _create_texture_wgpu(device, width, height, "rg32float", tex_usage_read_write, "velocity_tex")
    outflow_flux_tex = _create_texture_wgpu(device, width, height, "rgba32float", tex_usage_read_write, "outflow_flux_tex")

    device.queue.write_texture(
        {"texture": terrain_tex_a, "mip_level": 0, "origin": (0, 0, 0)},
        initial_terrain_numpy.tobytes(),
        {"bytes_per_row": width * 4, "rows_per_image": height},
        (width, height, 1)
    )
    zeros_r32 = np.zeros((height, width), dtype=np.float32).tobytes()
    zeros_rg32 = np.zeros((height, width, 2), dtype=np.float32).tobytes()
    zeros_rgba32 = np.zeros((height, width, 4), dtype=np.float32).tobytes()

    device.queue.write_texture({"texture": water_tex_a, "mip_level": 0, "origin": (0,0,0)}, zeros_r32, {"bytes_per_row": width*4, "rows_per_image": height}, (width,height,1))
    device.queue.write_texture({"texture": sediment_tex_a, "mip_level": 0, "origin": (0,0,0)}, zeros_r32, {"bytes_per_row": width*4, "rows_per_image": height}, (width,height,1))
    device.queue.write_texture({"texture": velocity_tex, "mip_level": 0, "origin": (0,0,0)}, zeros_rg32, {"bytes_per_row": width*8, "rows_per_image": height}, (width,height,1))
    device.queue.write_texture({"texture": outflow_flux_tex, "mip_level": 0, "origin": (0,0,0)}, zeros_rgba32, {"bytes_per_row": width*16, "rows_per_image": height}, (width,height,1))

    current_terrain_tex = terrain_tex_a
    next_terrain_tex = terrain_tex_b
    current_water_tex = water_tex_a
    next_water_tex = water_tex_b
    current_sediment_tex = sediment_tex_a
    next_sediment_tex = sediment_tex_b

    storage_texture_bgl_entry = lambda binding, fmt, access: {
        "binding": binding, "visibility": wgpu.ShaderStage.COMPUTE,
        "storage_texture": {"access": access, "format": fmt, "view_dimension": "2d"}
    }
    sampled_texture_bgl_entry = lambda binding, fmt: {
        "binding": binding, "visibility": wgpu.ShaderStage.COMPUTE,
        "texture": {"sample_type": "unfilterable-float", "view_dimension": "2d", "multisampled": False}
    }
    uniform_buffer_bgl_entry = lambda binding: {
        "binding": binding, "visibility": wgpu.ShaderStage.COMPUTE,
        "buffer": {"type": wgpu.BufferBindingType.uniform, "has_dynamic_offset": False, "min_binding_size": params_buffer_size}
    }

    pipelines = {}
    bind_group_layouts_cache = {}

    def get_bgl(device_handle, bgl_key_tuple):
        if bgl_key_tuple not in bind_group_layouts_cache:
            entries = list(bgl_key_tuple)
            bind_group_layouts_cache[bgl_key_tuple] = device_handle.create_bind_group_layout(entries=entries)
        return bind_group_layouts_cache[bgl_key_tuple]

    shader_files_ordered = [
        "rain.frag", "outflow_flux.frag", "velocity_field.frag", 
        "water_surface.frag", "erosion_deposition.frag", 
        "sediment_transportation.frag", "evaporation.frag", "smooth.frag"
    ]

    shader_configs = {
        "rain.frag": {
            "bgl_entries_tuple": tuple([
                uniform_buffer_bgl_entry(0),
                storage_texture_bgl_entry(1, "r32float", "write-only"),
            ]),
            "bindings_map": {"params":0, "water_out":1}
        },
        "outflow_flux.frag": {
            "bgl_entries_tuple": tuple([
                uniform_buffer_bgl_entry(0),
                sampled_texture_bgl_entry(1, "r32float"),
                sampled_texture_bgl_entry(2, "r32float"),
                storage_texture_bgl_entry(3, "rgba32float", "write-only"),
            ]),
            "bindings_map": {"params":0, "terrain_in":1, "water_in":2, "flux_out":3}
        },
        "velocity_field.frag": {
             "bgl_entries_tuple": tuple([
                uniform_buffer_bgl_entry(0),
                sampled_texture_bgl_entry(1, "rgba32float"),
                sampled_texture_bgl_entry(2, "r32float"),
                storage_texture_bgl_entry(3, "rg32float", "write-only"),
            ]),
            "bindings_map": {"params":0, "flux_in":1, "water_in":2, "velocity_out":3}
        },
        "water_surface.frag": {
            "bgl_entries_tuple": tuple([
                uniform_buffer_bgl_entry(0),
                sampled_texture_bgl_entry(1, "r32float"),
                sampled_texture_bgl_entry(2, "rgba32float"),
                storage_texture_bgl_entry(3, "r32float", "write-only"),
            ]),
            "bindings_map": {"params":0, "water_in":1, "flux_in":2, "water_out":3}
        },
        "erosion_deposition.frag": {
            "bgl_entries_tuple": tuple([
                uniform_buffer_bgl_entry(0),
                sampled_texture_bgl_entry(1, "r32float"),
                sampled_texture_bgl_entry(2, "r32float"),
                sampled_texture_bgl_entry(3, "r32float"),
                sampled_texture_bgl_entry(4, "rg32float"),
                storage_texture_bgl_entry(5, "r32float", "write-only"),
                storage_texture_bgl_entry(6, "r32float", "write-only"),
            ]),
            "bindings_map": {"params":0, "terrain_in":1, "water_in":2, "sediment_in":3, "velocity_in":4, "terrain_out":5, "sediment_out":6}
        },
        "sediment_transportation.frag": {
            "bgl_entries_tuple": tuple([
                uniform_buffer_bgl_entry(0),
                sampled_texture_bgl_entry(1, "r32float"),
                sampled_texture_bgl_entry(2, "rg32float"),
                sampled_texture_bgl_entry(3, "r32float"),
                storage_texture_bgl_entry(4, "r32float", "write-only"),
            ]),
            "bindings_map": {"params":0, "sediment_in":1, "velocity_in":2, "water_in":3, "sediment_out":4}
        },
        "evaporation.frag": {
            "bgl_entries_tuple": tuple([
                uniform_buffer_bgl_entry(0),
                sampled_texture_bgl_entry(1, "r32float"),
                storage_texture_bgl_entry(2, "r32float", "write-only"),
            ]),
            "bindings_map": {"params":0, "water_in":1, "water_out":2}
        },
        "smooth.frag": {
            "bgl_entries_tuple": tuple([
                uniform_buffer_bgl_entry(0),
                sampled_texture_bgl_entry(1, "r32float"),
                storage_texture_bgl_entry(2, "r32float", "write-only"),
            ]),
            "bindings_map": {"params":0, "terrain_in":1, "terrain_out":2}
        },
    }

    for shader_name, config in shader_configs.items():
        bgl = get_bgl(device, config["bgl_entries_tuple"])
        shader_full_path = os.path.join(shader_dir_path, shader_name)
        pipelines[shader_name] = _create_compute_pipeline_from_shader_file_wgpu(
            device, shader_full_path, [bgl], label=shader_name + "_pipeline"
        )

    workgroup_size_x, workgroup_size_y = 8, 8
    dispatch_x = (width + workgroup_size_x - 1) // workgroup_size_x
    dispatch_y = (height + workgroup_size_y - 1) // workgroup_size_y

    for i in range(num_iterations):
        command_encoder = device.create_command_encoder(label=f"iteration_{i}_encoder")
        tex_map = {
            "current_terrain": current_terrain_tex.create_view(),
            "next_terrain": next_terrain_tex.create_view(),
            "current_water": current_water_tex.create_view(),
            "next_water": next_water_tex.create_view(),
            "current_sediment": current_sediment_tex.create_view(),
            "next_sediment": next_sediment_tex.create_view(),
            "velocity": velocity_tex.create_view(),
            "outflow_flux": outflow_flux_tex.create_view(),
        }
        
        for shader_name in shader_files_ordered:
            pipeline = pipelines[shader_name]
            config = shader_configs[shader_name]
            bgl = get_bgl(device, config["bgl_entries_tuple"])
            bind_group_entries = []
            if "params" in config["bindings_map"]:
                 bind_group_entries.append({"binding": config["bindings_map"]["params"], "resource": {"buffer": params_buffer, "offset": 0, "size": params_buffer_size}})

            current_bindings = {}
            if shader_name == "rain.frag":
                current_bindings = {"water_out": tex_map["next_water"]}
            elif shader_name == "outflow_flux.frag":
                current_bindings = {"terrain_in": tex_map["current_terrain"], "water_in": tex_map["current_water"], "flux_out": tex_map["outflow_flux"]}
            elif shader_name == "velocity_field.frag":
                 current_bindings = {"flux_in": tex_map["outflow_flux"], "water_in": tex_map["current_water"], "velocity_out": tex_map["velocity"]}
            elif shader_name == "water_surface.frag":
                current_bindings = {"water_in": tex_map["current_water"], "flux_in": tex_map["outflow_flux"], "water_out": tex_map["next_water"]}
            elif shader_name == "erosion_deposition.frag":
                current_bindings = {
                    "terrain_in": tex_map["current_terrain"], "water_in": tex_map["current_water"], 
                    "sediment_in": tex_map["current_sediment"], "velocity_in": tex_map["velocity"],
                    "terrain_out": tex_map["next_terrain"], "sediment_out": tex_map["next_sediment"]
                }
            elif shader_name == "sediment_transportation.frag":
                current_bindings = {
                    "sediment_in": tex_map["current_sediment"], "velocity_in": tex_map["velocity"], 
                    "water_in": tex_map["current_water"], "sediment_out": tex_map["next_sediment"]
                }
            elif shader_name == "evaporation.frag":
                current_bindings = {"water_in": tex_map["current_water"], "water_out": tex_map["next_water"]}
            elif shader_name == "smooth.frag":
                current_bindings = {"terrain_in": tex_map["current_terrain"], "terrain_out": tex_map["next_terrain"]}

            for name, binding_idx in config["bindings_map"].items():
                if name == "params": continue
                if name in current_bindings:
                    bind_group_entries.append({"binding": binding_idx, "resource": current_bindings[name]})

            bind_group = device.create_bind_group(layout=bgl, entries=bind_group_entries)
            
            compute_pass = command_encoder.begin_compute_pass()
            compute_pass.set_pipeline(pipeline)
            compute_pass.set_bind_group(0, bind_group, [], 0, 0)
            compute_pass.dispatch_workgroups(dispatch_x, dispatch_y, 1)
            compute_pass.end()

            if shader_name == "rain.frag" or shader_name == "water_surface.frag" or shader_name == "evaporation.frag":
                current_water_tex, next_water_tex = next_water_tex, current_water_tex
                tex_map["current_water"], tex_map["next_water"] = tex_map["next_water"], tex_map["current_water"]
            
            if shader_name == "erosion_deposition.frag":
                current_terrain_tex, next_terrain_tex = next_terrain_tex, current_terrain_tex
                tex_map["current_terrain"], tex_map["next_terrain"] = tex_map["next_terrain"], tex_map["current_terrain"]
                current_sediment_tex, next_sediment_tex = next_sediment_tex, current_sediment_tex
                tex_map["current_sediment"], tex_map["next_sediment"] = tex_map["next_sediment"], tex_map["current_sediment"]

            if shader_name == "sediment_transportation.frag":
                current_sediment_tex, next_sediment_tex = next_sediment_tex, current_sediment_tex
                tex_map["current_sediment"], tex_map["next_sediment"] = tex_map["next_sediment"], tex_map["current_sediment"]

            if shader_name == "smooth.frag":
                current_terrain_tex, next_terrain_tex = next_terrain_tex, current_terrain_tex
                tex_map["current_terrain"], tex_map["next_terrain"] = tex_map["next_terrain"], tex_map["current_terrain"]

        device.queue.submit([command_encoder.finish()])

    output_buffer_size = width * height * 4
    output_buffer = device.create_buffer(
        label="output_terrain_buffer",
        size=output_buffer_size,
        usage=wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.MAP_READ
    )

    command_encoder = device.create_command_encoder(label="readback_encoder")
    command_encoder.copy_texture_to_buffer(
        source={"texture": current_terrain_tex, "mip_level": 0, "origin": (0, 0, 0)},
        destination={"buffer": output_buffer, "offset": 0, "bytes_per_row": width * 4, "rows_per_image": height},
        copy_size=(width, height, 1)
    )
    device.queue.submit([command_encoder.finish()])

    mapped_data = output_buffer.map_read()
    result_numpy = np.frombuffer(mapped_data, dtype=np.float32).copy()
    result_numpy = result_numpy.reshape((height, width))
    output_buffer.unmap()
    
    return result_numpy

def hydraulic_erosion(array):
    return erode_terrain_wgpu(array)