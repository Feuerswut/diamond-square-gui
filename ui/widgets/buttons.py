from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

class N_Buttons(GridLayout):
    _instances = {}  # maps id -> instance

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

    def __init__(self, button_data=None, **kwargs):
        # Avoid reinitialization
        if getattr(self, '_initialized', False):
            return

        # button_data should be a list of tuples: (button_name, button_action)
        if button_data is None:
            button_data = []

        super().__init__(cols=len(button_data), rows=1, **kwargs)

        for name, action in button_data:
            btn = Button(text=name)
            if callable(action):
                btn.bind(on_press=lambda instance, act=action: act())
            self.add_widget(btn)

        self._initialized = True

class ActionButtons(N_Buttons):
    def __init__(self, 
                 btn_1_name='Reset', btn_1_action=None, 
                 btn_2_name='Generate', btn_2_action=None, 
                 btn_3_name='Save', btn_3_action=None, 
                 **kwargs):
        
        from generate.main import generate_async as btn_2_action

        button_data = [
            (btn_1_name, btn_1_action),
            (btn_2_name, btn_2_action),
            (btn_3_name, btn_3_action)
        ]
        
        super().__init__(button_data=button_data, **kwargs)

class SquareOptions(N_Buttons):
    def __init__(self, opt_action=None, gen_action=None, **kwargs):
        button_data = [
            ('Options...', opt_action or (lambda: None)),
            ('Generate', gen_action or (lambda: None))
        ]
        super().__init__(button_data=button_data, **kwargs)
