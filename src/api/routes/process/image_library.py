# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 10:54:01 2021
@author: Mikel Larson
"""

import numpy as np
from skimage import segmentation
from skimage.feature import peak_local_max
from scipy import ndimage as ndi
import cv2
import tempfile

def imageStandardize(src, maxHeight=800):
    """Standardizes the size of the image
        uses the openCV2 module to read an image,
        and then rotate to a portriat view (long axis vertical)
        
        Parameters
        -----------
        filePath: str
            variable to be read by imread
        maxHeight : int 
            standardized value for the long axis image rescaled
            using openCV resize
        
        Returns
        ----------
        output : image
            rescaled image with color channels BGR. 
        scaleFactor: float
            ratio of scale. maxHeight/actual height
    """
    width = int(src.shape[1])
    height = int(src.shape[0])
    if (width > height):
        src = cv2.rotate(src, cv2.cv2.ROTATE_90_CLOCKWISE)
        width = int(src.shape[1])
        height = int(src.shape[0])
    scaleFactor = float(maxHeight/height)
    sWidth = int(width*scaleFactor)
    sHeight = int(height*scaleFactor)
    dsize = (sWidth, sHeight)
    output = cv2.resize(src, dsize)
    return output, scaleFactor


def colorFilter(src, plot=False):
    """Creates a binary mask based on the red color channel
     
    Parameters
    -----------
    src: array of unit8
        image with a BGR channels (in that order)
    plot : boolean
        to plot or not to plot (defaults to false)
    
    Returns
    ----------
    mask : array unint8 with single channel
        binary where 0 is not the right color, and 1 is
    TODO:
    -----------
    This is hit or miss for some images - needs some more work to work with
    all images that may be captured. 
    """

    # This section of the algorithm will likely be updated over the next
    # few weeks.

    #low = np.array([30,0,0])
    #up = np.array([255,210,65])
    # preparing the mask to overlay
    # if r > 40, if if !(b-r>40)
    rChan = src[:, :, 2]
    cl1 = cv2.equalizeHist(rChan)
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(5, 5))
    cl1 = clahe.apply(rChan)
    #cl1 = cl1.astype('uint8')
    mask = rChan < 60



    return mask.astype('uint8')

def keyPointIdByMaxima(mask, prox=20, num_peaks=50, thresh=0.2, plot=False):
    """Identifies regional peaks based on distance from edges 
     
    Parameters
    -----------
      mask : array unint8 with single channel
        binary where 0 is not an identified region, and 1 is. 
    prox : int, optional
        The minimal allowed distance separating peaks. To find the
        maximum number of peaks, use `min_distance=1`.
    num_peaks : int, optional
        Maximum number of peaks. When the number of peaks exceeds `num_peaks`,
        return `num_peaks` peaks based on highest peak intensity.
    thresh : float, optional
        Minimum intensity of peaks, calculated as `max(image) * threshold_rel`.
    plot : bool, optional
        plot the results
    
    Returns
    ----------
    maxi_coords: tuple
        tuple shaped like `image`, with peaks
         represented by True values.
    markers: ndarray or int
        An integer ndarray where each unique feature in `input` has a unique
        label in the returned array.
    
    """
    distance = ndi.distance_transform_edt(mask)
    localMaxima = peak_local_max(
        distance, min_distance=prox, threshold_rel=thresh, indices=False)
    maxi_coords = np.nonzero(localMaxima)
    markers = ndi.label(localMaxima)[0]
    return maxi_coords, markers

def regionFilter(maxi_coords, markers, processedImage, mask, img, plot=False):
    """Identifies regional peaks based on distance from edges 
     
    Parameters
    -----------
    maxi_coords: Boolean
        array shaped like `image`, with peaks
         represented by True values.
   markers: ndarray or int
        An integer ndarray where each unique feature in `input` has a unique
        label in the returned array.
    processedImage : aray of uint8
          image that has been scaled and cropped appropriately for area calculation 
    mask : array of uint8
         mask that has been scaled and cropped appropriately for area calculation 
    img : array of uint8
        initial image to be processed with channels bgr
    file: str
        file name to append to the plot file
    plot : bool, false 
        plot the results
    Returns
    ----------
        finalResult: float
        ratio of the counted pixels within hexagons to the area within the matched 
        template
        totalPix: int
        count of pixels within the masked image
        areaROI: int
        area within the template, should scale, but be shape and original image agnostic
        totalRegions: int
        count of identified regions, should always be less than 19. 
        labelsMasked: array of uint8
        final masked regions identified. 
        masked labels 
    
    """
    labelsMasked = segmentation.watershed(
        processedImage, markers, mask=processedImage, connectivity=1)
    seedBlackList = []
    Y = maxi_coords[0]
    X = maxi_coords[1]
    for i in range(len(X)):
        x = X[i]
        y = Y[i]
        if not(mask[y, x]):
            seedBlackList.append([x, y])
    filtRegions = []
    i = 0
    indices = np.unique(labelsMasked[labelsMasked != 0])
    for i in range(len(indices)):
        # take regions with large enough areas
        regionLab = indices[i]
        for seed in seedBlackList:
            x, y = seed
            if labelsMasked[y, x] == regionLab:
                filtRegions.append(regionLab)
                labelsMasked[labelsMasked == regionLab] = 0
                break
    totalRegions = len(np.unique(labelsMasked))
    labelsMasked[labelsMasked > 0] = 1
    totalPix = labelsMasked.sum()
    areaROI = mask.sum()
    ratio = totalPix/areaROI
    finalResult = ratio*100
    return [finalResult, totalPix, areaROI, totalRegions, labelsMasked]

def plotter(image):
    #Temporary file to edit
    #requires matplotlib import
    [_, temp_local_filename] = tempfile.mkstemp()
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
    ax[0].imshow(cl1, cmap='gray')
    ax[0].set_title('Init Image')
    ax[1].imshow(mask, cmap='gray')
    ax[1].set_title('Color Filtered Result')
    plt.show()
    plt.savefig(temp_local_filename+'.jpeg')
    # imgSave.imageSave(temp_local_filename+'.jpeg', file, "_colorFilter")