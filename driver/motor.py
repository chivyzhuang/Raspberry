from gpiozero import PWMOutputDevice, OutputDevice
import RPi.GPIO as GPIO

_std_by = OutputDevice(11)

GPIO.setup(0, GPIO.OUT)
_left_pwn = GPIO.PWM(0, 100)
_left_in1 = OutputDevice(5)
_left_in2 = OutputDevice(6)

GPIO.setup(26, GPIO.OUT)
_right_pwn = GPIO.PWM(26, 100)
_right_in1 = OutputDevice(19)
_right_in2 = OutputDevice(13)


def switcher(on):
    if on:
        _std_by.on()
    else:
        _std_by.off()


def left_stop():
    _left_in1.off()
    _left_in2.off()


def left_run(forward: bool = True, frequency=100):
    switcher(True)
    _left_pwn.ChangeDutyCycle(frequency)
    _left_pwn.start(40)
    if forward:
        _left_in1.off()
        _left_in2.on()
    else:
        _left_in1.on()
        _left_in2.off()


def right_stop():
    _right_in1.off()
    _right_in2.off()


def right_run(forward: bool = True, frequency=100):
    switcher(True)
    _right_pwn.ChangeDutyCycle(frequency)
    _right_pwn.start(0)
    # _right_pwn.frequency = frequency
    # _right_pwn.on()
    if forward:
        _right_in1.off()
        _right_in2.on()
    else:
        _right_in1.on()
        _right_in2.off()
