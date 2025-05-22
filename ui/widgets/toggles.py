from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from kivy.properties import ListProperty, ObjectProperty, StringProperty

class N_Toggle(GridLayout):
    setting_key = StringProperty('')
    settings = ObjectProperty(None)
    options = ListProperty([])

    def __init__(self, options=None, **kwargs):
        super().__init__(cols=0, rows=1, **kwargs)

        self.options = options or []
        self.buttons = {}

        self.bind(setting_key=self._sync_from_settings,
                  settings=self._sync_from_settings,
                  options=self._rebuild_buttons)

        self._rebuild_buttons()
        self._sync_from_settings()

    def _rebuild_buttons(self, *args):
        self.clear_widgets()
        self.cols = len(self.options)
        self.buttons = {}

        for opt in self.options:
            btn = ToggleButton(text=opt)
            btn.bind(state=self._on_toggle)
            self.buttons[opt] = btn
            self.add_widget(btn)

        self._sync_from_settings()

    def _sync_from_settings(self, *args):
        if not self.settings or not self.setting_key:
            return

        for opt, btn in self.buttons.items():
            # Use settings.get directly to check boolean flags
            btn.state = 'down' if self.settings.get(opt, False) else 'normal'

    def _on_toggle(self, instance, value):
        if not self.settings or not self.setting_key:
            return

        for opt, btn in self.buttons.items():
            self.settings.set(opt, btn.state == 'down')

class ErosionToggleWidget(N_Toggle):
    def __init__(self, **kwargs):
        super().__init__(options=['thermal', 'hydraulic'], **kwargs)
