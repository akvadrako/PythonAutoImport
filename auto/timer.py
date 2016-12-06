
from threading import Thread, Semaphore, current_thread

class Timer:
    """Run `func` every `period` seconds until stopped."""
    def __init__(self, func, period):
    
        self.func = func
        self.period = period
        self.active = True
        self._thread = Thread(name=self, target=self._run)
        self._thread.start()

    def stop(self):
        self.active = False
        if current_thread() != self._thread:
            self._thread.join()

    def _run(self):
        from time import sleep
    
        while self.active:
            self.func()
            sleep(self.period)

    def __repr__(self):
        return 'Timer(%s, %s, %s)' % (self.func, self.period, self.active)


def test_timer():
    lock = Semaphore(0)
    count = [0]

    def func():
        count[0] += 1
        if count[0] == 3:
            lock.release()

    a = Timer(func, 0.001)
    lock.acquire()
    a.stop()

    assert count == [3]