# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 12:04:15 2021
@author: Mikel Larson
"""


def estimateMassLoss(val):
    """Calculate body mass loss in a % based on a super simple linear regression
     
    Parameters
    -----------
      val : float
        final result
    
    Returns
    ----------
      %body mass loss. 
    
    TODO:
    ---------
    these values will change A LOT we should probably figure out a way to load
    them from the users, or generate them based on demographic data. 
    """
    m = 0.071428571
    b = -0.015
    return (val*m+b)


def adjustByRate(massLoss, dur, startWeight):
    """Use basic logic to adjust rate based on know values
     
    Parameters
    -----------
      massLoss : float
           estimated mass loss at this time point
      dur : float
          time when image was taken since start of the measurement in mins. 
      startWeight : int
          body mass of the subject in lbs
    Returns
    ----------
      totalLoss: float
         oz of fluid loss by this measurement
      rate: float
          rate at which fluid was lost (oz/hr)
      massLoss: float
          total % of body mass lost by this point
          
    
    TODO:
    ---------
    The upper and lower limits are likely to be adjusted based on demographics
    in the future, and will be much more dynamic. 
    """
    upperRateLimit = 75  # 99% of folks have a sweat rate under 75oz/hr, over that is likely an error
    # when exercising, you have a baseline loss due to resperation and mild fluid loss
    lowerRateLimit = 10
    if dur < 3:  # if less than 3 minutes, no sweating has logically occured
        totalLoss = 0
        rate = 0
        massLoss = 0
        return totalLoss, rate, massLoss
    rate = (massLoss*startWeight*16)/(dur/60)
    if rate > upperRateLimit:
        rate = upperRateLimit
    elif rate < lowerRateLimit:
        rate = lowerRateLimit
    totalLoss = rate*(dur/60)
    massLoss = (totalLoss/16)/startWeight
    return totalLoss, rate, massLoss


def electrolyteLoss(totalLoss, rate, acclimatized=True):
    """Estimate electrolyte loss based on rate, fluid loss, and acclimatization
     
    Parameters
    -----------
     totalLoss : float
         oz of fluid loss by this measurement
      rate : float
          rate at which fluid was lost (oz/hr)
      acclimatized : bool, optional
          is this activity under normal weather conditions for the individual
    Returns
    ----------
      sodLoss: float
         mg sodium lost 
     
      
    TODO:
    ---------
     in the future, acclimatized should be determined based on past activities
     the loss rate should be better calculated based on atheltic history
     and other factors. 
     the current fit is based on a study comparing acclimatized to unacclimatized
     individuals at variable sweat rates.
    """
    if acclimatized:
        m = 0.5338
        b = 4.1636
    else:
        m = 1.0265
        b = 16.192
    lossRate = rate*m+b  # in mg/oz
    sodLoss = totalLoss*lossRate  # in mg
    return sodLoss


def activeReplacementSuggestion(rate, startWeight, duration):
    '''
    Not currently in use.
    '''
    lbRate = rate/16.0
    percentRate = 100*lbRate/startWeight

    replacementRate = percentRate*duration/60-1
    print(percentRate)
    replacementRate = (replacementRate/100)*startWeight*16/(duration/60)
    baseString = 'During activities of this duration and conditions, '
    if replacementRate < 2.5:
        responseString = baseString+'you are unlikely to become dehydrated.'
    replacementRate = specificRound(replacementRate)
    if replacementRate > 40:
        maxReplacement = 40
        percentReplacementRate = (40/16)/startWeight
        perHourPercentDeficit = percentRate-100*percentReplacementRate
        dehydratedAfter = 3.0/perHourPercentDeficit

        responseString = baseString+'you should replace at a rate of ' + \
            str(maxReplacement)+' Oz/Hr.'
        if dehydratedAfter*60 < duration:
            print(perHourPercentDeficit*duration/60)
            responseString = responseString + \
                ' Fluids lost due to sweating exceed healthy replacement. Dehydration is likely.'
    else:
        responseString = baseString+'you should replace at a rate of ' + \
            str(replacementRate)+' Oz/Hr.'
    return [responseString, replacementRate]


def recoverySuggestion(replacementRate, consumed, duration):
    lost = replacementRate*(duration/60)
    if duration > 45:
        fluidType = 'an isotonic sports drink'
    else:
        fluidType = 'water'
    deficit = lost-consumed
    replacement = 1.20*deficit
    replacement = specificRound(replacement)
    return 'To replenish, consume ' + str(replacement) + ' Oz '+fluidType+' over the next two hours'


def specificRound(x, base=2):
    return base * round(x/base)
