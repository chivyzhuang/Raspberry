from picamera import PiCamera
import os
import zbarlight
import PIL


class Camera():
    def __init__(self, save_dir):
        self.cam = PiCamera()
        self.save_dir = save_dir
        self.file_path = None

    def capture(self, name):
        self.file_path = os.path.join(self.save_dir, name)
        self.cam.capture(self.file_path)

    def decode(self):
        if self.file_path is None or not os.path.exists(self.file_path):
            print(self.file_path, "is not valid")
            return None

        f = open(self.file_path, 'rb')
        qr = PIL.Image.open(f)
        qr.load()

        codes = zbarlight.scan_codes('qrcode', qr)
        if codes is None:
            print('No QR code found')
        else:
            print('QR code(s):', codes)

        return codes


# test code
if __name__ == '__main__':
    cam = Camera('/home/pi')
    cam.capture('fuck.jpg')
    print('decode msg:', cam.decode())




