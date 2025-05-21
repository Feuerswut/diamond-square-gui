import numpy as np
import threading

class Buffer:
    """A singleton, dynamically resizable buffer for NumPy arrays.
    Starts empty; only modifiable via append() and clear()."""
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.buffer = None
            self.write_index = 0
            self.dtype = None
            self.initialized = True

    def append(self, data):
        """Append data to the buffer. Initializes buffer if needed."""
        data = np.asarray(data)
        size = data.size

        # Initialize on first append
        if self.buffer is None:
            self.dtype = data.dtype
            self.buffer = np.empty(size, dtype=self.dtype)
            self.buffer[:size] = data
            self.write_index = size
            return

        if data.dtype != self.dtype:
            raise TypeError(f"Incompatible dtype: expected {self.dtype}, got {data.dtype}")

        required_size = self.write_index + size
        if required_size > self.buffer.size:
            # Resize
            new_size = max(required_size, self.buffer.size * 2)
            new_buffer = np.empty(new_size, dtype=self.dtype)
            new_buffer[:self.write_index] = self.buffer[:self.write_index]
            self.buffer = new_buffer

        self.buffer[self.write_index:self.write_index + size] = data
        self.write_index += size

    def get(self):
        """Get the written portion of the buffer."""
        if self.buffer is None:
            return np.array([], dtype=self.dtype or np.float32)
        return self.buffer[:self.write_index]

    def clear(self):
        """Reset buffer to initial empty state."""
        self.buffer = None
        self.write_index = 0
        self.dtype = None

buffer = Buffer()

# Example usage
if __name__ == "__main__":
    buf = Buffer()
    buf.append([1.0, 2.0, 3.0])
    print("Buffer contents:", buf.get())  # Output: [1. 2. 3.]

    buf.append([4.0, 5.0])
    print("Buffer contents:", buf.get())  # Output: [1. 2. 3. 4. 5.]

    buf.clear()
    print("After clear:", buf.get())      # Output: []
