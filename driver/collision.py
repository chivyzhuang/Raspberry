from gpiozero import DigitalInputDevice

INDEX_COLLISION_FRONT_LEFT = 1
INDEX_COLLISION_FRONT = 2
INDEX_COLLISION_FRONT_RIGHT = 3

collision_devices_map = {
    INDEX_COLLISION_FRONT_LEFT: [],
    INDEX_COLLISION_FRONT: [DigitalInputDevice(1, pull_up=True),
                            DigitalInputDevice(7, pull_up=True),
                            DigitalInputDevice(8, pull_up=True)],
    INDEX_COLLISION_FRONT_RIGHT: [],
}
