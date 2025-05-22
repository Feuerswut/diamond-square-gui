from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, ObjectProperty, ListProperty

class N_Selector(GridLayout):
    setting_key = StringProperty()
    settings = ObjectProperty()
    options = ListProperty()
    selected = StringProperty()

    def __init__(self, options=None, setting_key="", settings=None, **kwargs):
        super().__init__(cols=0, rows=1, **kwargs)
        self.setting_key = setting_key
        self.settings = settings
        self.options = options or []

        self.bind(setting_key=self._rebuild_buttons,
                  settings=self._rebuild_buttons,
                  options=self._rebuild_buttons)

        self._rebuild_buttons()

    def _rebuild_buttons(self, *args):
        self.clear_widgets()
        self.cols = len(self.options)
        self.buttons = {}

        if not self.setting_key or not self.settings:
            return

        for opt in self.options:
            btn = ToggleButton(text=opt, group=self.setting_key)
            btn.bind(on_press=self._on_select)
            self.buttons[opt] = btn
            self.add_widget(btn)

        init = self.settings.get(self.setting_key, self.options[0] if self.options else "")
        self.selected = init
        if init in self.buttons:
            self.buttons[init].state = 'down'

    def _on_select(self, instance):
        self.selected = instance.text
        if self.settings and self.setting_key:
            self.settings.set(self.setting_key, self.selected)

class StringSelector(N_Selector):
    def __init__(self, **kwargs):
        super().__init__(
            options=['fixed', 'periodic', 'clamped'],
            **kwargs
        )
