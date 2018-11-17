from driver.motor import ONE_CIRCLE_TICK_COUNT, ONE_METER_TICK_COUNT
from event_handler import *


def _handler(msg, args):
    if msg == MAIN_MSG_START:
        print('main start')
        motor_thread.post(MOTOR_MSG_FORWARD, ONE_METER_TICK_COUNT / 2)
        motor_thread.post(MOTOR_MSG_LEFT, ONE_CIRCLE_TICK_COUNT)
        motor_thread.post(MOTOR_MSG_RIGHT, ONE_CIRCLE_TICK_COUNT)
    elif msg == MAIN_MSG_COLLISION:
        # 几号位发生碰撞
        index = args
        print('collision, index : %d' % index)
    elif msg == MAIN_MSG_MOTOR_DONE:
        remaining_count = args
        print('motor done, remaining count : %d' % remaining_count)
    else:
        print('main unknown msg, msg : %d' % msg)


if __name__ == '__main__':
    main_loop(_handler)
