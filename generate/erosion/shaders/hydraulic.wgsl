// hydraulic.wgsl

struct Uniforms {
    width: u32,
    height: u32,
    dt: f32,
    rainfall: f32,
    evaporation: f32,
    sediment_capacity: f32,
    erosion: f32,
    deposition: f32,
};

@group(0) @binding(0) var<storage, read_write> heightmap : array<f32>;
@group(0) @binding(1) var<storage, read_write> water : array<f32>;
@group(0) @binding(2) var<storage, read_write> sediment : array<f32>;
@group(0) @binding(3) var<uniform> uniforms : Uniforms;

@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) GlobalID : vec3<u32>) {
    let x = GlobalID.x;
    let y = GlobalID.y;
    let width = uniforms.width;
    let height = uniforms.height;
    if (x >= width || y >= height) { return; }

    let idx = y * width + x;
    let idx_left = y * width + max(1, x) - 1;
    let idx_right = y * width + min(width - 2, x) + 1;
    let idx_up = max(1, y) - 1u * width + x;
    let idx_down = min(height - 2u, y) + 1u * width + x;

    water[idx] += uniforms.rainfall;

    let h_center = heightmap[idx] + water[idx];
    let h_left = heightmap[idx_left] + water[idx_left];
    let h_right = heightmap[idx_right] + water[idx_right];
    let h_up = heightmap[idx_up] + water[idx_up];
    let h_down = heightmap[idx_down] + water[idx_down];

    let dh_x = h_center - (h_left + h_right) * 0.5;
    let dh_y = h_center - (h_up + h_down) * 0.5;
    let slope = sqrt(dh_x * dh_x + dh_y * dh_y);
    let capacity = slope * uniforms.sediment_capacity;

    let current_sediment = sediment[idx];
    if (capacity > current_sediment) {
        let delta = (capacity - current_sediment) * uniforms.erosion;
        heightmap[idx] -= delta;
        sediment[idx] += delta;
    } else {
        let delta = (current_sediment - capacity) * uniforms.deposition;
        heightmap[idx] += delta;
        sediment[idx] -= delta;
    }

    water[idx] *= 1.0 - uniforms.evaporation;
}
