from numba import jit
import numpy as np
import random

class DiamondSquare:
    def __init__(self, size, roughness, seed=None):
        # ... (power of 2 check für size etc.)
        self.size = size
        self.grid_size = (1 << size) + 1 # Actual grid dimension
        self.roughness = roughness
        self.seed = seed
        if self.seed is not None:
            random.seed(self.seed)
            np.random.seed(self.seed) # Auch NumPy's RNG beeinflussen
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=float)

    # Beispiel für eine Funktion, die von JIT profitieren könnte
    @staticmethod
    @jit(nopython=True) # nopython=True für beste Performance
    def _displace(value, roughness_factor, scale):
        return value + (np.random.rand() - 0.5) * roughness_factor * scale

    @staticmethod
    @jit(nopython=True)
    def _diamond_step_core(grid, x, y, half_step, roughness_factor, current_scale):
        count = 0
        avg = 0.0
        # Top-Left
        if x - half_step >= 0 and y - half_step >= 0:
            avg += grid[y - half_step, x - half_step]
            count += 1
        # Top-Right
        if x + half_step < grid.shape[1] and y - half_step >= 0:
            avg += grid[y - half_step, x + half_step]
            count += 1
        # Bottom-Left
        if x - half_step >= 0 and y + half_step < grid.shape[0]:
            avg += grid[y + half_step, x - half_step]
            count += 1
        # Bottom-Right
        if x + half_step < grid.shape[1] and y + half_step < grid.shape[0]:
            avg += grid[y + half_step, x + half_step]
            count += 1

        if count > 0:
            avg /= count
            grid[y, x] = DiamondSquare._displace(avg, roughness_factor, current_scale)


    @staticmethod
    @jit(nopython=True)
    def _square_step_core(grid, x, y, half_step, roughness_factor, current_scale):
        count = 0
        avg = 0.0
        # Top
        if y - half_step >= 0:
            avg += grid[y - half_step, x]
            count += 1
        # Bottom
        if y + half_step < grid.shape[0]:
            avg += grid[y + half_step, x]
            count += 1
        # Left
        if x - half_step >= 0:
            avg += grid[y, x - half_step]
            count += 1
        # Right
        if x + half_step < grid.shape[1]:
            avg += grid[y, x + half_step]
            count += 1

        if count > 0:
            avg /= count
            grid[y, x] = DiamondSquare._displace(avg, roughness_factor, current_scale)


    def diamond_square(self):
        # Initial corners (Beispiel, anpassen an deine Logik)
        self.grid[0, 0] = np.random.rand()
        self.grid[0, self.grid_size - 1] = np.random.rand()
        self.grid[self.grid_size - 1, 0] = np.random.rand()
        self.grid[self.grid_size - 1, self.grid_size - 1] = np.random.rand()

        step = self.grid_size - 1
        current_scale = 1.0 # Start scale

        while step > 1:
            half_step = step // 2
            # Diamond step
            for y in range(half_step, self.grid_size, step):
                for x in range(half_step, self.grid_size, step):
                    DiamondSquare._diamond_step_core(self.grid, x, y, half_step, self.roughness, current_scale)

            # Square step
            for y in range(0, self.grid_size, half_step):
                for x in range((y + half_step) % step, self.grid_size, step):
                        DiamondSquare._square_step_core(self.grid, x, y, half_step, self.roughness, current_scale)

            step //= 2
            current_scale *= (2**(-self.roughness)) # H-Parameter, roughness 0-1

        return self.grid
