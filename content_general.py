from kivy.metrics   import dp, sp # sp for fonts only
from kivy.utils     import platform

from widgets        import *
from settings       import settings

def content():
    """
    :return: widget list
    """

    # Global slider options:
    height = dp(80)
    font_s = sp(16)

    button_height = height // 2

    # Slider 1: 'initial_terrain' INTEGER(2^n+1) default 129
    slider_widget01 = ExponentialSliderWidget(
        setting_key='initial_terrain', settings=settings, min_value=3, max_value=12, 
        integer=True, size_hint_y=None, height=height, font_size=font_s
    )

    # Slider 2: 'roughness_float' (0.000-1.000) default 0.7
    slider_widget02 = SliderWidget(
        setting_key='roughness_float', settings=settings, min_value=0.000, max_value=1.000, 
        size_hint_y=None, height=height, font_size=font_s
    )

    # Selectable Options 1: 'boundary_type' (fixed; periodic; ...)
    selector_label = Label(text="boundary_condition:", size_hint_max_y=font_s-dp(50))

    selector = StringSelector(
        setting_key='boundary_type', settings=settings, font_size=font_s,
        size_hint_min = [None,button_height-dp(10)], size_hint_max = [None,button_height],
    )
    
    # Sliders 3 (a-d): 'initial_edges', each (0.0 - 5.0) default 2.0
    slider_grid_widget = GridLayout(
        cols=2,
        rows=2,
        size_hint_y=None
    )

    for i in range(4):
        slider = SliderWidget(
            setting_key=f'initial_edges_{i}', settings=settings, min_value=0, max_value=5, 
            font_size=14, size_hint_y=None, height=70 # Intentional static size
        )
        slider_grid_widget.add_widget(slider)

    # Advanced Erosion/Smoothing
    erosion = ErosionToggleWidget(
        setting_key='erosion', settings=settings, font_size=font_s,
        size_hint_min = [None, 2.5*button_height], size_hint_max = [None, 4*button_height],
    )

    # Bundle all sliders in a list
    return [
        slider_widget01,
        slider_widget02,
        selector_label, selector,
        slider_grid_widget,
        Widget(size_hint_min = [None,dp(0)], size_hint_max = [None,None]),
        erosion
        # ...
    ]
