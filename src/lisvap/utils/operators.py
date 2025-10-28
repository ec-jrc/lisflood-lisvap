import numpy as np
from ..utils import MaskMapMetadata

# Numerical value of Pi
Pi = 3.14159265358979323846
deg2rad = Pi / 180.


sqr = np.square
exp = np.exp
maximum = np.maximum
ifthenelse = np.where
abs = np.abs

def sin(angle_degrees):
    return np.round(np.sin(deg2rad * angle_degrees), 16)

def cos(angle_degrees):
    return np.round(np.cos(deg2rad * angle_degrees), 16)

def tan(angle_degrees):
    return np.round(np.tan(deg2rad * angle_degrees), 16)

def asin(x):
    # clip_x = np.clip(x, -1, 1)
    clip_x = x.copy()
    clip_x[(clip_x < -1) | (clip_x > 1)] = np.nan
    angle_degrees = np.arcsin(clip_x) / deg2rad
    return np.round(angle_degrees, 16)

def sqrt(x):
    clip_x = x.copy()
    clip_x[(clip_x < 0)] = np.nan
    return np.round(np.sqrt(clip_x), 16)

def scalar(expression):
    """
    If expression is a map or a calculation resulting in a map, it is converted:
    the cell values of expression are assigned without change to the corresponding cells on Result.
    Or it generates a map of scalar data type with one constant value.
    """
    maskmap = MaskMapMetadata.instance().get_maskmap()
    if isinstance(expression, (int, float)):
        scalar_array = np.empty(maskmap.shape)
        # scalar_array[maskmap.mask] = expression
        # scalar_array[~maskmap.mask] = np.nan
        scalar_array.fill(expression)
    else:
        scalar_array = np.ma.masked_where(np.ma.getmask(maskmap), expression)
        # scalar_array = np.ma.masked_where(np.ma.getmask(maskmap), expression)
    return scalar_array

def cover(input_map, mv=0.0):
    """
    This operator is used to cover missing values on a map.
    """
    nparray = input_map
    nparray[np.isnan(nparray)] = mv
    return nparray


