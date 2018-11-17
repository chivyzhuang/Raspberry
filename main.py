from driver.camera import Camera
from driver.collision import INDEX_COLLISION_FRONT
from driver.motor import ONE_METER_TICK_COUNT, ONE_CIRCLE_TICK_COUNT
from event_handler import *

camera = Camera('/home/pi/qrcode.jpg')
step_count = ONE_METER_TICK_COUNT / 6
final_step_count = ONE_METER_TICK_COUNT / 4
qua_circle_count = ONE_CIRCLE_TICK_COUNT / 36


# ---------------------------- 1号算法 ----------------------------

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

_first_catch_qr = None
_first_move_steps = 0
_first_final_forward = False
_first_turn_left_count = 0


def _camera_scan():
    main_queue.put((MAIN_MSG_CODE_DONE, camera.get_cur_qrcode_list()))


def _first_handler(msg, args):
    global _first_catch_qr, _first_final_forward, _first_turn_left_count, _first_move_steps
    print('catch qr : %s, final forward : %s, turn left count : %s, move steps : %s' %
          (str(_first_catch_qr),
           str(_first_final_forward),
           str(_first_turn_left_count),
           str(_first_move_steps)))

    if msg == MAIN_MSG_START:
        print('main start')

        _camera_scan()
    elif msg == MAIN_MSG_CODE_DONE:
        left, center, right = args
        print(left, center, right)
        if _first_catch_qr is None:
            if _is_qrcode_in(_first_alg_qrcode_list, center):
                _first_catch_qr = center
                motor_thread.post(MOTOR_MSG_FORWARD, step_count)
            else:
                motor_thread.post(MOTOR_MSG_LEFT, qua_circle_count)
        else:
            if _is_qrcode_in(_first_alg_qrcode_list, left):
                motor_thread.post(MOTOR_MSG_LEFT, qua_circle_count / 2)
            elif _is_qrcode_in(_first_alg_qrcode_list, right):
                motor_thread.post(MOTOR_MSG_RIGHT, qua_circle_count / 2)
            elif _is_qrcode_in(_first_alg_qrcode_list, center):
                motor_thread.post(MOTOR_MSG_FORWARD, step_count)
            else:
                motor_thread.post(MOTOR_MSG_FORWARD, final_step_count)
                _first_final_forward = True
    elif msg == MAIN_MSG_COLLISION_HAPPEN:
        # 几号位发生碰撞
        index = args
        print('collision happen, index : %d' % index)
        if index == INDEX_COLLISION_FRONT:
            if _first_catch_qr is not None:
                _remove_from(_first_catch_qr, _first_alg_qrcode_list)
                _first_catch_qr = None
                MotorThread.cancel()
    elif msg == MAIN_MSG_COLLISION_DELETE:
        # 几号位碰撞取消
        index = args
        print('collision delete, index : %d' % index)
    elif msg == MAIN_MSG_MOTOR_DONE:
        motor_msg, run_count = args
        print('motor done, msg : %d, run count : %d' % (motor_msg, run_count))

        if _first_catch_qr is not None:
            if motor_msg == MOTOR_MSG_FORWARD:
                _first_move_steps += step_count
            if _first_final_forward:
                _first_final_forward = False
                _remove_from(_first_catch_qr, _first_alg_qrcode_list)
                _first_catch_qr = None
                motor_thread.post(MOTOR_MSG_BACKWARD, _first_move_steps)
                _first_move_steps = 0
                if len(_first_alg_qrcode_list) == 0:
                    main_queue.put(MAIN_MSG_QUIT)
            else:
                _camera_scan()
        else:
            if motor_msg == MOTOR_MSG_LEFT:
                _first_turn_left_count += 1
                if _first_turn_left_count > ONE_CIRCLE_TICK_COUNT / qua_circle_count:
                    main_queue.put(MAIN_MSG_QUIT)
                    return True
            _camera_scan()
    elif msg == MAIN_MSG_MOTOR_CANCEL:
        motor_msg, run_count = args
        print('motor cancel, msg : %d, run count : %d' % (motor_msg, run_count))
        if _first_final_forward:
            _first_final_forward = False
        _first_move_steps += run_count
        motor_thread.post(MOTOR_MSG_BACKWARD, _first_move_steps)
        _first_move_steps = 0
        if len(_first_alg_qrcode_list) == 0:
            main_queue.put(MAIN_MSG_QUIT)

    elif msg == MAIN_MSG_QUIT:
        print('main quit')
        return False
    else:
        print('main unknown msg, msg : %d' % msg)

    return True


# ---------------------------- 1号算法 ----------------------------

def __second_handler(msg, args):
    if msg == MAIN_MSG_START:
        print('main start')
    elif msg == MAIN_MSG_COLLISION_HAPPEN:
        # 几号位发生碰撞
        index = args
        print('collision happen, index : %d' % index)
    elif msg == MAIN_MSG_COLLISION_DELETE:
        # 几号位碰撞取消
        index = args
        print('collision delete, index : %d' % index)
    elif msg == MAIN_MSG_MOTOR_DONE:
        motor_msg, run_count = args
        print('motor done, msg : %d, run count : %d' % (motor_msg, run_count))
    elif msg == MAIN_MSG_MOTOR_CANCEL:
        motor_msg, run_count = args
        print('motor cancel, msg : %d, run count : %d' % (motor_msg, run_count))
    elif msg == MAIN_MSG_QUIT:
        print('main quit')
        return False
    else:
        print('main unknown msg, msg : %d' % msg)


if __name__ == '__main__':
    main_loop(_first_handler)
    # main_loop(__second_handler)
