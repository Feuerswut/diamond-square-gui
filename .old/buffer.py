from io import BytesIO

class BufferManager:
    def __init__(self):
        self.buffer = BytesIO()

    def get_buffer(self):
        return self.buffer

    def reset_buffer(self):
        self.buffer.seek(0)
        self.buffer.truncate(0)

# Create a global buffer manager instance
buffer_manager = BufferManager()