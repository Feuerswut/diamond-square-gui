from concurrent.futures import ThreadPoolExecutor
from kivy.clock import Clock, mainthread

class AsyncManager:
    def __init__(self, max_workers=1):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def run_async(self, func, *args, callback=None, **kwargs):
        future = self.executor.submit(func, *args, **kwargs)
        if callback:
            future.add_done_callback(lambda f: self._schedule_callback(callback, f.result()))
        return future

    @mainthread # Stellt sicher, dass der Callback im Hauptthread ausgeführt wird
    def _schedule_callback(self, callback, result):
        callback(result)

    def shutdown(self):
        self.executor.shutdown(wait=True)
