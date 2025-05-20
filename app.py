import os
from kivy.app import App
from kivy.lang import Builder

from ui.root import RootWindow

class DiamondSquareApp(App):
    kv_directory = os.path.join(os.path.dirname(__file__), "ui") # Point to ui folder
    kv_file = "root.kv" # Point to the main root.kv

    def build(self):
        return RootWindow()