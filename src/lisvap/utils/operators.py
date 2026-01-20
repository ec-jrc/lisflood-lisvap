import numpy as np
from ..utils import MaskMapMetadata


sqr = np.square
exp = np.exp
maximum = np.maximum
ifthenelse = np.where
abs = np.abs

def round_decimals(expression):
    return np.round(expression, decimals=16)

def sin(angle_degrees):
    return np.sin(np.deg2rad(round_decimals(angle_degrees)))

def cos(angle_degrees):
    return np.cos(np.deg2rad(round_decimals(angle_degrees)))

def tan(angle_degrees):
    return np.tan(np.deg2rad(round_decimals(angle_degrees)))

def asin(x):
    clip_x = x.copy()
    clip_x[(clip_x < -1) | (clip_x > 1)] = np.nan
    angle_rads = np.arcsin(clip_x)
    # To reproduce the same behaviour as pcraster asin function
    # we need to return positive angles therefore for negative angle
    # in radians we need to rotate in the positive radian direction 
    angle_rads[angle_rads < 0.0] += 2 * np.pi
    angle_degrees = round_decimals(np.rad2deg(angle_rads))
    return angle_degrees

def sqrt(x):
    clip_x = x.copy()
    clip_x[(clip_x < 0)] = np.nan
    return round_decimals(np.sqrt(clip_x))

def scalar(expression):
    """
    If expression is a map or a calculation resulting in a map, it is converted:
    the cell values of expression are assigned without change to the corresponding cells on Result.
    Or it generates a map of scalar data type with one constant value.
    """
    maskmap = MaskMapMetadata.instance().get_maskmap()
    if isinstance(expression, (int, float,
                               np.float16, np.float32, np.float64,
                               np.int16, np.int32, np.int64)):
        scalar_array = np.ma.masked_array(np.full(shape=maskmap.shape, fill_value=expression), mask=maskmap.mask, fill_value=np.nan)
    elif isinstance(expression, np.ma.MaskedArray):
        scalar_array = expression.copy()
    else:
        # scalar_array = np.ma.masked_where(~np.ma.getmask(maskmap), expression)
        scalar_array = np.ma.masked_array(expression.flatten().reshape(maskmap.shape), mask=maskmap.mask, fill_value=np.nan)
    return scalar_array

def cover(input_map, mv=0.0):
    """
    This operator is used to cover missing values on a map.
    """
    npmasked = scalar(input_map)
    nparray = np.ma.getdata(npmasked.filled(), subok=False)
    nparray[np.isnan(nparray)] = mv
    return np.ma.masked_array(nparray, mask=npmasked.mask, fill_value=np.nan)

def defined(input_map):
    """
    Boolean TRUE for non missing values and FALSE for missing values.
    """
    return_map = np.empty(input_map.shape)
    return_map[~np.isnan(input_map)] = True
    return_map[np.isnan(input_map)] = False
    return return_map


