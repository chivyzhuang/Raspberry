from time import sleep

from driver.motor import left_run, right_run

left_run(forward=True, dc=50)
right_run(forward=True, dc=50)

sleep(2)
