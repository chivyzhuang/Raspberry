from driver.camera import Camera
from driver.motor import ONE_METER_TICK_COUNT, ONE_CIRCLE_TICK_COUNT
from event_handler import *

camera = Camera('/home/pi/qrcode.jpg')
step_count = ONE_METER_TICK_COUNT / 4
qua_circle_count = ONE_CIRCLE_TICK_COUNT / 36


def _is_qrcode_in(left, right):
    for i in left:
        if i in right:
            return True
    return False


def _remove_from(left: list, right: list):
    for i in left:
        if i in right:
            right.remove(i)


_first_alg_qrcode_list = [b'Block-1', b'Block-2']


def _first_handler(msg, args):
    if msg == MAIN_MSG_START:
        print('main start')

        # 20分算法
        count = 0
        hit_count = 0
        while count < 36:
            count += 1
            left, center, right = camera.get_cur_qrcode_list()
            print(left, center, right)
            if _is_qrcode_in(_first_alg_qrcode_list, center):
                catch_qr = center
                motor.run(True, step_count)
                steps = 1
                tmp_count = 3
                while tmp_count >= 0:
                    left, center, right = camera.get_cur_qrcode_list()
                    if _is_qrcode_in(_first_alg_qrcode_list, left):
                        motor.turn_left(qua_circle_count)
                    elif _is_qrcode_in(_first_alg_qrcode_list, left):
                        motor.turn_right(qua_circle_count)
                    elif _is_qrcode_in(_first_alg_qrcode_list, center):
                        motor.run(True, step_count)
                        tmp_count -= 1
                        steps += 1
                    else:
                        if collision_thread.has_collision():
                            break
                        motor.run(True, step_count)
                        motor.run(False, step_count)
                        break

                motor.run(False, step_count * steps)
                _remove_from(catch_qr, _first_alg_qrcode_list)
                hit_count += 1
                if hit_count == 2:
                    break

            motor.turn_left(qua_circle_count)

        # motor_thread.post(MOTOR_MSG_LEFT, ONE_CIRCLE_TICK_COUNT / 4)
        # motor_thread.post(MOTOR_MSG_RIGHT, ONE_CIRCLE_TICK_COUNT)

    elif msg == MAIN_MSG_COLLISION_HAPPEN:
        # 几号位发生碰撞
        index = args
        print('collision happen, index : %d' % index)
    elif msg == MAIN_MSG_COLLISION_DELETE:
        # 几号位发生碰撞
        index = args
        print('collision delete, index : %d' % index)
    elif msg == MAIN_MSG_MOTOR_DONE:
        remaining_count = args
        print('motor done, remaining count : %d' % remaining_count)
        # if remaining_count == 0:
        #     motor_thread.post(MOTOR_MSG_LEFT, ONE_CIRCLE_TICK_COUNT / 4)
    else:
        print('main unknown msg, msg : %d' % msg)


if __name__ == '__main__':
    main_loop(_first_handler)
    # main_loop(None)
