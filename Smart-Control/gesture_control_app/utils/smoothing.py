from collections import deque

class TemporalSmoother:
    def __init__(self, size=5):
        self.buffer = deque(maxlen=size)

    def stabilize(self, gesture):
        self.buffer.append(gesture)
        return max(set(self.buffer), key=self.buffer.count)
