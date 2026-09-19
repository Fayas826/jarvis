from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty

class SiriOrb(Widget):
    glow_radius = NumericProperty(80)
    glow_alpha  = NumericProperty(0.6)
    is_active   = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._pulse_anim = None
        self._angle = 0
        Clock.schedule_interval(self._rotate_tick, 1/30)
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y
        r  = self.glow_radius

        with self.canvas:
            for i, (col, alpha) in enumerate([
                ((0, 0.94, 1, 0.12), r + 40),
                ((0.66, 0.33, 0.97, 0.18), r + 25),
                ((0.93, 0.28, 0.6, 0.1), r + 12),
            ]):
                Color(*col[:3], col[3] * self.glow_alpha)
                d = alpha * 2
                Ellipse(pos=(cx - alpha, cy - alpha), size=(d, d))

            Color(0, 0.94, 1, 0.9 * self.glow_alpha)
            d = r * 2
            Ellipse(pos=(cx - r, cy - r), size=(d, d))
            Color(0.66, 0.33, 0.97, 0.7 * self.glow_alpha)
            r2 = r * 0.75
            Ellipse(pos=(cx - r2, cy - r2), size=(r2 * 2, r2 * 2))
            Color(0.93, 0.28, 0.6, 0.5 * self.glow_alpha)
            r3 = r * 0.45
            Ellipse(pos=(cx - r3, cy - r3), size=(r3 * 2, r3 * 2))
            Color(1, 1, 1, 0.8 * self.glow_alpha)
            r4 = r * 0.18
            Ellipse(pos=(cx - r4, cy - r4), size=(r4 * 2, r4 * 2))

    def _rotate_tick(self, dt):
        self._angle = (self._angle + 2) % 360
        if self.is_active: self._redraw()

    def activate(self):
        self.is_active = True
        if self._pulse_anim: self._pulse_anim.cancel(self)
        self._pulse_anim = (Animation(glow_radius=100, glow_alpha=1.0, duration=0.4) + Animation(glow_radius=85, glow_alpha=0.85, duration=0.5))
        self._pulse_anim.repeat = True
        self._pulse_anim.start(self)
        self._redraw()

    def deactivate(self):
        self.is_active = False
        if self._pulse_anim:
            self._pulse_anim.cancel(self)
            self._pulse_anim = None
        anim = Animation(glow_radius=80, glow_alpha=0.45, duration=0.6)
        anim.start(self)

    def on_glow_radius(self, *_): self._redraw()
    def on_glow_alpha(self, *_): self._redraw()
