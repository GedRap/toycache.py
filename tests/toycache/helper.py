"""
Reusable helper methods and classes for testing
"""


class Timer(object):
    def __init__(self):
        self.time = 0

    def __call__(self):
        return self.time

    def tick(self):
        self.time += 1