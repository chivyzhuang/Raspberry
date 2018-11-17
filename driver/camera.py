import os
from typing import Tuple

import zbarlight
from PIL import Image
from picamera import PiCamera


class Camera:

    def __init__(self, save_path):
        self.cam = PiCamera()
        self.save_path = save_path

    def get_cur_qrcode_list(self) -> Tuple[list, list, list]:
        self.cam.capture(self.save_path)
        if not os.path.exists(self.save_path):
            print(self.save_path, "is not valid")
            return [], [], []

        # 第一次整图识别
        f = open(self.save_path, 'rb')
        qr = Image.open(f)
        codes = zbarlight.scan_codes('qrcode', qr)
        if codes is None:
            codes = []

        # 无二维码
        if len(codes) == 0:
            return [], [], []

        # 识别左边二维码
        left_qr = qr.crop((360, 0, 720, 480))
        left_codes = zbarlight.scan_codes('qrcode', left_qr)
        if left_codes is None:
            left_codes = []

        # 识别右边二维码
        right_qr = qr.crop((0, 0, 360, 480))
        right_codes = zbarlight.scan_codes('qrcode', right_qr)
        if right_codes is None:
            right_codes = []

        # 不在左右的放中间
        center_codes = list(set(codes) - set(left_codes) - set(right_codes))

        # 同时在左右的也放中间
        for i in list(left_codes):
            if i in right_codes:
                left_codes.remove(i)
                right_codes.remove(i)
                center_codes.append(i)

        return left_codes, center_codes, right_codes


if __name__ == '__main__':
    camera = Camera('/home/pi/qrcode.jpg')
    print(camera.get_cur_qrcode_list())
