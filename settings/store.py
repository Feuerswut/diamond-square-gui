class Settings:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Important: Empty [None] not allowed, use [False] instead.
        self.settings = {
            'initial_terrain'   : 129,          # Initial Terrain Array Size Variable (N)
            # Array Initial Edge Condition (2D python List, NOT array)
            'initial_edges'     : [[2.0, 2.0], [2.0, 2.0]],

            'roughness_float'   : 0.7,          # Terrain Roughness Variable (S/dS)
            'boundary_type'     : 'fixed',      # 'fixed' Boundary Condition

            'noise'             : [['simplex', 0.8]],
            'erosion'           : [["thermal"], ["hydraulic"]],
            'smoothing'         : [[False]],#[["gauss",  {'sigma': 3.0, 'scale': 8.0}], [False]]
        }

    def set_initial_edge(self, index, value):
        """Set value for initial_edges based on a flat index (0 to 3)."""
        i, j = divmod(index, len(self.settings['initial_edges'][0]))
        self.settings['initial_edges'][i][j] = value
    
    def get_initial_edge(self, index):
        """Get value for initial_edges based on a flat index (0 to 3)."""
        i, j = divmod(index, len(self.settings['initial_edges'][0]))
        return self.settings['initial_edges'][i][j]
        
    def set(self, key, value):
        if key.startswith('initial_edges_'):
            index = int(key.split('_')[-1])
            self.set_initial_edge(index, value)
        elif key in self.settings:
            self.settings[key] = value
    
    def get(self, key, default=None):
        if key.startswith('initial_edges_'):
            index = int(key.split('_')[-1])
            return self.get_initial_edge(index)
        return self.settings.get(key, default)
    
    def get_all(self):
        return self.settings

# Create a global settings instance
settings = Settings()
