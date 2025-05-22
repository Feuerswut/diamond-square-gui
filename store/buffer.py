import threading
import numpy as np

class DataBuffer:
    """Singleton buffer storing exactly one numpy array at a time.
    Raises an exception if an attempt is made to overwrite existing buffer.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.buffer = None  # stores the numpy array directly
            self.dtype = None
            self.shape = None
            self.initialized = True

    def store(self, data):
        """Store exactly one numpy array. Raises if buffer is occupied."""
        data = np.asarray(data)
        if self.buffer is not None:
            raise RuntimeError("Buffer already contains data. Clear before storing new array.")
        self.buffer = data
        self.dtype = data.dtype
        self.shape = data.shape

    def get(self):
        """Return the stored numpy array."""
        if self.buffer is None:
            raise RuntimeError("Buffer is empty.")
        return self.buffer

    def clear(self):
        """Clear the stored array."""
        self.buffer = None
        self.dtype = None
        self.shape = None

    def get_shape(self):
        """Get the shape of the stored array."""
        return self.shape

data_buffer = DataBuffer()
