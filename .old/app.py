from kivy.app           import App
from kivy.core.window   import Window
from kivy.utils         import platform
from kivy.metrics       import dp, sp # sp for fonts only
from kivy.clock         import Clock

from widgets            import *
from settings           import settings
from content_general    import content  as content_general

class TerrainGeneratorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.FLAG_UPDATE_UI = False

    def update_flags(self, flag, value):
        if flag == 'FLAG_UPDATE_UI':
            self.FLAG_UPDATE_UI = value

    def build(self):
        # Bind the window resize event
        Window.bind(on_resize=self.on_window_resize)

        # Schedule the update_ui method to be called every
        Clock.schedule_interval(self.update_ui, 1.0 / 30.0)  # 30 FPS

        # Android features and permissions:
        if platform == 'android':
            self.apply_custom_dpi_scaling()
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

        # Create the main layout
        self.main_layout = GridLayout(cols=1, rows=1)

        # Create a FloatLayout to overlay widgets
        self.float_layout = FloatLayout()

        # Widget 1: Resizable Square
        self.resizable_square = ResizableSquareWidget(texture=None,size_hint=(None, None))

        # Widget 2: Scrollable Variant
        self.scrollable_widget = ScrollableWidget(size_hint=(1, None))
        self.scrollable_widget.layout.add_widget(Widget(size_hint_y=None, height=dp(0)))

        # Widget 2: Grid Variant
        self.grid_widget = GridLayout()
        self.grid_widget.cols = 1
        self.grid_widget.rows = 20

        # Widget 3: Action Buttons
        self.action_buttons = ActionButtons(
            resizable_square=self.resizable_square, 
            horizontal=False, size_hint=(1, None), 
            size_hint_max=(None, dp(40))
        )

        if platform == 'android':
            self.action_buttons.size[1]*=3

        self.action_buttons_horizontal = ActionButtons(
            resizable_square=self.resizable_square, 
            horizontal=True, height=dp(40), size_hint=(dp(40), None),
            size_hint_max=(None, dp(40))
        )

        # Options Button (Square layout)
        self.square_options = SquareOptions(
            resizable_square=self.resizable_square, 
            height=dp(40), size_hint=(dp(40), dp(180)),
            size_hint_max=(None, dp(50)),
            content=content_general()
        )

        # Set initial layout
        self.configure_layout(self.get_mode(Window.width, Window.height))

        return self.main_layout

    def content(self, **kwargs):
        return content_general(**kwargs)

    def get_mode(self, width, height):
        mode = None
        if width / height > 1.4: # Landscape
            mode = 'horizontal'
        elif width / height > 0.7: # Close to Square
            mode = 'square'
        else: # Portrait
            mode = 'vertical'
        return mode

    def default_horizontal(self, content=[]):
        # Setup main view
        self.main_layout.cols = 2
        self.main_layout.rows = 1

        # Setup grid widget + square
        self.main_layout.add_widget(self.grid_widget)
        self.main_layout.add_widget(self.resizable_square)

        # Add content
        for each in content:
            self.grid_widget.add_widget(each)

        self.grid_widget.add_widget(self.action_buttons)

    def horizontal_scrollable(self, content=[]):
        # Setup main view
        self.main_layout.cols = 2
        self.main_layout.rows = 1

        # Update scrollable widget size
        self.scrollable_widget.size_hint_y = None
        self.scrollable_widget.height = Window.height

        # Setup scrollable widget + square
        self.main_layout.add_widget(self.grid_widget)
        self.grid_widget.add_widget(self.scrollable_widget)
        self.main_layout.add_widget(self.resizable_square)
                
        # Add content to scrollable widget
        for each in content:
            self.scrollable_widget.layout.add_widget(each)

        self.scrollable_widget.layout.add_widget(self.action_buttons)

    def default_scrollable(self, content=[]):
        # Setup main view
        self.main_layout.cols = 1
        self.main_layout.rows = 3

        # Setup scrollable widget + square
        self.main_layout.add_widget(self.resizable_square)
        self.main_layout.add_widget(self.scrollable_widget)

        # Update scrollable widget size
        self.scrollable_widget.size_hint_y = None

        if platform == 'android':
            self.scrollable_widget.height = Window.height - self.resizable_square.height - dp(50)
        else:
            self.scrollable_widget.height = Window.height - self.resizable_square.height

        # Add content to scrollable widget
        for each in content:
            self.scrollable_widget.layout.add_widget(each)

        # Somehow this works better...
        self.scrollable_widget.layout.add_widget(self.action_buttons)

    def default_square(self, content=[]):
        # Setup main view
        self.main_layout.cols = 1
        self.main_layout.rows = 2

        # Set grid_widget size
        self.grid_widget.add_widget(self.resizable_square)

        self.main_layout.add_widget(self.grid_widget)
        self.main_layout.add_widget(self.square_options)

    def default_square_alt(self, content=[]):
        # Setup main view
        self.main_layout.cols = 3
        self.main_layout.rows = 3

        # Set grid_widget size
        self.grid_widget.height = self.main_layout.height * 2/3

        # Setup grid widget + square
        self.main_layout.add_widget(self.grid_widget)
        # self.main_layout.add_widget(self.resizable_square)

        # Add content
        for each in content:
            self.grid_widget.add_widget(each)

        self.grid_widget.add_widget(self.action_buttons)

    def configure_layout(self, mode):

        # Clear existing widgets
        self.main_layout.clear_widgets()
        self.grid_widget.clear_widgets()
        self.scrollable_widget.layout.clear_widgets()

        # Get content, mode and platform
        content = self.content()
        platform

        if platform == 'android':
            if mode == 'horizontal':
                self.default_scrollable(content)
            elif mode == 'vertical':
                self.default_scrollable(content)
            else:
                self.default_square(content)

        elif platform == 'win':
            if mode == 'horizontal':
                self.horizontal_scrollable(content)
            elif mode == 'vertical':
                self.default_scrollable(content)
            else:
                self.default_square(content)

        # elif platform == 'linux' or 'maxosx':
            pass

        else:
            if mode == 'horizontal':
                self.default_horizontal(content)
            elif mode == 'vertical':
                self.default_scrollable(content)
            else:
                self.default_square(content)

    def on_window_resize(self, window, width, height):
        # Reconfigure the layout when the window size changes
        self.configure_layout(self.get_mode(width, height))
    
    def update_ui(self, dt):
        # Ensure the resizable square widget is square and properly sized
        self.resizable_square.update_rect()

        try: 
            if self.FLAG_UPDATE_UI == True:
                self.resizable_square.update_texture(pplot())
                self.FLAG_UPDATE_UI = False
        except Exception as e:
            print(e)

    def apply_custom_dpi_scaling(self):
        # Get the actual DPI of the device
        current_dpi = Window.dpi
        print(f"Current DPI: {current_dpi}")

        # Define custom DPI buckets
        if current_dpi <= 160:  # MDPI
            scale_factor = 80 / current_dpi  # Target MDPI as 80 DPI
        elif current_dpi <= 240:  # HDPI
            scale_factor = 100 / current_dpi  # Target HDPI as 100 DPI
        else:  # Higher DPIs (XHDPI and above)
            scale_factor = 120 / current_dpi  # Max at 120 DPI

        # Adjust all metrics scaling using the scale factor
        dp_scale = lambda x: dp(x) * scale_factor
        sp_scale = lambda x: sp(x) * scale_factor

        # Update the dp and sp scaling globally in your app 
        # (you can also refactor to use dp_scale directly)
        self.dp = dp_scale
        self.sp = sp_scale
