from .diamond_square_core import DiamondSquare # Angepasste DiamondSquare Klasse
from ..utils.normalizer import normalize_array # Beispiel
import numpy as np
import time

class TerrainGenerator:
    def __init__(self, size, roughness, seed=None):
        self.size = size
        self.roughness = roughness
        self.seed = seed
        if self.seed is not None:
            try:
                self.seed = int(self.seed)
            except ValueError:
                print(f"Ungültiger Seed '{self.seed}', verwende zufälligen Seed.")
                self.seed = int(time.time()) # Oder None für komplett zufällig
        else:
            self.seed = int(time.time()) # Oder None

        # Initialisiere die Kern-Logik mit dem Seed
        self.ds_algo = DiamondSquare(self.size, self.roughness, seed=self.seed)


    def generate(self):
        # Rufe die Methode in diamond_square_core auf
        raw_terrain = self.ds_algo.diamond_square() # Annahme: diese Methode existiert
        # Normalisiere hier, falls noch nicht im Core geschehen
        # normalized_terrain = normalize_array(raw_terrain, target_min=0, target_max=255)
        # return normalized_terrain
        return raw_terrain # Annahme: diamond_square liefert bereits das nutzbare Array