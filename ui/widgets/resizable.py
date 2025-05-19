from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty

class AspectRatioTextureWidget(Widget):
    _instances = {}  # map id -> widget instance

    texture = ObjectProperty(None, allownone=True)

    def __new__(cls, **kwargs):
        kivy_id = kwargs.get('id')
        if kivy_id and kivy_id in cls._instances:
            existing_instance = cls._instances[kivy_id]
            parent = existing_instance.parent
            if parent:
                parent.remove_widget(existing_instance)
            del cls._instances[kivy_id]

        instance = super().__new__(cls)
        if kivy_id:
            cls._instances[kivy_id] = instance
        return instance

    def __init__(self, texture=None, **kwargs):
        if getattr(self, '_initialized', False):
            return
        super().__init__(**kwargs)
        self.texture = texture or self._default_texture()
        self.rect = None

        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, texture=self.texture)

        self.bind(pos=self._update_rect, size=self._update_rect, texture=self._update_texture)
        self._initialized = True

    def _default_texture(self):
        tex = Texture.create(size=(1, 1), colorfmt='rgba')
        tex.blit_buffer(b'\xff\xff\xff\xff', colorfmt='rgba', bufferfmt='ubyte')
        tex.flip_vertical()
        return tex

    def _update_rect(self, *args):
        if not self.parent or not self.texture:
            return

        parent_width, parent_height = self.parent.size
        texture_ratio = self.texture.width / self.texture.height
        parent_ratio = parent_width / parent_height

        if texture_ratio > parent_ratio:
            width = parent_width
            height = width / texture_ratio
        else:
            height = parent_height
            width = height * texture_ratio

        x = self.parent.center_x - width / 2
        y = self.parent.center_y - height / 2

        self.rect.size = (width, height)
        self.rect.pos = (x, y)

    def _update_texture(self, *args):
        if self.rect:
            self.rect.texture = self.texture
            self.canvas.ask_update()

    def update_texture(self, new_texture):
        """Update the texture externally."""
        self.texture = new_texture
