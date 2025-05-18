import numpy as np
import os
from kivy.app import App

class SavingService:
    def get_save_path(self, filename="terrain_data.npy"):
        app = App.get_running_app()
        # user_data_dir ist plattformübergreifend verfügbar
        return os.path.join(app.user_data_dir, filename)

    def save_terrain(self, terrain_array, filename="terrain_data.npy"):
        if terrain_array is None:
            print("Keine Daten zum Speichern vorhanden.")
            return False
        try:
            filepath = self.get_save_path(filename)
            np.save(filepath, terrain_array)
            print(f"Terrain gespeichert unter: {filepath}")
            return True
        except Exception as e:
            print(f"Fehler beim Speichern des Terrains: {e}")
            return False

    def load_terrain(self, filename="terrain_data.npy"):
        filepath = self.get_save_path(filename)
        if not os.path.exists(filepath):
            print(f"Keine gespeicherten Daten gefunden unter: {filepath}")
            return None
        try:
            terrain_array = np.load(filepath)
            print(f"Terrain geladen von: {filepath}")
            return terrain_array
        except Exception as e:
            print(f"Fehler beim Laden des Terrains: {e}")
            return None