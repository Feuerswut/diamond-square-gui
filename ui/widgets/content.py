from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.uix.popup import Popup
from kivy.clock import Clock

import ui.widgets.sliders, ui.widgets.selectors, ui.widgets.toggles
from settings.store import settings

import os
kv_dir = os.path.join(os.path.dirname(__file__))
KV_PATH = os.path.join(kv_dir, "content.kv")
Builder.load_file(KV_PATH)

class ContentWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.populate())

    def populate(self):
        # Adding the dynamic widgets based on the settings
        self.ids.initial_terrain_slider.setting_key = 'initial_terrain'
        self.ids.roughness_float_slider.setting_key = 'roughness_float'
        self.ids.boundary_type_selector.setting_key = 'boundary_type'
        self.ids.erosion_toggle.setting_key = 'erosion'

        # Set values dynamically for the sliders (you can adjust this as needed)
        self.ids.initial_terrain_slider.set_value(settings.get('initial_terrain', 129))
        self.ids.roughness_float_slider.set_value(settings.get('roughness_float', 0.7))

        # Initialize the edge sliders
        for i in range(4):
            self.ids[f'initial_edges_{i}_slider'].setting_key = f'initial_edges_{i}'
            self.ids[f'initial_edges_{i}_slider'].set_value(settings.get(f'initial_edges_{i}', 2.0))

class ContentPopup(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._popup = None

    def open(self, title='Dialog', size_hint=(0.6, 0.8)):
        self._popup = Popup(title=title, content=self, size_hint=size_hint)
        self._popup.open()

    def dismiss_popup(self):
        if self._popup:
            self._popup.dismiss()
