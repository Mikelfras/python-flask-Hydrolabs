# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 11:35:45 2021
@author: Mikel Larson
'''
#input values:
duration
bodyweight
image location which is really just the file to load
future values which may be pulled from firebase: 
    temp 
    humidity
    activity
    locations
#stored diagnostic values:
    --------------
    file : image UUID value so we can find it
     finalResult: float
    ratio of the counted pixels within hexagons to the area within the matched 
    template
    totalPix: int
    count of pixels within the masked image
    areaROI: int
    area within the template, should scale, but be shape and original image agnostic
    totalRegions: int
    count of identified regions, should always be less than 19. 
    templateMatchTime : float
    time to complete template matching
    imageRescaleTime: float
    time to complete image rescaling
#returned values:
    -------------
massLoss 
totalLoss
rate
sodLoss
'''
"""
from flask import jsonify
import numpy as np
from . import object_match
from . import loss
from . import image_library
import cv2
import utils
from PIL import Image

def hello(s):
    print(s)

def image_analysis(r,storageBucket):
    file = r.files['image']
    payload = r.form.to_dict()
    uid = (payload['id'])
    utils.store_image(storageBucket,uid=uid,image=file)
    pil_image = Image.open(file.stream)
    open_cv_image = np.array(pil_image) 
    open_cv_image = open_cv_image[:, :, ::-1].copy() #RGB to BGR
    userWeight = int(payload['bodyweight'])
    duration = int(payload['duration'])
    verificationDict = {'size': [open_cv_image.shape[0], open_cv_image.shape[1]],'duration':duration,'userweight':userWeight}
    #These template objects never change, but are loaded each time the current
    #script runs, they may be able to be saved in memory.
    template = cv2.imread('./routes/process_endpoint/masks/blueTemplate.png')
    mask = cv2.imread('./routes/process_endpoint/masks/blueTemplate.png')
    ring =cv2.imread('./routes/process_endpoint/masks/blueTemplate.png')
    #this is always the same.
    tempIm, junk = image_library.imageStandardize(template, 800)
    mask, junk = image_library.imageStandardize(mask, 800)
    ring, junk = image_library.imageStandardize(ring, 800)
    tempImB = image_library.colorFilter(tempIm, plot=False)
    img, x = image_library.imageStandardize(open_cv_image, 800)
    imgB = image_library.colorFilter(img, plot=False)
    maxV, sM, xM, yM = object_match.findScale(imgB, tempImB, 30, 60, 2, showPlot=False)
    height = imgB.shape[0]
    imageDownScale = 150/height
    xPos = int(xM/imageDownScale)
    yPos = int(yM/imageDownScale)
    fullMask, croppedAndRotatedImg, internalMask = object_match.imageScaleRotate(
        imgB, mask, sM, 0, xPos, yPos, showPlot=False)
    fullMaskRing, croppedAndRotatedImg, externalMask = object_match.imageScaleRotate(
        imgB, ring, sM, 0, xPos, yPos, showPlot=False)
    #print('failed on file: '+file)
    maxi_coordsIn, markersIn = image_library.keyPointIdByMaxima(internalMask)
    maxi_coordsOut, markersOut = image_library.keyPointIdByMaxima(
        externalMask, prox=5, num_peaks=200)
    yArray = np.append(maxi_coordsIn[0], maxi_coordsOut[0])
    xArray = np.append(maxi_coordsIn[1], maxi_coordsOut[1])
    maxi_coords = (yArray, xArray)
    markers = np.zeros(shape=fullMask.shape, dtype='uint32')
    for i in range(0, len(yArray), 1):
        markers[yArray[i], xArray[i]] = i+1
    finalResult, totalPix, areaROI, totalRegions, labelsMasked = image_library.regionFilter(
        maxi_coords, markers, croppedAndRotatedImg, fullMask, img, plot=False)
    utils.store_array_image(storageBucket,'final',croppedAndRotatedImg*255,uid)
    passFail = True
    if (finalResult < 0.15) or (totalRegions < 18) or (maxV < 0.45):
        passFail = 0
        #return {"message":'image failed to process, check quality of image',"status":500}
    userWeight = int(userWeight)
    duration = int(duration)
    massLoss = loss.estimateMassLoss(finalResult)
    totalLoss, rate, massLoss = loss.adjustByRate(massLoss, duration, userWeight)
    sodLoss = loss.electrolyteLoss(totalLoss, rate)
    #Put results into dictionary
    resultDict = {
        "rate": rate,
        "userWeight": userWeight,
        "massLoss": massLoss,
        "totalLoss": totalLoss,
        "sodLoss": sodLoss,
        "passFail": passFail,
        "status": 200,
        "message": 'successfully processed the image'
    }
    if resultDict['status'] == 500:
        app.logger.error('poor quality image')
        return resultDict['message'], resultDict['status']
    resultDict.update(verificationDict)
    resp = jsonify(resultDict)
    resp.status_code= 200;
    return resp
