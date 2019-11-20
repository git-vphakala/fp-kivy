"""
Clock module
"""
import time
from threading import Timer

class Clock():
    """Clock calls the callback once per second.\n
    The following kwargs are supported:\n
    start <boolean>
        Tells if the clock should start ticking
    tick_callback <func>
        This is called when a tick happens
    cb_args <list>
        Callback args
    time_counter <int>
        Initial value for time.
        Should be set (int(time.perf_counter())) if start is True.
    start_time <int>
    """
    KW_TIME_COUNTER = "time_counter"
    KW_START_TIME = "start_time"
    KW_TICK_CALLBACK = "tick_callback"
    KW_TICK_CALLBACK_ARGS = "cb_args"
    KW_START = "start"

    def __init__(self, **kwargs):
        # start=False, tick_callback=None, time_counter=0, start_time=200, cb_args=[]):
        if self.KW_TIME_COUNTER in kwargs:
            self.time_counter = kwargs[self.KW_TIME_COUNTER]
        else:
            self.time_counter = 0
        if self.KW_START_TIME in kwargs:
            self.start_time = kwargs[self.KW_START_TIME]
        else:
            self.start_time = 200
        self.stopped = False
        self.current_value = self.start_time
        self.interval = 0.1
        self.timer = Timer(self.interval, self.tick)
        if self.KW_TICK_CALLBACK in kwargs:
            self.tick_callback = kwargs[self.KW_TICK_CALLBACK]
        else:
            self.tick_callback = None
        if self.KW_TICK_CALLBACK_ARGS in kwargs:
            self.tick_callback_args = kwargs[self.KW_TICK_CALLBACK_ARGS]
        else:
            self.tick_callback_args = []
        if self.KW_START in kwargs and kwargs[self.KW_START]:
            print("start timer")
            self.timer.start()

    def tick(self):
        """
        tick
        """
        #sys.stdout.write(".")
        #sys.stdout.flush()
        if self.stopped:
            return
        new_time_counter = int(time.perf_counter())
        if new_time_counter != self.time_counter:
            self.current_value -= 1
            self.time_counter = new_time_counter
            if self.tick_callback is not None:
                self.tick_callback(self.current_value, *self.tick_callback_args)
        self.timer = Timer(self.interval, self.tick)
        self.timer.start()

    def init_time_counter(self):
        """
        First call of time_perf_counter
        """
        self.time_counter = int(time.perf_counter())

    def stop(self):
        """
        stop
        """
        self.stopped = True
        self.timer.cancel()

    def get_current_value(self):
        """
        get_current_value
        """
        return self.current_value

def print_time(current_time, timer_name):
    """
    test callback for Clock
    """
    print(timer_name, str(current_time))

if __name__ == '__main__':
    CLK = Clock(start=True, time_counter=int(time.perf_counter()), tick_callback=print_time,
                cb_args=["test-timer"], start_time=5)
    time.sleep(10.3)
    CLK.stop()
