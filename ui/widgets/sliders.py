import math
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label

class SliderWidget(BoxLayout):
    def __init__(self, setting_key, settings, min_value=0, max_value=100, font_size=16, integer=False, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.setting_key = setting_key
        self.settings = settings
        self.integer = integer

        self.label = Label(font_size=font_size)
        self.slider = Slider(min=min_value, max=max_value)
        self.slider.bind(value=self._on_value_change)

        self.add_widget(self.label)
        self.add_widget(self.slider)
        self._update_label(settings.get(setting_key, 0))

    def _on_value_change(self, instance, value):
        value = int(round(value)) if self.integer else value
        self._update_label(value)
        self._update_setting(value)

    def _update_label(self, value):
        self.label.text = f'{self.setting_key}: {value:.1f}'

    def _update_setting(self, value):
        self.settings.set(self.setting_key, value)

class ExponentialSliderWidget(SliderWidget):
    def __init__(self, setting_key, settings, min_value=0, max_value=10, **kwargs):
        super().__init__(setting_key, settings, min_value=min_value, max_value=max_value, **kwargs)
        self._update_label(self.settings.get(setting_key, 0))

    def _on_value_change(self, instance, value):
        exp_val = (2 ** int(round(value))) + 1
        self._update_label(exp_val)
        self._update_setting(exp_val)

    def _update_label(self, value):
        self.label.text = f'{self.setting_key}: {value}'