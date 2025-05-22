import os
from kivy.app import App
from kivy.lang import Builder

from ui.windows.root import RootWindow
from settings.store import settings

class DiamondSquareApp(App):
    kv_directory = os.path.join(os.path.dirname(__file__), "ui/windows")
    kv_file = "root.kv"

    def build(self):
        # Make settings accessible via app.settings in KV
        self.settings_store = settings
        return RootWindow()

    @property
    def settings(self):
        return self.settings_store
