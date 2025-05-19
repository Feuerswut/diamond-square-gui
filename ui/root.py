import threading
from time import sleep

from kivy.clock import Clock
from kivy.properties import BooleanProperty
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout

import ui.widgets.__self__

class RootWindow(BoxLayout):
    is_mobile = BooleanProperty(False)
    MOBILE_WIDTH_THRESHOLD = 0  # px

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(size=self.on_window_resize)
        self.check_mobile(Window.size)

    def on_window_resize(self, instance, size):
        old_is_mobile = self.is_mobile
        self.check_mobile(size)
        if old_is_mobile != self.is_mobile:
            self.clear_canvas()

    def check_mobile(self, size):
        width, height = size
        self.is_mobile = width < self.MOBILE_WIDTH_THRESHOLD

    def clear_canvas(self):
        if hasattr(self.ids, 'canvas_widget'):
            self.ids.canvas_widget.canvas.clear()

    def generate_terrain(self):
        pass

    def save_image(self):
        pass

    def start_compute_task(self):
        self.ids.status_label.text = "Working..."
        threading.Thread(target=self.compute_task, daemon=True).start()

    def compute_task(self):
        result = None
        Clock.schedule_once(lambda dt: self.update_ui(result))

    def update_ui(self, result):
        self.ids.status_label.text = f"Task complete! Result: {result}"
