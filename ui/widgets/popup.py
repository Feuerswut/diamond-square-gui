from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp

class ContentPopup(BoxLayout):
    def __init__(self, content=None, close_button=True, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.add_widget(self.grid)
        if content:
            for w in content:
                self.grid.add_widget(w)
        if close_button:
            btn = Button(text='Close', size_hint_y=None, height=dp(40))
            btn.bind(on_press=lambda x: self._popup.dismiss())
            self.add_widget(btn)

    def open(self, title='Dialog', size_hint=(0.6, 0.8)):
        self._popup = Popup(content=self, title=title, size_hint=size_hint)
        self._popup.open()