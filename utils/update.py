from kivy.app import App
from kivy.clock import Clock

def find_widget_by_id(widget, target_id):
    if hasattr(widget, 'ids') and target_id in widget.ids:
        return widget.ids[target_id]

    for child in widget.children:
        result = find_widget_by_id(child, target_id)
        if result:
            return result

    return None

def update_widget(widget_id, method_name, **kwargs) -> bool:
    def _update(dt):
        try:
            app = App.get_running_app()
            widget = find_widget_by_id(app.root, widget_id)
            if widget is None:
                raise KeyError(f"Widget ID '{widget_id}' not found.")
            method = getattr(widget, method_name)
            method(**kwargs)
        except Exception as e:
            print(f"[update_widget] Error: {e}")
            return False

    # Schedule on the main thread
    Clock.schedule_once(_update)
    return True
