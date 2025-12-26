import time

class Later:
    def __init__(self):
        self.delay = 0.1

    def wait(self):
        time.sleep(self.delay)