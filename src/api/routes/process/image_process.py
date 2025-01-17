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
    file = r.files['image'] #pulls the file out of the request 
    payload = r.form.to_dict() # pulls the payload from the request
    uid = (payload['id'])
    utils.store_image(storageBucket,uid=uid,image=file) #stores the image into the google storage bucket
    pil_image = Image.open(file.stream)#load the image into a readable format from the request
    open_cv_image = np.array(pil_image) 
    open_cv_image = open_cv_image[:, :, ::-1].copy() #RGB to BGR
    userWeight = int(payload['bodyweight'])
    duration = int(payload['duration'])
    verificationDict = {'size': [open_cv_image.shape[0], open_cv_image.shape[1]],'duration':duration,'userweight':userWeight} #creats a dictionary 
    #These template objects never change, but are loaded each time the current
    #script runs, they may be able to be saved in memory.
    template = cv2.imread('./routes/process/masks/blueTemplate.png')
    mask = cv2.imread('./routes/process/masks/Hex Mask.png')
    ring =cv2.imread('./routes/process/masks/Ring.png')
    #this is always the same.
    tempIm, junk = image_library.imageStandardize(template, 800) 
    mask, junk = image_library.imageStandardize(mask, 800)
    ring, junk = image_library.imageStandardize(ring, 800)
    tempImB = image_library.colorFilter(tempIm, plot=False)
    img, x = image_library.imageStandardize(open_cv_image, 800)
    imgB = image_library.colorFilter(img, plot=False)
    #Filter an image that is all blue, or all black

    bluePix = sum(sum(imgB))
    [x,y] = imgB.shape
    tPix = x*y
    if (bluePix/tPix) > .85:
        resultDict = {
        "userWeight": userWeight,
        "passFail": False,
        "status": 500,
        "message": 'The image is too dark, the patch could not be identified'
        }
        resp = jsonify(resultDict)
        resp.status_code= 500
        return resp
        #This failure occures when the blue pixel count is less than 15% of the image, which generally occurs when the image is not 
        # of the patch, when the patch is partially blocked, or when the image is very dark. 

    if (bluePix/tPix) < .05:
        resultDict = {
        "userWeight": userWeight,
        "passFail": False,
        "status": 500,
        "message": 'The image is too blue or bright, the patch could not be identified'
        }
        resp = jsonify(resultDict)
        resp.status_code= 500
        return resp
        # this may occur with significant glare, or if the image is too close.

    maxV, sM, xM, yM = object_match.findScale(imgB, tempImB, 30, 65, 2, showPlot=False)
    #Adjusting the stop to 65 from 60. some images are not be caught
    height = imgB.shape[0]
    imageDownScale = 150/height
    xPos = int(xM/imageDownScale)
    yPos = int(yM/imageDownScale)
    fullMask, croppedAndRotatedImg, internalMask = object_match.imageScaleRotate(
        imgB, mask, sM, 0, xPos, yPos, showPlot=False)
    savedFullMask = fullMask
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
    utils.store_array_image(storageBucket,'mask',fullMask*255,uid)
    utils.store_array_image(storageBucket,'internalMask',internalMask*255,uid)
    utils.store_array_image(storageBucket,'externalMask',externalMask*255,uid)
    passed = True
    if (finalResult < 0.15) or (maxV < 0.35):
        print('failed on '+uid)
        passed = False
        #return {"message":'image failed to process, check quality of image',"status":500}
        #This failure occures when the patch reading returns very little blue, which indicates glare, or an incomplete image
        # If maxV is less than 0.35, the patch could not be identified in the image.
        # If finalResult is less than 0.15, then part of the patch is blocked, due to lighting or other issues. 
    userWeight = int(userWeight)
    duration = int(duration)
    massLoss = loss.estimateMassLoss(finalResult)
    print({'finalResult':finalResult,'totalRegions':totalRegions,'maxV':maxV,'uid':uid,'area':areaROI,'totalPix':totalPix,'sM':sM,'sumFullMask':fullMask.sum()})
    totalLoss, rate, massLoss = loss.adjustByRate(massLoss, duration, userWeight)
    sodLoss = loss.electrolyteLoss(totalLoss, rate)
    #Put results into dictionary
    resultDict = {
        "rate": rate,
        "userWeight": userWeight,
        "massLoss": massLoss,
        "totalLoss": totalLoss,
        "sodLoss": sodLoss,
        "passFail": passed,
        "status": 200,
        "message": 'successfully processed the image'
    }
    print(resultDict)
    if passed == False:
        resultDict['status'] = 500
        resultDict['message'] = 'Poor image quality, failed! this could be due blurring of the image, or that the patch image is skewed'
        #app.logger.error('poor quality image')
        #pass is set above. 
    resultDict.update(verificationDict)

    resp = jsonify(resultDict)

    if passed:
        resp.status_code= 200
    else:
        resp.status_code=500
    return resp
