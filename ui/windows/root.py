# ui/root.py
import threading
from time import sleep
import os

from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.core.window import Window
Window.minimum_width  = 160 # minimum width in pixels
Window.minimum_height = 300 # minimum width in pixels

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.factory import Factory

import ui.widgets.__self__ # __init__.py in ui/widgets imports all custom widgets

class RootLayoutDesktop(BoxLayout):
    pass

class RootLayoutIntermediate(BoxLayout):
    pass

class RootLayoutMobile(BoxLayout):
    pass

# Register the new layout classes with the Factory
Factory.register('RootLayoutDesktop', cls=RootLayoutDesktop)
Factory.register('RootLayoutIntermediate', cls=RootLayoutIntermediate)
Factory.register('RootLayoutMobile', cls=RootLayoutMobile)

class RootWindow(BoxLayout):
    layout_mode = StringProperty('desktop') # 'desktop', 'intermediate', 'mobile'

    INTERMEDIATE_WIDTH_THRESHOLD    = 800 # dp
    MOBILE_WIDTH_THRESHOLD          = 300 # dp

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_all_kv()

        # Create instances of each layout
        self.layouts = {
            'desktop': RootLayoutDesktop(),
            'intermediate': RootLayoutIntermediate(),
            'mobile': RootLayoutMobile()
        }

        Window.bind(size=self.on_window_resize)
        # Schedule the initial layout check after initialization 
        # TODO: Update layout once after init with Kivy's factoryWindow.resize (or at the end of init)
        Clock.schedule_once(lambda dt: self.check_layout_mode(Window.size), 0)


    def _load_all_kv(self):
        """Loads all necessary KV files at the start."""
        kv_dir = os.path.join(os.path.dirname(__file__))
        layout_kv_files = ['desktop.kv', 'intermediate.kv', 'mobile.kv']

        for kv_file in layout_kv_files:
            path = os.path.join(kv_dir, kv_file)
            try:
                Builder.load_file(path)
                # print(f"Loaded KV: {kv_file}") # Debugging
            except Exception as e:
                print(f"Error loading initial KV file {path}: {e}")

    def on_window_resize(self, instance, size):
        old_layout_mode = self.layout_mode
        self.check_layout_mode(size)
        if old_layout_mode != self.layout_mode:
            self._update_layout()

    def check_layout_mode(self, size):
        width_dp = dp(size[0])
        if width_dp >= self.INTERMEDIATE_WIDTH_THRESHOLD:
            self.layout_mode = 'desktop'
        elif width_dp >= self.MOBILE_WIDTH_THRESHOLD:
            self.layout_mode = 'intermediate'
        else:
            self.layout_mode = 'mobile'

    def _update_layout(self):
        """Clears current widgets and adds the appropriate layout instance."""
        self.clear_widgets()
        current_layout_widget = self.layouts[self.layout_mode]
        self.add_widget(current_layout_widget)
        # print(f"Switched to layout: {self.layout_mode}") # Debugging

    def generate_terrain(self):
        pass

    def save_image(self):
        pass

    def start_compute_task(self, settings):
        current_layout_widget = self.layouts[self.layout_mode]
        status_label = current_layout_widget.ids.get('status_label')

        if status_label:
             status_label.text = "Working..."
        else:
             print(f"Warning: Status label not found to set 'Working...'.")

        threading.Thread(target=self.compute_task, args=(settings,), daemon=True).start()


    def compute_task(self, settings):
        print(f"Starting computation with settings: {settings}")
        sleep(2) # Simulate work
        result = "Computation Complete"
        Clock.schedule_once(lambda dt: True) # pass
