from gpiozero import DigitalInputDevice

INDEX_COLLISION_FRONT_1 = 1
INDEX_COLLISION_FRONT_2 = 2
INDEX_COLLISION_FRONT_3 = 3
INDEX_COLLISION_FRONT_4 = 4

collision_devices_map = {
    INDEX_COLLISION_FRONT_1: DigitalInputDevice(25, pull_up=True),
    INDEX_COLLISION_FRONT_2: DigitalInputDevice(8, pull_up=True),
    INDEX_COLLISION_FRONT_3: DigitalInputDevice(7, pull_up=True),
    INDEX_COLLISION_FRONT_4: DigitalInputDevice(1, pull_up=True),
}
