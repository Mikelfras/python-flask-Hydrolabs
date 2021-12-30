# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 11:27:23 2021
@author: Mikel Larson
"""


import numpy as np
import cv2
from skimage.feature import match_template
from scipy import ndimage

def rescale(src,factor):
    """Rescales an image 
    Parameters
    -----------
    src: array of uint8 
     array shaped like `image` with a binary mask
   factor: float 
       scaling factor, i.e. a value of 0.8 will scale the image to 80%
    Returns
    ----------
    scaled: array of uint8 
     array shaped like `image` with a binary mask reduced in size. 
    """
    width = int(src.shape[1] * factor)
    height = int(src.shape[0] * factor)
    dim = (width, height)
    scaled = cv2.resize(src, dim)
    return scaled

def imageScaleRotate(src,template,scale,rotation,x,y, showPlot=False):
    """ Creates a mask, and then places it on the image
     
    Parameters
    -----------
    src : array of uint8 
     array shaped like `image` with a binary mask of color
    template : array of uint8 
     array shaped like `template` with a binary mask, to be identified in the image. 
   scale : int
     scale factor to use, calculated by (100-S)/100, so it is a % decrease
     in scale
    rotation : float
        rotation value f the max correlation in the src for the template
    x : int
        x location of the max correlation in the src for the template
    y : int
        y location of the max correlation in the src for the template
   
       
    Returns
    ----------
    fullMask : array of uint8 
        masked matched in size to the src
       
    src : array of uint8
        array sized to fit the full mask
    internal : int
       src with the full mask anded to it, such that only the area within
       the mask is identified. 
    """
    scaleFactor = 1.0*(float(100-(scale))/100)
    template = cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)
    template = cv2.bitwise_not(template)
    template = rescale(template,scaleFactor)
    if rotation<0:
        rotate = 360+rotation
        template = ndimage.rotate(template,rotate)
    else:
        rotate = rotation
        template = ndimage.rotate(template,rotate)

    h,w = template.shape
    cropped = src[y:y+h,x:x+w] 
    if rotation != 0:
        cropped = ndimage.rotate(cropped,360-rotate)
        template = ndimage.rotate(template,-rotate)
    fullMask = np.zeros(shape=cropped.shape[0:2],dtype='uint8')
    fullMask = template;
    internal = cv2.bitwise_and(cropped,cropped,mask=fullMask)
    return fullMask, cropped,internal
    
def findScale(image,template,start,stop,increment,subRot=0,showPlot=True):
    """Uses template matching to find the approximate scale and location of the template
     
    Parameters
    -----------
    image : array of uint8 
     array shaped like `image` with a binary mask
    template: array of uint8 
     array shaped like `image` with a binary mask, to be identified in the image. 
   start : int
     initial scale factor to use, calculated by (100-S)/100, so it is a % decrease
     in scale
   stop : int
       smallest reduction in size allowable
   increment : int
       reduction in size at each increment
   subRot : float, optional
        The rotation angle in degrees.
   showPlot : bool, optional
       show the plot or dont. 
       
    Returns
    ----------
    maxV : float
        max correlation coefficient from skimage.feature, match_template
    sM: float
        scale value that resulted in the max correlation
    xM: int
        x location of the max correlation
    yM: int
        y location of the max correlation        
    """
    #determines the scale of the patch within the image using template matching
    height = template.shape[0]
    scale_factor = 150/height
    template = rescale(template,scale_factor)
    height = image.shape[0]
    scale_factor = 150/height
    image = rescale(image,scale_factor)
    if subRot !=0:
        template = ndimage.rotate(template,subRot)
    maxV = 0
    sM = 1
    s=start
    fit = 0    
    while s<stop:
        #todo: Convergence - determine if the match is no longer improving. 
        #adjust the scaling increments by the relative improvements in fit. 
        scaleFactor = 1.0*(float(100-s)/100)
        output = rescale(template,scaleFactor)
        try:
            result = match_template(image, output)
            values = result.flatten()
            fit = max(values)
            if fit>maxV:
                maxV=fit
                sM = s
                ij = np.unravel_index(np.argmax(result), result.shape)
                x, y = ij[::-1]
                xM = x
                yM = y
            if fit<0.2: 
                s = s+2*increment
            elif fit<0.5:
                s = s+0.5*increment
            elif fit>0.75:
                s = stop
            else:
                s = s+0.3*increment
        except:
            #occurs when the template is to big in one dim.
            s=s+2*increment
    return maxV, sM, xM,yM

def findRotation(image,template,start,stop,increment,subScale=0,showPlot=True):
    """Uses template matching to find the approximate scale and location of the template
     
    Parameters
    -----------
    image: array of uint8 
     array shaped like `image` with a binary mask
    template: array of uint8 
     array shaped like `image` with a binary mask, to be identified in the image. 
   start : int
     initial rotation factor to use 
   stop : int
       max angle of rotation in size allowable
   increment : int
       rotation at each increment
   subScale : float, optional
        The scaling factor from findScale
   showPlot : bool, optional
       show the plot or dont. 
       
    Returns
    ----------
    maxV: float
        max correlation coefficient from skimage.feature, match_template
    rM: float
        rotation value that resulted in the max correlation
    xM: int
        x location of the max correlation
    yM: int
        y location of the max correlation  
    imageDownScale : float
        factor for scaling the base image to speed up processing, can be used to adjust the x and y locations
    """
    height = template.shape[0]
    imageDownScale = 150/height
    template = rescale(template,imageDownScale)
    height = image.shape[0]
    imageDownScale = 150/height
    image = rescale(image,imageDownScale)
    scaleFactor = 1.0*(float(100-subScale)/100)
    template = rescale(template,scaleFactor)
    maxV = 0
    rotation=start
    fit = 0    
    
    while rotation<stop:
        rotation = rotation+increment
        if rotation<0:
            rotate = 360+rotation
        else:
            rotate = rotation
        output = ndimage.rotate(template, rotate)
        try: 
            result = match_template(image, output)
            values = result.flatten()
            fit = max(values)
            ij = np.unravel_index(np.argmax(result), result.shape)
            x, y = ij[::-1]
            if fit>maxV:
                maxV=fit
                rM = rotation 
                xM = x
                yM = y
            if fit < 0.2:
                rotation = rotation+15
        except:
            rotation = rotation+increment
    return maxV, rM, xM,yM,imageDownScale 