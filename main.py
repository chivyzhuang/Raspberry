from driver.camera import Camera
from driver.collision import INDEX_COLLISION_FRONT
from driver.motor import ONE_METER_TICK_COUNT, ONE_CIRCLE_TICK_COUNT
from event_handler import *

camera = Camera('/home/pi/qrcode.jpg')
step_count = ONE_METER_TICK_COUNT / 6
final_step_count = ONE_METER_TICK_COUNT / 4
qua_circle_count = ONE_CIRCLE_TICK_COUNT / 36
angle_modify_count = 1

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


# ---------------------------- 2号算法 ----------------------------

_second_block_to_door_map = {
    b'Block-1': b'Door1',
    b'Block-2': b'Door2',
}
_second_after_enter_door_target_map = {
    b'Door1': [b'Door2', b'Wall-Right-1', b'Wall-Right-2'],
    b'Door2': [b'Door1', b'Wall-Left-1', b'Wall-Left-2'],
}
_second_after_enter_door_target = None

_second_init_catch_qr = [b'Block-1', b'Block-2']
_second_catch_qr = list(_second_init_catch_qr)

_second_found_qr = None
_second_final_forward = False
_second_target_door = None
_second_door_found = False


def _get_matched_qrcode(target, search_list):
    for i in target:
        if i in search_list:
            return i
    return None


def __second_handler(msg, args):
    global _second_found_qr, _second_catch_qr, _second_final_forward, _second_target_door, _second_door_found, \
        _second_after_enter_door_target, _second_after_enter_door_target_map
    print('found qr : %s, final forward : %s, target door : %s, door found : %s' %
          (str(_second_found_qr),
           str(_second_final_forward),
           str(_second_target_door),
           str(_second_door_found)))

    if msg == MAIN_MSG_START:
        print('main start')
        _camera_scan()
    elif msg == MAIN_MSG_CODE_DONE:
        left, center, right = args
        print(left, center, right)
        if _second_found_qr is None:
            # 小块还未找到
            _second_found_qr = _get_matched_qrcode(_second_catch_qr, center)
            if _second_found_qr is not None:
                _second_after_enter_door_target = None
                motor_thread.post(MOTOR_MSG_FORWARD, step_count / 2)
            elif _get_matched_qrcode(_second_catch_qr, right) is not None:
                _second_after_enter_door_target = None
                motor_thread.post(MOTOR_MSG_RIGHT, angle_modify_count)
            elif _get_matched_qrcode(_second_catch_qr, left) is not None:
                _second_after_enter_door_target = None
                motor_thread.post(MOTOR_MSG_LEFT, angle_modify_count)
            else:
                if _second_after_enter_door_target is not None:
                    tmp_codes = center + right + left
                    if _is_qrcode_in(_second_after_enter_door_target, tmp_codes):
                        _second_after_enter_door_target = None
                        motor.run(forward=True, count=final_step_count * 1.5)
                        _camera_scan()
                    else:
                        motor_thread.post(MOTOR_MSG_LEFT, qua_circle_count / 2)
                else:
                    motor_thread.post(MOTOR_MSG_LEFT, qua_circle_count / 2)
        else:
            # 小块已找到
            if _second_target_door is None:
                # 小块未捕获
                if _second_found_qr in left:
                    motor_thread.post(MOTOR_MSG_LEFT, angle_modify_count)
                elif _second_found_qr in right:
                    motor_thread.post(MOTOR_MSG_RIGHT, angle_modify_count)
                elif _second_found_qr in center:
                    motor_thread.post(MOTOR_MSG_FORWARD, step_count / 2)
                else:
                    motor_thread.post(MOTOR_MSG_FORWARD, final_step_count)
                    _second_final_forward = True
            else:
                # 小块已捕获
                if not _second_door_found:
                    # 门还未找到
                    if _second_target_door in center:
                        _second_door_found = True
                        motor_thread.post(MOTOR_MSG_FORWARD, step_count / 2)
                    elif _second_target_door in right:
                        motor_thread.post(MOTOR_MSG_RIGHT, angle_modify_count)
                    elif _second_target_door in left:
                        motor_thread.post(MOTOR_MSG_LEFT, angle_modify_count)
                    else:
                        motor_thread.post(MOTOR_MSG_LEFT, qua_circle_count / 2)
                else:
                    # 门已经找到
                    if _second_target_door in left:
                        motor_thread.post(MOTOR_MSG_LEFT, angle_modify_count)
                    elif _second_target_door in right:
                        motor_thread.post(MOTOR_MSG_RIGHT, angle_modify_count)
                    elif _second_target_door in center:
                        motor_thread.post(MOTOR_MSG_FORWARD, step_count / 2)
                    else:
                        motor_thread.post(MOTOR_MSG_FORWARD, ONE_METER_TICK_COUNT)
                        _second_final_forward = True

    elif msg == MAIN_MSG_COLLISION_HAPPEN:
        # 几号位发生碰撞
        index = args
        print('collision happen, index : %d' % index)
        if index == INDEX_COLLISION_FRONT:
            # 正对着找到的小块前进
            if _second_found_qr is not None:
                # 已经hold住小块
                if _second_target_door is not None:
                    return True
                _second_target_door = _second_block_to_door_map.get(_second_found_qr)
                MotorThread.cancel()

    elif msg == MAIN_MSG_COLLISION_DELETE:
        # 几号位碰撞取消
        index = args
        print('collision delete, index : %d' % index)
    elif msg == MAIN_MSG_MOTOR_DONE:
        motor_msg, run_count = args
        print('motor done, msg : %d, run count : %d' % (motor_msg, run_count))
        if _second_found_qr is not None:
            if _second_target_door is None:
                if _second_final_forward:
                    # 丢失小块
                    _second_found_qr = None
                    _second_final_forward = False
                    _second_target_door = None
                    _second_door_found = False

                    # 重新查找小块
                    _camera_scan()
                else:
                    # 继续朝小块前进
                    _camera_scan()
            else:
                # 向着门前进
                if _second_final_forward:
                    _second_after_enter_door_target = _second_after_enter_door_target_map.get(_second_target_door)
                    _second_final_forward = False
                    if _second_found_qr in _second_catch_qr:
                        _second_catch_qr.remove(_second_found_qr)
                    _second_found_qr = None
                    _second_target_door = None
                    _second_door_found = False

                    motor_thread.post(MOTOR_MSG_BACKWARD, final_step_count)
                    if len(_second_catch_qr) == 0:
                        main_queue.put(MAIN_MSG_QUIT)
                else:
                    # 继续朝门前进
                    _camera_scan()

        else:
            _camera_scan()

    elif msg == MAIN_MSG_MOTOR_CANCEL:
        motor_msg, run_count = args
        print('motor cancel, msg : %d, run count : %d' % (motor_msg, run_count))

        if _second_found_qr is not None and _second_target_door is not None:
            if _second_final_forward:
                _second_final_forward = False

            # 开始找门
            _camera_scan()

    elif msg == MAIN_MSG_QUIT:
        print('main quit')
        return False
    else:
        print('main unknown msg, msg : %d' % msg)

    return True


if __name__ == '__main__':
    # main_loop(_first_handler)
    main_loop(__second_handler)
