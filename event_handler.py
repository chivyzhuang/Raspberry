import threading
from queue import Queue
from time import sleep

from driver import motor
# 开始运行
from driver.collision import collision_devices_map

# 退出
MAIN_MSG_QUIT = -1
# 启动
MAIN_MSG_START = 0
# 发生碰撞，参数为几号位碰撞传感器
MAIN_MSG_COLLISION_HAPPEN = 1
# 发生碰撞，参数为几号位碰撞传感器
MAIN_MSG_COLLISION_DELETE = 2
# 发动机任务完成
MAIN_MSG_MOTOR_DONE = 3
# 发动机任务取消
MAIN_MSG_MOTOR_CANCEL = 4
# 识别二维码完成
MAIN_MSG_CODE_DONE = 5

# 发动机任务，前进
MOTOR_MSG_FORWARD = 0
# 发动机任务，后退
MOTOR_MSG_BACKWARD = 1
# 发动机任务，左转
MOTOR_MSG_LEFT = 2
# 发动机任务，右转
MOTOR_MSG_RIGHT = 3

# 发动机任务结束后等待时间
MOTOR_WAIT_SECONDS = 0.5

# 碰撞传感器轮询时间
COLLISION_POLLING_CYCLE = 0.01

main_queue = Queue()
_motor_queue = Queue()


class MotorThread(threading.Thread):

    def __init__(self, queue: Queue):
        super(MotorThread, self).__init__()
        self.queue = queue

    def run(self):
        while True:
            obj = self.queue.get()
            if isinstance(obj, tuple):
                msg, args = obj
            else:
                msg, args = obj, None

            main_thread_msg = MAIN_MSG_MOTOR_DONE
            run_count = 0
            if msg == MOTOR_MSG_FORWARD:
                count = args
                print('motor forward, count : %d' % count)
                ret, run_count = motor.run(forward=True, count=count)
                if not ret:
                    main_thread_msg = MAIN_MSG_MOTOR_CANCEL
            elif msg == MOTOR_MSG_BACKWARD:
                count = args
                print('motor backward, count : %d' % count)
                ret, run_count = motor.run(forward=False, count=count)
                if not ret:
                    main_thread_msg = MAIN_MSG_MOTOR_CANCEL
            elif msg == MOTOR_MSG_LEFT:
                count = args
                print('motor turn left, count : %d' % count)
                ret, run_count = motor.turn_left(count=count)
                if not ret:
                    main_thread_msg = MAIN_MSG_MOTOR_CANCEL
            elif msg == MOTOR_MSG_RIGHT:
                count = args
                print('motor turn right, count : %d' % count)
                ret, run_count = motor.turn_right(count=count)
                if not ret:
                    main_thread_msg = MAIN_MSG_MOTOR_CANCEL
            else:
                print('motor unknown msg, msg : %d' % msg)

            main_queue.put((main_thread_msg, (msg, run_count)))

            # 发动机不要频繁变化，小车会有惯性，所以每次任务结束后，等待一定时间
            sleep(MOTOR_WAIT_SECONDS)

    @staticmethod
    def cancel():
        motor.set_cancel_flag()

    def post(self, msg, args):
        self.queue.put((msg, args))


class CollisionThread(threading.Thread):

    def __init__(self):
        super(CollisionThread, self).__init__()
        self.cache_status = {}
        self.collision_count = 0

    def run(self):
        # 初始化碰撞情况
        tmp_count = 0
        for index, device_union in collision_devices_map.items():
            active = False
            for device in device_union:
                if device.is_active:
                    active = True
                    break
            self.cache_status[index] = active
            if active:
                tmp_count += 1
                main_queue.put((MAIN_MSG_COLLISION_HAPPEN, index))
        self.collision_count = tmp_count
        print('collision status : %s, collision count : %d' % (str(self.cache_status), self.collision_count))

        while True:
            sleep(COLLISION_POLLING_CYCLE)
            tmp_count = 0
            for index, device_union in collision_devices_map.items():
                active = False
                for device in device_union:
                    if device.is_active:
                        active = True
                        break
                cache_active = self.cache_status[index]
                if active != cache_active:
                    self.cache_status[index] = active
                    if active:
                        main_queue.put((MAIN_MSG_COLLISION_HAPPEN, index))
                    else:
                        main_queue.put((MAIN_MSG_COLLISION_DELETE, index))
                if active:
                    tmp_count += 1

            self.collision_count = tmp_count

    def has_collision(self):
        return self.collision_count > 0


motor_thread = MotorThread(_motor_queue)
motor_thread.start()
collision_thread = CollisionThread()
collision_thread.start()


def main_loop(callback):
    # 清空队列
    while not main_queue.empty():
        main_queue.get()

    # 发送开始消息
    main_queue.put(MAIN_MSG_START)
    while True:
        obj = main_queue.get()
        if isinstance(obj, tuple):
            msg, args = obj
        else:
            msg, args = obj, None
        if not callback(msg, args):
            break
