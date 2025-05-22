import numpy as np

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
