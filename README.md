Create an alternating, monotonic timer:
```
timer = CycleTimer(callback)
seconds_off = timer.set_off(180)
seconds_on = timer.set_on(10)
timer.run()
# timer.cancel()
```
`callback(True)` will be called after `seconds_off`, and called with `False` after the `seconds_on`. The `seconds_off` timer is then reset. Rescheduling while running will take effect on the following cycle; to avoid this behavior call `cancel()`.
