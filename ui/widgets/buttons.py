from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

class ActionButtons(GridLayout):
    _instances = {}  # maps id -> instance

    def __new__(cls, **kwargs):
        kivy_id = kwargs.get('id')
        if kivy_id and kivy_id in cls._instances:
            existing_instance = cls._instances[kivy_id]
            parent = existing_instance.parent
            if parent:
                parent.remove_widget(existing_instance)
            # Remove old instance from dict to replace it
            del cls._instances[kivy_id]

        instance = super().__new__(cls)
        if kivy_id:
            cls._instances[kivy_id] = instance
        return instance

    def __init__(self, **kwargs):
        if getattr(self, '_initialized', False):
            return
        super().__init__(cols=3, rows=1, **kwargs)

        btn_reset = Button(text='Reset')
        btn_gen = Button(text='Generate')
        btn_save = Button(text='Save')

        btn_reset.bind(on_press=lambda x: None)
        btn_gen.bind(on_press=lambda x: None)
        btn_save.bind(on_press=lambda x: None)

        self.add_widget(btn_reset)
        self.add_widget(btn_gen)
        self.add_widget(btn_save)

        self._initialized = True

class SquareOptions(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(cols=2, rows=1, **kwargs)
        opt_btn = Button(text='Options...')
        gen_btn = Button(text='Generate')
        opt_btn.bind(on_press=lambda x: None)
        gen_btn.bind(on_press=lambda x: None)
        self.add_widget(opt_btn)
        self.add_widget(gen_btn)