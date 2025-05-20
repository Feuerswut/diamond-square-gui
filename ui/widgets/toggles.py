from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty, NumericProperty

class ErosionToggleWidget(BoxLayout):
    setting_key = StringProperty('')
    settings = ObjectProperty(None)
    font_size = NumericProperty(16)

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.label = Label(text='Erosion Types', font_size=self.font_size)
        self.thermal = ToggleButton(text='Thermal')
        self.hydraulic = ToggleButton(text='Hydraulic')

        self.thermal.bind(on_state=self._on_toggle)
        self.hydraulic.bind(on_state=self._on_toggle)

        self.add_widget(self.label)
        self.add_widget(self.thermal)
        self.add_widget(self.hydraulic)

        self.bind(setting_key=self._update_from_settings,
                  settings=self._update_from_settings)

    def _update_from_settings(self, *args):
        if not self.settings or not self.setting_key:
            return
        current = self.settings.get(self.setting_key, [False, False])
        self.thermal.state = 'down' if current[0] else 'normal'
        self.hydraulic.state = 'down' if current[1] else 'normal'

    def _on_toggle(self, instance, value):
        if self.settings and self.setting_key:
            t = self.thermal.state == 'down'
            h = self.hydraulic.state == 'down'
            self.settings.set(self.setting_key, [t, h])
