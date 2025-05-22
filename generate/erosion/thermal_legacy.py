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

    print("[INFO] thermal_legacy")
    return heightmap
