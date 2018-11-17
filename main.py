from driver.motor import turn_left, ONE_CIRCLE_TICK_COUNT, turn_right, ONE_METER_TICK_COUNT

run(forward=True, count=ONE_METER_TICK_COUNT)
turn_left(count=ONE_CIRCLE_TICK_COUNT)
turn_right(count=ONE_CIRCLE_TICK_COUNT)
