from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

# Funktion zum Speichern von 2D-Arrays als .txt-Dateien
def save_array_as_txt(array, filename):
    with open(filename, 'w') as f:
        for row in array:
            f.write(' '.join(f'{value:.4f}' for value in row) + '\n')

class SaveDialog(Popup):
    def __init__(self, resizable_widget=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Speichern unter..."
        self.size_hint = (0.8, 0.4)
        self.auto_dismiss = False
        self.resizable_widget = resizable_widget

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.filename_input = TextInput(hint_text="Dateiname eingeben", multiline=False)
        layout.add_widget(Label(text="Dateiname:"))
        layout.add_widget(self.filename_input)

        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        cancel_button = Button(text="Abbrechen", on_release=self.dismiss)
        save_button = Button(text="Speichern", on_release=self.save_and_close)
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(save_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def save_and_close(self, instance):
        filename = self.filename_input.text.strip()
        if filename and self.resizable_widget:
            try:
                array = self.resizable_widget.get_data()
                save_array_as_txt(array, filename + ".txt")
            except Exception as e:
                print("Fehler beim Speichern:", e)
        self.dismiss()

    @classmethod
    def open_save_dialog(cls, resizable_widget):
        dialog = cls(resizable_widget=resizable_widget)
        dialog.open()
