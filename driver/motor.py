from gpiozero import OutputDevice, DigitalInputDevice
import RPi.GPIO as GPIO

_std_by = OutputDevice(11)

_frequency = 50

_left_pwm_channel = 0
GPIO.setup(_left_pwm_channel, GPIO.OUT)
_left_pwn = GPIO.PWM(_left_pwm_channel, _frequency)
_left_in1 = OutputDevice(5)
_left_in2 = OutputDevice(6)
_left_digital = DigitalInputDevice(14)

_right_pwn_channel = 26
GPIO.setup(_right_pwn_channel, GPIO.OUT)
_right_pwn = GPIO.PWM(_right_pwn_channel, _frequency)
_right_in1 = OutputDevice(19)
_right_in2 = OutputDevice(13)
_right_digital = DigitalInputDevice(21)


def switcher(on):
    if on:
        _std_by.on()
    else:
        _std_by.off()


def left_stop():
    _left_in1.off()
    _left_in2.off()


def left_run(forward: bool = True, dc=100):
    switcher(True)
    _left_pwn.stop()
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


def right_run(forward: bool = True, dc=100):
    switcher(True)
    _right_pwn.stop()
    _right_pwn.start(dc)
    if forward:
        _right_in1.off()
        _right_in2.on()
    else:
        _right_in1.on()
        _right_in2.off()
