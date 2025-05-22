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

    def _rebuild_buttons(self, *args):
        self.clear_widgets()
        self.cols = len(self.options)
        self.buttons = {}

        for opt in self.options:
            btn = ToggleButton(text=opt)
            btn.bind(on_state=self._on_toggle)
            self.buttons[opt] = btn
            self.add_widget(btn)

        self._sync_from_settings()

    def _sync_from_settings(self, *args):
        if not self.settings or not self.setting_key:
            return

        # Get the list of active options from settings
        active_items = [item[0] for item in self.settings.get(self.setting_key, [])]
        for opt, btn in self.buttons.items():
            btn.state = 'down' if opt in active_items else 'normal'

    def _on_toggle(self, instance, value):
        print(f"_on_toggle called with: {instance.text}, value={value}")
        if not self.settings or not self.setting_key:
            print("No settings or setting_key, skipping set")
            return
        print(f"Calling settings.set with key={self.setting_key}")
        active_items = [[opt] for opt, btn in self.buttons.items() if btn.state == 'down']
        self.settings.set(self.setting_key, active_items)

class ErosionToggleWidget(GridLayout):
    setting_key = StringProperty()
    settings = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(cols=1, size_hint_y=None, **kwargs)
        self.label = Label(text='Erosion Types')
        self.add_widget(self.label)

        # Create toggle_group but don't set properties yet
        self.toggle_group = N_Toggle(options=['thermal', 'hydraulic'])
        self.add_widget(self.toggle_group)

        # Bind properties so N_Toggle updates when they change
        self.bind(setting_key=self._update_toggle_settings,
                  settings=self._update_toggle_settings)

    def _update_toggle_settings(self, *args):
        self.toggle_group.setting_key = self.setting_key
        self.toggle_group.settings = self.settings
