import picamera
from time import sleep

camera = picamera.PiCamera()

camera.capture('image1.jpg')
sleep(5)
camera.capture('image2.jpg')
