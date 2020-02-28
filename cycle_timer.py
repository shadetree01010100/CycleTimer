import logging
import threading


class CycleTimer():

    """ Create an alternating, monotonic timer:

        ```
        timer = CycleTimer(callback)
        seconds_off = timer.set_off(180)
        seconds_on = timer.set_on(10)
        timer.run()
        # timer.cancel()
        ```

        `callback(True)` will be called after `seconds_off`, and called with
        `False` after the `seconds_on`. The `seconds_off` timer is then reset.
        Rescheduling while running will take effect on the following cycle;
        to avoid this behavior call `cancel()`.
    """

    def __init__(self, callback, name='CycleTimer'):
        """ Pass a method that accepts a single boolean type argument."""
        self.logger = logging.getLogger(name)
        self.callback = callback
        self.off_time = None
        self.on_time = None
        self.running = False
        self._kill = threading.Event()
        self._schedule_thread = None

    def cancel(self):
        self.running = False
        self._kill.set()
        self._schedule_thread.join()
        self._schedule_thread = None
        self.off_time = None
        self.on_time = None
        self.logger.info('Cancelled')

    def run(self):
        """ Run the schedule in another thread.

            Raises RuntimeError if interval and duration are not set.
        """
        if not (self.off_time and self.on_time):
            raise RuntimeError('call set_off() and set_on() before run()')
        self._kill.clear()
        self._schedule_thread = threading.Thread(target=self._loop)
        self._schedule_thread.start()
        self.running = True
        self.logger.info('Timer started')

    def set_on(self, seconds):
        """ Set time to run callback with `False` flag. If running, the
            next scheduled event will be run at its original time, and then
            rescheduled at this new time.
        """
        self.on_time = seconds
        self.logger.debug('ON time set to {} seconds'.format(self.on_time))
        if self.running:
            self.logger.warning('New setting will take effect next cycle')
        return self.on_time

    def set_off(self, seconds):
        """ Set time to run callback with `True` flag. If running, the
            next scheduled event will be run at its original time, and then
            rescheduled at this new time.
        """
        self.off_time = seconds
        self.logger.debug('OFF time set to {} seconds'.format(self.off_time))
        if self.running:
            self.logger.warning('New setting will take effect next cycle')
        return self.off_time

    def _loop(self):
        while not self._kill.is_set():
            if self._kill.wait(self.off_time):
                break
            self.logger.debug('Running callback with True flag')
            self.callback(True)
            if self._kill.wait(self.on_time):
                break
            self.logger.debug('Running callback with False flag')
            self.callback(False)
