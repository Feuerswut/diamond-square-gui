from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label

from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty
from kivy.metrics import dp

class N_Toggle(GridLayout):
    setting_key = StringProperty('')
    settings = ObjectProperty(None)
    options = ListProperty([])
    font_size = NumericProperty(16)

    def __init__(self, options=None, **kwargs):
        super().__init__(cols=0, rows=1, size_hint_y=None, height=dp(50), **kwargs)

        self.options = options or []
        self.buttons = {}

        self.bind(setting_key=self._sync_from_settings,
                  settings=self._sync_from_settings,
                  options=self._rebuild_buttons)

        self._rebuild_buttons()

    def _rebuild_buttons(self, *args):
        self.clear_widgets()
        self.cols = len(self.options)
        self.buttons = {}

        for opt in self.options:
            btn = ToggleButton(text=opt, font_size=self.font_size)
            btn.bind(on_state=self._on_toggle)
            self.buttons[opt] = btn
            self.add_widget(btn)

        self._sync_from_settings()

    def _sync_from_settings(self, *args):
        if not self.settings or not self.setting_key:
            return

        current_states = self.settings.get(self.setting_key, [False] * len(self.options))
        for i, opt in enumerate(self.options):
            btn = self.buttons.get(opt)
            if btn:
                btn.state = 'down' if i < len(current_states) and current_states[i] else 'normal'

    def _on_toggle(self, instance, value):
        if not self.settings or not self.setting_key:
            return

        states = [self.buttons[opt].state == 'down' for opt in self.options]
        self.settings.set(self.setting_key, states)


class ErosionToggleWidget(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(cols=2, size_hint_y=None, height=dp(50), **kwargs)

        self.label = Label(text='Erosion Types')
        self.toggle_group = N_Toggle(options=['Thermal', 'Hydraulic'], **kwargs)

        self.add_widget(self.label)
        self.add_widget(self.toggle_group)

        # Optional: bind label font size to toggle font size for consistency
        self.toggle_group.bind(font_size=lambda instance, value: setattr(self.label, 'font_size', value))
