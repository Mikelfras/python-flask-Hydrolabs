from __future__ import print_function

import time
import testCases as tC 
from datetime import datetime

addr = '127.19.0.2:5000'
test_url = addr + '/api/process'
# prepare headers for http request
content_type = 'image/jpeg'
headers = {'content-type': content_type}


attempts=0
totalAttempts = 1
# send http request with image and receive response
while attempts < totalAttempts:
    now = datetime.now()
    timeNow = now.strftime("%H:%M:%S")
    print('**********TEST START at {} ******************'.format(timeNow))
    time.sleep(2);
    tC.resTest()
    tC.noImageTest()
    tC.getTest()
    tC.noPayloadTest('image.JPG')
    tC.testImage(fileName = 'IMG_0809.JPG', bodyweight=160, duration=120, uid='image_1')
    tC.testImage(fileName = 'IMG_0810.JPG', bodyweight= 160, duration = 180, uid='image_2')
    #tC.testImageFailed(fileName='image.JPG',uid='failed')
    tC.resEmptyTest()
    attempts = attempts+1

