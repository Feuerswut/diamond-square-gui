from kivy.app import App

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout   import   BoxLayout
from kivy.uix.gridlayout  import  GridLayout
from kivy.uix.scrollview  import ScrollView

from kivy.uix.label         import Label
from kivy.uix.button        import Button
from kivy.uix.togglebutton  import ToggleButton
from kivy.uix.slider        import Slider
from kivy.uix.widget        import Widget
from kivy.uix.popup         import Popup
from kivy.uix.image         import Image

from kivy.core.window       import Window
from kivy.properties        import StringProperty, ObjectProperty
from kivy.metrics           import dp, sp # sp for fonts only
from kivy.utils             import platform
from kivy.clock             import Clock

from kivy.graphics          import Rectangle, Color
from kivy.graphics.texture  import Texture

import math
import threading

from generate   import generate
from plot       import plot         as pplot
from save       import SaveDialog #TODO

class ResizableSquareWidget(Widget):
    def __init__(self, texture, **kwargs):
        super(ResizableSquareWidget, self).__init__(**kwargs)
        self.texture = texture # Load Texture

        with self.canvas:
            Color(1, 1, 1, 1)  # Set the color to white
            self.rect = Rectangle(size=self.size, pos=self.pos, texture=self.texture)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        try:
            # Ensure the widget remains square by setting its size to the minimum of width and height
            side_length = min(self.parent.width, self.parent.height)
            self.size = (side_length, side_length)
            self.rect.size = self.size
            self.rect.pos = self.pos
        except Exception as e: # Update fails if Object does not exist.
            pass

    def update_texture(self, new_texture):
        """Method to update the texture of the widget."""
        self.texture = new_texture
        self.rect.texture = self.texture
        self.canvas.ask_update()

class SliderWidget(BoxLayout):
    def __init__(self, setting_key, settings, min_value=0, max_value=100, font_size=16, integer=False, **kwargs):
        super().__init__(**kwargs)

        self.setting_key = setting_key
        self.settings = settings
        self.integer = integer
        self.orientation = 'vertical'
        self.value(setting_key)

        # Create a label to display the current slider value
        self.label = Label(font_size=font_size)
        self.slider = Slider(min=min_value, max=max_value, value=self.value)

        # Add label and slider to the layout
        self.add_widget(self.label)
        self.add_widget(Widget(size_hint_y=None, height=1))  # Spacer
        self.add_widget(self.slider)

        # Bind the slider value change to update methods
        self.slider.bind(value=self.on_slider_value_change)
        
        # Initialize the label with the current slider value
        self.update_label(self.value)

    def value(self, key):
        self.value = self.settings.get(key, 0)

    def on_slider_value_change(self, instance, value):
        """Callback for slider value change."""
        value = int(round(value)) if self.integer else value
        self.update_label(value)
        self.update_setting(value)

    def update_label(self, value):
        """Update the label to reflect the current slider value."""
        self.label.text = f'{self.setting_key}: {value:.1f}'

    def update_setting(self, value):
        """Update the settings with the current value."""
        self.settings.set(self.setting_key, value)

class ErosionToggleWidget(BoxLayout):
    def __init__(self, setting_key, settings, font_size=16, **kwargs):
        super().__init__(**kwargs)

        self.setting_key = setting_key
        self.settings = settings
        self.orientation = 'vertical'

        # Initialize the toggle buttons based on current settings
        current_settings = self.settings.get(self.setting_key, [[False], [False]])
        self.thermal_toggle = ToggleButton(
            text='Thermal',
            state='down' if current_settings[0] else 'normal'
        )
        self.hydraulic_toggle = ToggleButton(
            text='Hydraulic',
            state='down' if current_settings[1] else 'normal'
        )

        # Bind toggle buttons to their callbacks
        self.thermal_toggle.bind(on_state=self.on_thermal_toggle)
        self.hydraulic_toggle.bind(on_state=self.on_hydraulic_toggle)

        # Add widgets to the layout
        self.add_widget(Label(text='Select Erosion Types'))
        self.add_widget(self.thermal_toggle)
        self.add_widget(self.hydraulic_toggle)

    def on_thermal_toggle(self, instance, value):
        self.update_settings()

    def on_hydraulic_toggle(self, instance, value):
        self.update_settings()

    def update_settings(self):
        thermal_state = self.thermal_toggle.state == 'down'
        hydraulic_state = self.hydraulic_toggle.state == 'down'
        self.settings.set(self.setting_key, [[thermal_state], [hydraulic_state]])

class ExponentialSliderWidget(SliderWidget):
    def __init__(self, setting_key, settings, min_value=0, max_value=10, **kwargs):
        super().__init__(setting_key, settings, min_value=min_value, max_value=max_value, **kwargs)
        self.update_label(self.settings.get(setting_key, 0))

    def value(self, key):
        self.value = int(
                math.log2(
                    (self.settings.get(key, 0) - 1)
                )
            )

    def on_slider_value_change(self, instance, value):
        """Override the method to apply 2^n + 1 transformation."""
        self.exponential_value = (2 ** int(round(value))) + 1
        self.update_label(self.exponential_value)
        self.update_setting(self.exponential_value)

    def update_label(self, value):
        """Override the label update to show the exponential value."""
        self.label.text = f'{self.setting_key}: {value}'

class ScrollableWidget(ScrollView):
    def __init__(self, **kwargs):
        super(ScrollableWidget, self).__init__(**kwargs)
        self.layout = GridLayout(
            cols=1,                     # One column layout
            spacing=sp(35),             # Spacing between sliders (in d. pixels)
            padding=[10, 20, 10, 10],   # Padding: [padding_left, padding_top, padding_right, padding_bottom]
            size_hint_y=None            # Required for scrolling
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
        self.update_width()

    def update_width(self):
        if Window.width > Window.height:
            # Desktop or Landscape mode
            self.layout.width = min(Window.width * 0.33, dp(400))
        else:
            # Mobile or Portrait mode
            self.layout.width = Window.width

    def on_window_resize(self, window, width, height):
        self.update_width()

class ActionButtons(GridLayout):
    def __init__(self, resizable_square, horizontal=False, **kwargs):
        if horizontal:
            kwargs['cols'] = 3
            kwargs['rows'] = 1
        else:
            kwargs['cols'] = 1
            kwargs['rows'] = 3

        super(ActionButtons, self).__init__(**kwargs)
        
        self.resizable_square = resizable_square

        # Add Buttons to the layout
        button1 = Button(text='Reset', size_hint=(1, 1))
        button2 = Button(text='Generate', size_hint=(1, 1))
        button3 = Button(text='Save', size_hint=(1, 1))

        # Bind actions to buttons
        button1.bind(on_press=self.reset_action)
        button2.bind(on_press=self.generate_action)
        button3.bind(on_press=self.save_action)
        
        # Add to layout
        self.add_widget(button1)
        self.add_widget(button2)
        self.add_widget(button3)

    def reset_action(self, instance):
        # TODO Implement reset action
        print("Reset button pressed")

    def generate_action(self, instance):
        # Start a new thread to run the generate function
        thread = threading.Thread(target=self.thread())
        thread.start()
    
    def thread(self):
        generate()

        # Set global flag to update
        from app import TerrainGeneratorApp
        app_instance = TerrainGeneratorApp.get_running_app()  # Get the running app instance
        app_instance.update_flags('FLAG_UPDATE_UI', True)

    def save_action(self, instance):
        SaveDialog.open_save_dialog(self)


class ContentPopup(BoxLayout):
    _content_added = False

    def __init__(self, content=[], auto_dismiss=False, close_button=False, **kwargs):
        super(ContentPopup, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # Initialize grid layout
        self.grid = GridLayout(cols=1)

        # Update content
        self.update_content(content)

        # Add close button if needed
        if close_button:
            self.add_close_button()

        # Add grid to the layout
        self.add_widget(self.grid)

    def update_content(self, content):
        # Clear existing widgets if needed
        self.grid.clear_widgets()

        # Add new content
        for each in content:
            if each.parent is None:  # Check if widget has no parent
                self.grid.add_widget(each)
            else:
                # Optionally, you could remove the widget from its current parent
                each.parent.remove_widget(each)
                self.grid.add_widget(each)

    def add_close_button(self):
        close_button = Button(text="Close", size_hint=(1, 0.1))
        if platform == 'android':
            close_button.size_hint_max_y = dp(80)
            close_button.size_hint_min_y = dp(60)
        else:
            close_button.size_hint_max_y = dp(50)
            close_button.size_hint_min_y = dp(40)

        close_button.bind(on_press=self.dismiss_popup)

        # Check if close button already exists before adding it
        if not any(isinstance(child, Button) and child.text == "Close" for child in self.grid.children):
            self.grid.add_widget(close_button)

    def dismiss_popup(self, *args):
        if hasattr(self, 'popup_instance'):
            self.popup_instance.dismiss()

    @staticmethod
    def open_dialog(
        parent, size_hint=(0.6, 0.86), title='Popup_Placeholder', 
        content=[], auto_dismiss=True, close_button=True
    ):
        # Create ContentPopup instance
        dialog_content = ContentPopup(content=content, close_button=close_button)

        # Create the Popup instance
        popup = Popup(
            content      = dialog_content,
            auto_dismiss = auto_dismiss,
            size_hint    = size_hint,
            title        = title
        )

        dialog_content.popup_instance = popup  # Assign the Popup instance to the dialog
        popup.open()

class SquareOptions(GridLayout):
    def __init__(self, resizable_square, content=[], **kwargs):
        kwargs['cols'] = 2
        kwargs['rows'] = 1

        super(SquareOptions, self).__init__(**kwargs)

        # Save to class obj
        self.resizable_square = resizable_square
        self.content          = content

        # Add Buttons to the layout
        button1 = Button(text="Options...", size_hint=(1, 1))
        button2 = Button(text='Generate', size_hint=(1, 1))

        # Bind actions
        button1.bind(on_press=self.options_action)
        button2.bind(on_press=self.generate_action)

        # Add to layout
        self.add_widget(button1)
        self.add_widget(button2)

    def generate_action(self, instance):
        generate()
        self.resizable_square.update_texture(pplot())

    def options_action(self, instance):
        ContentPopup.open_dialog(self, content=self.content, title='Generation Options')

class StringSelector(GridLayout):
    # The selected value, which will be bound to the settings key
    selected_value = StringProperty()

    def __init__(
        self, setting_key, settings, 
        options = ['fixed', 'periodic', 'clamped'], 
        font_size = sp(16), **kwargs
    ):
        
        kwargs['cols'] = len(options)
        kwargs['rows'] = 1

        super(StringSelector, self).__init__(**kwargs)
        
        self.setting_key = setting_key
        self.settings = settings
        self.button_ = {}

        # Create toggle buttons
        for i in options:
            self.button_[i] = ToggleButton(
                text=i, group='boundary_type', on_press=self.on_button_press,
                size_hint_min=[None, dp(20)], size_hint_max=[None, dp(40)], font_size=font_size
            )
            # Add buttons to layout
            self.add_widget(self.button_[i])
        
        # Set initial state based on the settings
        self.selected_value = self.settings.get(self.setting_key, 'fixed')
        if self.selected_value in self.button_:
            self.button_[self.selected_value].state = 'down'

        # Bind the property to update settings
        self.bind(selected_value=self.update_settings)
    
    def on_button_press(self, instance):
        # Update the selected value when a button is pressed
        self.selected_value = instance.text

    def update_settings(self, instance, value):
        # Update the settings dictionary with the new value
        self.settings.set(self.setting_key, value)
