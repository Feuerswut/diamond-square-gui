from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import dp
from kivy.properties import StringProperty

class StringSelector(GridLayout):
    selected = StringProperty()

    def __init__(self, setting_key, settings, options=None, **kwargs):
        options = options or ['fixed', 'periodic', 'clamped']
        super().__init__(cols=len(options), rows=1, **kwargs)
        self.setting_key = setting_key
        self.settings = settings
        self.buttons = {}
        for opt in options:
            btn = ToggleButton(text=opt, group=setting_key)
            btn.bind(on_press=self._on_select)
            self.buttons[opt] = btn
            self.add_widget(btn)
        init = self.settings.get(setting_key, options[0])
        self.selected = init
        if init in self.buttons:
            self.buttons[init].state = 'down'

    def _on_select(self, instance):
        self.selected = instance.text
        self.settings.set(self.setting_key, self.selected)