from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label

class ErosionToggleWidget(BoxLayout):
    def __init__(self, setting_key, settings, font_size=16, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.setting_key = setting_key
        self.settings = settings

        current = self.settings.get(self.setting_key, [False, False])
        self.thermal = ToggleButton(text='Thermal', state='down' if current[0] else 'normal')
        self.hydraulic = ToggleButton(text='Hydraulic', state='down' if current[1] else 'normal')

        self.thermal.bind(on_state=self._on_toggle)
        self.hydraulic.bind(on_state=self._on_toggle)

        self.add_widget(Label(text='Erosion Types'))
        self.add_widget(self.thermal)
        self.add_widget(self.hydraulic)

    def _on_toggle(self, instance, value):
        self._update_settings()

    def _update_settings(self):
        t = self.thermal.state == 'down'
        h = self.hydraulic.state == 'down'
        self.settings.set(self.setting_key, [t, h])