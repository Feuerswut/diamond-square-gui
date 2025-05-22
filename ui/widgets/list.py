#TODO: WORK IN PROGRESS
# IS NOT IMPLEMENTED

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ObjectProperty, ListProperty


class ExpandablePresetList(BoxLayout):
    settings = ObjectProperty()
    setting_key = StringProperty()
    available_presets = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def open_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        self.toggle_buttons = {}
        current_values = [p[0] for p in self.settings.get(self.setting_key, [])]

        for preset in self.available_presets:
            btn = ToggleButton(text=preset, size_hint_y=None, height=40)
            if preset in current_values:
                btn.state = 'down'
            grid.add_widget(btn)
            self.toggle_buttons[preset] = btn

        scroll.add_widget(grid)
        content.add_widget(Label(text="Select Presets"))
        content.add_widget(scroll)

        btn_save = Button(text="Save", size_hint_y=None, height=50)
        btn_save.bind(on_press=lambda _: self.save_and_close(popup))
        content.add_widget(btn_save)

        popup = Popup(title=f"Edit {self.setting_key}", content=content,
                      size_hint=(None, None), size=(400, 400))
        popup.open()

    def save_and_close(self, popup):
        selected = [[name] for name, btn in self.toggle_buttons.items() if btn.state == 'down']
        self.settings.set(self.setting_key, selected)
        popup.dismiss()
