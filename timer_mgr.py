"""Timer Manager
"""
import time
from sortedcontainers import SortedDict
from clock import Clock

def get_unique_id():
    """get_unique_id
    """
    uid = 0
    while True:
        uid += 1
        yield uid

GEN_UID = get_unique_id()
def get_next_uid():
    """get_next_uid
    """
    return next(GEN_UID)

class UniqueTime():
    """UniqueTime
    """
    def __init__(self, ts=None, uid=None, seconds_from_now=0):
        if not ts:
            ts = time.time()
        self.__timestamp = ts + seconds_from_now
        if not uid:
            uid = next(GEN_UID)
        self.__unique_id = uid

    def __eq__(self, other):
        return self.get_timestamp() == other.get_timestamp() and \
            self.get_unique_id() == other.get_unique_id()

    def __lt__(self, other):
        """__lt__
        """
        if self.__timestamp == other.get_timestamp():
            return self.__unique_id < other.get_unique_id()
        return self.__timestamp < other.get_timestamp()

    def __hash__(self):
        return hash((self.__timestamp, self.__unique_id))

    def get_timestamp(self):
        """get_timestamp
        """
        return self.__timestamp

    def get_unique_id(self):
        """get_unique_id
        """
        return self.__unique_id

    def __str__(self):
        return "ts={}, uid={}".format(self.__timestamp, self.__unique_id)

TR_OK = 0
TR_TOOMANY = 1
TR_NOTFOUND = 2

class TimerManager():
    """TimerManager
    """
    def __init__(self):
        self.__max_timers = 16 * 1000000
        self.__timers = SortedDict()

    def setup_timer(self, seconds_from_now, timer_data):
        """setup_timer\n
        param timer_data = ("app-spesific-timer-type", "app-spesific-id")\n
        return status, (timer-expiry-ts <float>, timer-unique-id <int>)\n
        """
        if len(self.__timers) > self.__max_timers:
            return TR_TOOMANY, ()

        unique_time = UniqueTime(seconds_from_now=seconds_from_now)
        self.__timers[unique_time] = timer_data
        return TR_OK, (unique_time.get_timestamp(), unique_time.get_unique_id())

    def cancel_timer(self, timer):
        """cancel_timer\n
        param timer = (ts <float>, unique-id <int>)\n
        """
        cancelled_timer = UniqueTime(ts=timer[0], uid=timer[1])
        try:
            del self.__timers[cancelled_timer]
        except KeyError:
            print("cancel_timer failed, ts={}, uid={}, cancelled_timer={}"\
                .format(timer[0], timer[1], cancelled_timer))
            return TR_NOTFOUND

        return TR_OK

    def poll_timer(self):
        """poll_timer
        """
        now = UniqueTime()
        # print("poll_timer, now: {}".format(now))
        if not self.__timers:
            return TR_NOTFOUND, ()
        first_timer = next(iter(self.__timers))
        if first_timer < now:
            try:
                timer_data = self.__timers.pop(first_timer)
            except KeyError:
                return TR_NOTFOUND, ()
            return TR_OK, timer_data
        return TR_NOTFOUND, ()

    def get_timers(self):
        """get_timers
        """
        return self.__timers

if __name__ == "__main__":
    NOW = UniqueTime(ts=time.time())
    NOW_TOO = UniqueTime(ts=NOW.get_timestamp(), uid=NOW.get_unique_id())
    time.sleep(1.0)
    LATER = UniqueTime(ts=time.time())
    print("now: {}, later: {}".format(NOW, LATER))
    if NOW == NOW_TOO:
        print("now is now")
    if NOW < LATER:
        print("now before later")

    TIMER_MANAGER = TimerManager()
    TIMEOUT_1 = 15
    TIMEOUT_2 = 3

    TIMER_MANAGER.setup_timer(TIMEOUT_1, ("timer-type-1", "id-1"))
    TIMER_MANAGER.setup_timer(TIMEOUT_2, ("timer-type-2", "id-1"))

    time.sleep(1.0)

    TIMER_MANAGER.setup_timer(TIMEOUT_1, ("timer-type-1", "id-2"))
    TIMER_MANAGER.setup_timer(TIMEOUT_2, ("timer-type-2", "id-2"))

    time.sleep(1.0)

    TIMER_MANAGER.setup_timer(TIMEOUT_1, ("timer-type-1", "id-3"))
    RETVAL, WILL_BE_CANCELLED_TIMER = TIMER_MANAGER.setup_timer(TIMEOUT_2, ("timer-type-2", "id-3"))
    print("this is cancelled: {}".format(WILL_BE_CANCELLED_TIMER))

    TIMER_MANAGER.cancel_timer((1000000.0000, 5))
    TIMER_MANAGER.cancel_timer(WILL_BE_CANCELLED_TIMER)

    for timer_i in TIMER_MANAGER.get_timers():
        print(timer_i)

    #print("start polling")
    #while TIMER_MANAGER.get_timers():
    #    RESULT, EXPIRED_TIMER = TIMER_MANAGER.poll_timer()
    #    if RESULT == TR_OK:
    #        print("expired: type={}, id={}".format(EXPIRED_TIMER[0], EXPIRED_TIMER[1]))
    #    time.sleep(1)
    #print("end polling")
    def poll_timer(args):
        """poll_timer
        """
        result, expired_timer = TIMER_MANAGER.poll_timer()
        if result == TR_OK:
            print("expired: type={}, id={}".format(expired_timer[0], expired_timer[1]))

    CLK = Clock(start=True, time_counter=int(time.perf_counter()), tick_callback=poll_timer)

    time.sleep(22.3)
    CLK.stop()
