import numpy as np

def hydraulic_erosion(
    heightmap:                np.ndarray,
    iterations:               int = 5,
    rain_amount:              float = 0.05,
    evaporation_rate:         float = 0.01,
    erosion_rate:             float = 0.5,
    sediment_capacity_factor: float = 0.05,
) -> np.ndarray:
    """
    A fully-vectorized hydraulic erosion on a 2D heightmap.
    Uses only NumPy (or swap in CuPy by setting xp = cupy).
    """

    # You can replace xp = np with:
    try: import cupy as xp
    except ImportError: xp = np
    xp = np

    h = heightmap.copy().astype(float)
    water    = xp.zeros_like(h)
    sediment = xp.zeros_like(h)
    H, W = h.shape

    # pre-allocate shifts
    for it in range(iterations):
        # 1) Rain
        water += rain_amount

        # 2) Compute height diffs to neighbors
        #    pad edges with zeros so everything stays same shape
        pad_h = xp.pad(h, 1, mode='edge')
        cen = pad_h[1:-1,1:-1]
        up    = cen - pad_h[0:-2,1:-1]
        down  = cen - pad_h[2:  ,1:-1]
        left  = cen - pad_h[1:-1,0:-2]
        right = cen - pad_h[1:-1,2:  :]

        # only downhill slopes
        pos_up    = xp.maximum(up,    0.0)
        pos_down  = xp.maximum(down,  0.0)
        pos_left  = xp.maximum(left,  0.0)
        pos_right = xp.maximum(right, 0.0)

        total_dh = pos_up + pos_down + pos_left + pos_right
        mask = total_dh > 0

        # flow fraction per direction
        frac = xp.zeros((4, H, W), dtype=float)
        frac[0][mask] = erosion_rate * pos_up[mask]    / total_dh[mask]
        frac[1][mask] = erosion_rate * pos_down[mask]  / total_dh[mask]
        frac[2][mask] = erosion_rate * pos_left[mask]  / total_dh[mask]
        frac[3][mask] = erosion_rate * pos_right[mask] / total_dh[mask]

        # compute flow amounts
        w = water
        amt_up    = frac[0] * w
        amt_down  = frac[1] * w
        amt_left  = frac[2] * w
        amt_right = frac[3] * w

        # update water by sending out and receiving flows
        water = (
            w
            - (amt_up + amt_down + amt_left + amt_right)
            + xp.pad(amt_down,  ((1,0),(0,0)), mode='constant')[0:H, :]
            + xp.pad(amt_up,    ((0,1),(0,0)), mode='constant')[1:H+1, :]
            + xp.pad(amt_right, ((0,0),(1,0)), mode='constant')[:, 0:W]
            + xp.pad(amt_left,  ((0,0),(0,1)), mode='constant')[:, 1:W+1]
        )

        # erosion: remove terrain into sediment
        eroded = xp.minimum(erosion_rate * (amt_up+amt_down+amt_left+amt_right), h)
        h       = h - eroded
        sediment += eroded

        # sediment transport: carry only up to capacity
        capacity = (amt_up+amt_down+amt_left+amt_right) * sediment_capacity_factor
        moveable = xp.minimum(sediment, capacity)
        sediment -= moveable

        # distribute moved sediment same way as water flows
        s_up    = moveable * (frac[0] / erosion_rate)
        s_down  = moveable * (frac[1] / erosion_rate)
        s_left  = moveable * (frac[2] / erosion_rate)
        s_right = moveable * (frac[3] / erosion_rate)
        sediment = (
            sediment
            - (s_up + s_down + s_left + s_right)
            + xp.pad(s_down,  ((1,0),(0,0)), mode='constant')[0:H, :]
            + xp.pad(s_up,    ((0,1),(0,0)), mode='constant')[1:H+1, :]
            + xp.pad(s_right, ((0,0),(1,0)), mode='constant')[:, 0:W]
            + xp.pad(s_left,  ((0,0),(0,1)), mode='constant')[:, 1:W+1]
        )

        # 3) Evaporation
        water *= (1 - evaporation_rate)

        # 4) Deposition
        depos = xp.minimum(sediment, water)
        h += depos
        sediment -= depos

        # optional progress  
        print(f"Erosion iter {it+1}/{iterations}", end='\r')

    return h
