import numpy as np
import threading

class Buffer:
    """Singleton, dynamically resizable buffer that supports 1D and n-D array appending separately."""
    
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
            self.nd_shapes = []  # For storing shapes of appended nd-arrays
            self.initialized = True

    def append(self, data):
        """Append 1D data to the buffer."""
        data = np.asarray(data).ravel()  # ensure 1D
        size = data.size

        if self.buffer is None:
            self.dtype = data.dtype
            self.buffer = np.empty(size, dtype=self.dtype)
            self.buffer[:size] = data
            self.write_index = size
            return

        if data.dtype != self.dtype:
            raise TypeError(f"Incompatible dtype: expected {self.dtype}, got {data.dtype}")

        self._resize_if_needed(size)
        self.buffer[self.write_index:self.write_index + size] = data
        self.write_index += size

    def appendnd(self, data):
        """Append n-D data (stored flattened) to the buffer and store its shape."""
        data = np.asarray(data)
        flat_data = data.ravel()
        size = flat_data.size

        if self.buffer is None:
            self.dtype = flat_data.dtype
            self.buffer = np.empty(size, dtype=self.dtype)
            self.buffer[:size] = flat_data
            self.write_index = size
        else:
            if flat_data.dtype != self.dtype:
                raise TypeError(f"Incompatible dtype: expected {self.dtype}, got {flat_data.dtype}")
            self._resize_if_needed(size)
            self.buffer[self.write_index:self.write_index + size] = flat_data
            self.write_index += size

        self.nd_shapes.append(data.shape)

    def _resize_if_needed(self, additional_size):
        """Resize the buffer if required to fit new data."""
        required_size = self.write_index + additional_size
        if required_size > self.buffer.size:
            new_size = max(required_size, self.buffer.size * 2)
            new_buffer = np.empty(new_size, dtype=self.dtype)
            new_buffer[:self.write_index] = self.buffer[:self.write_index]
            self.buffer = new_buffer

    def get(self):
        """Get the current 1D buffer contents."""
        if self.buffer is None:
            return np.array([], dtype=self.dtype or np.float32)
        return self.buffer[:self.write_index]

    def getnd_shapes(self):
        """Return stored shapes of all n-D arrays added with appendnd()."""
        return self.nd_shapes

    def clear(self):
        """Reset buffer to initial empty state."""
        self.buffer = None
        self.write_index = 0
        self.dtype = None
        self.nd_shapes = []

buffer = Buffer()

# Example usage
if __name__ == "__main__":
    buf = Buffer()
    buf.append([1, 2, 3])
    buf.append([4, 5])

    terrain = np.random.rand(127, 127)
    buf.appendnd(terrain)

    print("1D buffer contents:", buf.get())
    print("Stored n-D shapes:", buf.getnd_shapes())
