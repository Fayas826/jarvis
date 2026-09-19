from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.properties import ListProperty, BooleanProperty
import math

class WaveBars(Widget):
    heights = ListProperty([0.2, 0.4, 0.7, 0.5, 0.9, 0.6, 0.3])
    active  = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._t = 0
        Clock.schedule_interval(self._tick, 1/20)
        self.bind(pos=self._draw, size=self._draw)

    def _tick(self, dt):
        if self.active:
            self._t += dt
            self.heights = [0.3 + 0.65 * abs(math.sin(self._t * 3.2 + i * 0.7)) for i in range(7)]
        else:
            self.heights = [0.15] * 7
        self._draw()

    def _draw(self, *_):
        self.canvas.clear()
        n = len(self.heights)
        total_w = self.width
        bar_w = max(4, total_w / (n * 1.8))
        gap   = (total_w - bar_w * n) / (n + 1)

        with self.canvas:
            for i, h in enumerate(self.heights):
                bh = self.height * h
                x  = self.x + gap * (i + 1) + bar_w * i
                y  = self.center_y - bh / 2
                t = i / max(n - 1, 1)
                Color(0 + t * 0.66, 0.94 - t * 0.61, 1 - t * 0.03, 0.9)
                RoundedRectangle(pos=(x, y), size=(bar_w, bh), radius=[bar_w / 2])
