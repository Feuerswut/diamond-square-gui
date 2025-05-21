from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty
import math

class SliderWidget(BoxLayout):
    setting_key = StringProperty('')
    settings = ObjectProperty(None)
    min_value = NumericProperty(0)
    max_value = NumericProperty(100)
    integer = BooleanProperty(False)
    font_size = NumericProperty(16)

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.label = Label(font_size=self.font_size)
        self.slider = Slider(min=self.min_value, max=self.max_value)
        self.slider.bind(value=self._on_value_change)
        self.add_widget(self.label)
        self.add_widget(self.slider)

        # Update slider and label once properties are set
        self.bind(setting_key=self._update_from_settings,
                  settings=self._update_from_settings,
                  min_value=self._update_slider_range,
                  max_value=self._update_slider_range)

    def _update_slider_range(self, *args):
        self.slider.min = self.min_value
        self.slider.max = self.max_value

    def _update_from_settings(self, *args):
        if not self.settings or not self.setting_key:
            return
        value = self.settings.get(self.setting_key, self.min_value)
        if self.integer:
            value = int(value)
        self.set_value(value)

    def _on_value_change(self, instance, value):
        value = int(round(value)) if self.integer else value
        self._update_label(value)
        if self.settings and self.setting_key:
            self.settings.set(self.setting_key, value)

    def _update_label(self, value):
        self.label.text = f'{self.setting_key}: {value:.1f}'

    def set_value(self, value):
        # Update slider value and label
        self.slider.value = value
        self._update_label(value)

class IntegerSliderWidget(SliderWidget):
    def set_value(self, value):
        self.slider.value = value
        self._update_label(value)

    def _on_value_change(self, instance, value):
        int_value = int(round(value))
        self._update_label(int_value)
        if self.settings and self.setting_key:
            self.settings.set(self.setting_key, int_value)

    def _update_label(self, value):
        self.label.text = f'{self.setting_key}: {value}'

class ExponentialSliderWidget(IntegerSliderWidget):
    def set_value(self, value):
        # Convert real value to slider value using log2 scale
        slider_val = math.log2(value + 1)
        self.slider.value = slider_val
        self._update_label(value)

    def _on_value_change(self, instance, value):
        # Convert slider value to exponential scale and subtract 1
        exp_val = (2 ** int(round(value))) - 1
        self._update_label(exp_val)
        if self.settings and self.setting_key:
            self.settings.set(self.setting_key, exp_val)
