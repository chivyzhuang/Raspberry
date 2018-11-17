import threading
from queue import Queue
from time import sleep

from driver import motor

# 开始运行
MAIN_MSG_START = 0
# 发生碰撞，参数为几号位碰撞传感器
MAIN_MSG_COLLISION = 1
# 发动机任务完成，参数为剩余任务数量
MAIN_MSG_MOTOR_DONE = 2

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

main_queue = Queue()
_motor_queue = Queue()


class Motor(threading.Thread):
    def __init__(self, queue: Queue):
        super(Motor, self).__init__()
        self.queue = queue
        self.lock = threading.Lock()

    def run(self):
        while True:
            obj = self.queue.get()
            if isinstance(obj, tuple):
                msg, args = obj
            else:
                msg, args = obj, None

            if msg == MOTOR_MSG_FORWARD:
                count = args
                print('motor forward, count : %d' % count)
                motor.run(forward=True, count=count)
            elif msg == MOTOR_MSG_BACKWARD:
                count = args
                print('motor backward, count : %d' % count)
                motor.run(forward=False, count=count)
            elif msg == MOTOR_MSG_LEFT:
                count = args
                print('motor turn left, count : %d' % count)
                motor.turn_left(count=count)
            elif msg == MOTOR_MSG_RIGHT:
                count = args
                print('motor turn right, count : %d' % count)
                motor.turn_right(count=count)
            else:
                print('motor unknown msg, msg : %d' % msg)
            self.lock.acquire()
            try:
                main_queue.put((MAIN_MSG_MOTOR_DONE, self.queue.qsize()))
            finally:
                self.lock.release()

            # 发动机不要频繁变化，小车会有惯性，所以每次任务结束后，等待一定时间
            sleep(MOTOR_WAIT_SECONDS)

    def post(self, msg, args):
        self.lock.acquire()
        try:
            self.queue.put((msg, args))
        finally:
            self.lock.release()


motor_thread = Motor(_motor_queue)
motor_thread.start()


def main_loop(callback):
    main_queue.put(MAIN_MSG_START)
    while True:
        obj = main_queue.get()
        if isinstance(obj, tuple):
            msg, args = obj
        else:
            msg, args = obj, None
        callback(msg, args)
