"""ui_clock.py
Countdown clock widget (inherits Label)
"""
import time
from kivy.uix.label import Label
from kivy.clock import Clock as KivyClock
# from kivy.properties import BooleanProperty

class Clock(Label):
    """Clock\n
    start_time <int>
        Initial value for the clock
    kwargs
        Args for the kivy Label
    """
    def __init__(self, start_time, **kwargs):
        self.start_time = start_time
        if "font_size" not in kwargs:
            kwargs["font_size"] = 20
        if "bold" not in kwargs:
            kwargs["bold"] = True
        if "text" not in kwargs:
            kwargs["text"] = str(self.start_time)
        if "color" not in kwargs:
            kwargs["color"] = [1, 1, 1, 1]
        super(Clock, self).__init__(**kwargs)
        self.time_counter = 0
        self.stopped = False
        self.min_val = 0
        self.min_val_reached = None

    def tick(self, *args):
        """tick
        """
        if self.stopped:
            return
        new_time_counter = int(time.perf_counter())
        schedule_next = True
        if new_time_counter != self.time_counter:
            current_value = int(self.text)
            current_value -= 1
            if current_value == self.min_val:
                schedule_next = False
                if self.min_val_reached is not None:
                    print("ui_clock.Clock.tick, min val reached")
                    self.min_val_reached()
            self.text = str(current_value)
            self.time_counter = new_time_counter
            # print(self.text)
        if schedule_next:
            KivyClock.schedule_once(self.tick, 0.2)

    def init_time_counter(self):
        """First call of time_perf_counter
        """
        self.time_counter = int(time.perf_counter())

    def stop(self):
        """stop
        """
        self.stopped = True

    def get_current_value(self):
        """get_current_value
        """
        return int(self.text)

    def set_timeout_trigger(self, min_val_reached):
        """set_timeout_trigger
        param min_val_reached callback func
        """
        self.min_val_reached = min_val_reached

if __name__ == '__main__':
    from kivy.app import App
    from kivy.properties import BooleanProperty
    class TestApp(App):
        """TestApp for Clock
        """
        def __init__(self, **kwargs):
            super(TestApp, self).__init__(**kwargs)
            self.clock = Clock(10)
            self.clock.set_timeout_trigger(self.on_min_val_reached)

        def on_min_val_reached(self, *args):
            """on_timeout
            """
            print("on_timeout")

        def build(self):
            return self.clock
    app = TestApp()
    app.clock.tick()
    app.run()
