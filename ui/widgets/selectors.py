from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, ObjectProperty, ListProperty

class StringSelector(GridLayout):
    setting_key = StringProperty()
    settings = ObjectProperty()
    options = ListProperty(['fixed', 'periodic', 'clamped'])
    selected = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(cols=0, rows=1, **kwargs)
        # We can't create buttons here yet because setting_key or settings might not be set
        self.bind(setting_key=self._rebuild_buttons,
                  settings=self._rebuild_buttons,
                  options=self._rebuild_buttons)

    def _rebuild_buttons(self, *args):
        # Clear existing buttons/widgets if any
        self.clear_widgets()
        self.cols = len(self.options)
        self.buttons = {}
        if not self.setting_key or not self.settings:
            return  # Wait until both are set

        for opt in self.options:
            btn = ToggleButton(text=opt, group=self.setting_key)
            btn.bind(on_press=self._on_select)
            self.buttons[opt] = btn
            self.add_widget(btn)

        init = self.settings.get(self.setting_key, self.options[0])
        self.selected = init
        if init in self.buttons:
            self.buttons[init].state = 'down'

    def _on_select(self, instance):
        self.selected = instance.text
        if self.settings and self.setting_key:
            self.settings.set(self.setting_key, self.selected)
