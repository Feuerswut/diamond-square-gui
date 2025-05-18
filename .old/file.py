from plyer import filechooser, notification
import os

class FileHandler:
    @staticmethod
    def load(filters=None):
        """
        Opens a file dialog to load a file and returns its path and content.
        
        :param filters: A list of file filters to restrict the types of files shown.
                        Example: [("Text files", "*.txt")]
        :return: A tuple containing the file path and content, or (None, None) if no file was selected.
        """
        filters = filters if filters else [("All files", "*.*")]
        file_path = filechooser.open_file(title="Select a file to load", filters=filters)

        if file_path:  # filechooser returns a list
            file_path = file_path[0]
            # Ensure it's a valid file path and that the file exists
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    return file_path, content
                except FileNotFoundError:
                    FileHandler.show_error(f"File not found: {file_path}")
            else:
                FileHandler.show_error(f"Invalid file selected: {file_path}")
        
        return None, None

    @staticmethod
    def save(content, default_filename="untitled.txt", filters=None):
        """
        Opens a file dialog to save the provided content to a file.
        
        :param content: The text content to save to the file.
        :param default_filename: The default filename suggestion for saving.
        :param filters: A list of file filters for saving.
                        Example: [("Text files", "*.txt")]
        :return: The saved file path, or None if no file was saved.
        """
        filters = filters if filters else [("Text files", "*.txt")]
        file_path = filechooser.save_file(title="Save file as...", filters=filters, 
                                          filename=default_filename)

        if file_path:  # filechooser returns a list
            file_path = file_path[0]
            # Ensure that the directory exists where the file is being saved
            file_dir = os.path.dirname(file_path)
            if os.path.isdir(file_dir):
                try:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    return file_path
                except Exception as e:
                    FileHandler.show_error(f"Error saving file: {e}")
            else:
                FileHandler.show_error(f"Invalid directory: {file_dir}")
        
        return None

    @staticmethod
    def show_error(message):
        """
        Displays an error notification using Plyer's notification feature.
        
        :param message: The error message to display.
        """
        notification.notify(
            title="File Operation Error",
            message=message,
            app_name="FileHandler",
            timeout=5  # Notification disappears after 5 seconds
        )

# Example usage without GUI (can be called from anywhere in your code):
# Load a file
file_path, file_content = FileHandler.load(filters=[("Text files", "*.txt")])
if file_path:
    print(f"Loaded file: {file_path}")
    print(f"Content: {file_content}")

# Save a file
saved_path = FileHandler.save("This is the content to save.", default_filename="example.txt")
if saved_path:
    print(f"File saved at: {saved_path}")
