import RPi.GPIO as GPIO
from gpiozero import OutputDevice, DigitalInputDevice

ONE_METER_TICK_COUNT = 192
ONE_CIRCLE_TICK_COUNT = 160

_std_by = OutputDevice(11)
_std_by.on()

_frequency = 200
_left_run_init_dc = 70
_right_run_init_dc = 72
_left_turn_init_dc = 50
_right_turn_init_dc = 52

_left_pwm_channel = 0
GPIO.setup(_left_pwm_channel, GPIO.OUT)
_left_pwn = GPIO.PWM(_left_pwm_channel, _frequency)
_left_in1 = OutputDevice(5)
_left_in2 = OutputDevice(6)
_left_running = False
left_digital = DigitalInputDevice(14)

_right_pwn_channel = 26
GPIO.setup(_right_pwn_channel, GPIO.OUT)
_right_pwn = GPIO.PWM(_right_pwn_channel, _frequency)
_right_in1 = OutputDevice(19)
_right_in2 = OutputDevice(13)
_right_running = False
right_digital = DigitalInputDevice(21)

_cancel_flag = False


def set_cancel_flag():
    global _cancel_flag
    _cancel_flag = True


def left_stop():
    _left_in1.off()
    _left_in2.off()
    _left_pwn.stop()
    global _left_running
    _left_running = False


def left_run(forward: bool = True, dc=100):
    if dc > 100:
        dc = 100

    global _left_running
    if _left_running:
        _left_pwn.ChangeDutyCycle(dc)
    else:
        _left_pwn.start(dc)
    if forward:
        _left_in1.off()
        _left_in2.on()
    else:
        _left_in1.on()
        _left_in2.off()


def right_stop():
    _right_in1.off()
    _right_in2.off()
    _right_pwn.stop()
    global _right_running
    _right_running = False


def right_run(forward: bool = True, dc=100):
    if dc > 100:
        dc = 100

    global _right_running
    if _right_running:
        _right_pwn.ChangeDutyCycle(dc)
    else:
        _right_pwn.start(dc)
    if forward:
        _right_in1.off()
        _right_in2.on()
    else:
        _right_in1.on()
        _right_in2.off()


def run(forward: bool, count: int):
    # 初始化计数
    left_count = 0
    right_count = 0
    left_active = left_digital.is_active
    right_active = right_digital.is_active

    # 开启左右轮
    left_run(forward, dc=_left_run_init_dc)
    right_run(forward, dc=_right_run_init_dc)

    # 进行计数 & 矫正直线
    while True:
        global _cancel_flag
        if _cancel_flag:
            _cancel_flag = False
            return False, left_count

        tmp_left_active = left_digital.is_active
        if left_active != tmp_left_active:
            left_active = tmp_left_active
            left_count += 1

        tmp_right_active = right_digital.is_active
        if right_active != tmp_right_active:
            right_active = tmp_right_active
            right_count += 1

        delta = left_count - right_count
        left_run(forward, dc=_left_run_init_dc - delta / 2)

        if left_count >= count:
            break

    # 停止左右轮
    left_stop()
    right_stop()

    return True, left_count


def turn_left(count: int):
    # 初始化计数
    cur_count = 0
    left_active = left_digital.is_active
    right_active = right_digital.is_active

    # 转动
    left_run(forward=False, dc=_left_turn_init_dc)
    right_run(forward=True, dc=_right_turn_init_dc)

    # 计数
    while True:
        global _cancel_flag
        if _cancel_flag:
            _cancel_flag = False
            return False, cur_count

        tmp_left_active = left_digital.is_active
        if left_active != tmp_left_active:
            left_active = tmp_left_active
            cur_count += 1

        tmp_right_active = right_digital.is_active
        if right_active != tmp_right_active:
            right_active = tmp_right_active
            cur_count += 1

        if cur_count >= count:
            break

    # 停止
    left_stop()
    right_stop()

    return True, cur_count


def turn_right(count: int):
    # 初始化计数
    cur_count = 0
    left_active = left_digital.is_active
    right_active = right_digital.is_active

    # 转动
    left_run(forward=True, dc=_left_turn_init_dc)
    right_run(forward=False, dc=_right_turn_init_dc)

    # 计数
    while True:
        global _cancel_flag
        if _cancel_flag:
            _cancel_flag = False
            return False, cur_count

        tmp_left_active = left_digital.is_active
        if left_active != tmp_left_active:
            left_active = tmp_left_active
            cur_count += 1

        tmp_right_active = right_digital.is_active
        if right_active != tmp_right_active:
            right_active = tmp_right_active
            cur_count += 1

        if cur_count >= count:
            break

    # 左轮停止
    left_stop()
    right_stop()

    return True, cur_count
