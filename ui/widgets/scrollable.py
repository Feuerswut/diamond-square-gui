from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp, sp

class ScrollableWidget(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = GridLayout(cols=1, spacing=sp(20), padding=dp(10), size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.add_widget(self.container)
        Window.bind(on_resize=self._on_resize)
        self._adjust_width()

    def _adjust_width(self):
        if Window.width > Window.height:
            self.container.width = min(Window.width * 0.3, dp(400))
        else:
            self.container.width = Window.width

    def _on_resize(self, window, w, h):
        self._adjust_width()