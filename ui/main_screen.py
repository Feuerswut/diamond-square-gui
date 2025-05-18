# ... (in Kivy Screen Klasse)
# self.async_manager = AsyncManager() # Initialisieren

def start_generation_async(self):
    # UI-Elemente für Eingaben (size, roughness, seed) auslesen
    size_input = self.ids.size_input.text
    roughness_input = self.ids.roughness_input.text
    seed_input = self.ids.seed_input.text

    try:
        size = int(size_input) # Fehlerbehandlung hinzufügen!
        roughness = float(roughness_input) # Fehlerbehandlung hinzufügen!
        seed = seed_input if seed_input else None
    except ValueError:
        # Zeige Fehler in der UI
        self.update_status("Ungültige Eingabe!")
        return

    self.update_status("Generiere Terrain...")
    # Deaktiviere den Button, um doppelte Klicks zu verhindern
    self.ids.generate_button.disabled = True 

    # Erstelle Instanz des Generators mit aktuellen Werten
    self.terrain_gen_instance = TerrainGenerator(size, roughness, seed)

    self.async_manager.run_async(
        self.terrain_gen_instance.generate, # Die Methode zum Ausführen
        callback=self.on_generation_complete
    )

def on_generation_complete(self, terrain_array):
    self.ids.generate_button.disabled = False # Button wieder aktivieren
    if terrain_array is not None:
        self.update_status("Terrain generiert!")
        # Hier das Terrain anzeigen, z.B. im terrain_display Widget
        # self.ids.terrain_display_widget.update_terrain(terrain_array)
        self.current_terrain_data = terrain_array # Fürs Speichern merken
        print("Terrain-Generierung abgeschlossen.")
    else:
        self.update_status("Fehler bei der Generierung.")

def update_status(self, message):
    self.ids.status_label.text = message # Annahme: es gibt ein Label mit der id status_label
