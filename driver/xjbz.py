from driver.motor import left_run

# door1
DOOR_ONE='Door1'
# door2
DOOR_TWO='Door2'
# wall right
WALL_RIGHT_ONE = 'Wall-Right-1'
WALL_RIGHT_TWO = 'Wall-Right-2'
# wall left
WALL_LEFT_ONE = 'Wall-Left-1'
WALL_LEFT_TWO = 'Wall-Left-2'
# wall top
WALL_TOP_ONE = 'Wall-Top-1'
WALL_TOP_TWO = 'Wall-Top-2'
WALL_TOP_THREE = 'Wall-Top-3'
# wall bottom
WALL_BOTTOM_ONE = 'Wall-Bottom-1'
WALL_BOTTOM_TWO = 'Wall-Bottom-2'
WALL_BOTTOM_THREE = 'Wall-Bottom-3'


# wall list
wall_list = [WALL_RIGHT_TWO, DOOR_TWO, WALL_RIGHT_ONE, WALL_BOTTOM_THREE, WALL_BOTTOM_TWO, WALL_BOTTOM_ONE, WALL_LEFT_TWO, DOOR_ONE, WALL_LEFT_ONE, WALL_TOP_ONE, WALL_TOP_TWO, WALL_TOP_THREE]

# 是否已经找到门
_door_found = False


def go_xjbz():


def find_door():
    # 旋转车，查找door
    while _door_found:
        # 转动一定角度
        # 拍照，查看二维码
        # 判断是否找到门的二维码
