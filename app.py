import os
from kivy.app import App
from kivy.lang import Builder

from ui.root import RootWindow

class DiamondSquareApp(App):
    # load kv files
    kv_directory = os.path.join(os.path.dirname(__file__), "..", "ui")
    kv_file = "ui/root.kv"

    def build(self):
        return RootWindow()
