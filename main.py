from gpiozero import LED, Button
from time import sleep

from driver.motor import left_run, right_run

left_run(forward=True, frequency=50)

sleep(4.6)
