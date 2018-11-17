from gpiozero import LED, Button
from time import sleep

STBY = LED(14)

AIN2 = LED(2)
AIN1 = LED(3)

BIN1 = LED(4)
BIN2 = LED(17)

PMWA = LED(27)
PMWB = LED(22)

AIN1.off()
AIN2.on()

BIN1.off()
BIN2.on()

PMWA.on()
PMWB.on()

button = Button(26)

while True:
    if button.is_pressed:
        STBY.off()
    else:
        STBY.on()

    sleep(0.1)
