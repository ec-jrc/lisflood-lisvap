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

def asin(x, in_degrees=True, positive_angles=True):
    clip_x = np.array(x, copy=True)
    clip_x[(clip_x < -1) | (clip_x > 1)] = np.nan
    angle_rads = np.arcsin(clip_x)
    if positive_angles:
        # To reproduce the same behaviour as pcraster asin function
        # we need to return positive angles therefore for negative angle
        # in radians we need to rotate in the positive radian direction 
        angle_rads[angle_rads < 0.0] += 2 * np.pi
    if in_degrees:
        angle_degrees = round_decimals(np.rad2deg(angle_rads))
        return angle_degrees
    return angle_rads

def acos(x, in_degrees=True, positive_angles=True):
    clip_x = np.array(x, copy=True)
    clip_x[(clip_x < -1) | (clip_x > 1)] = np.nan
    angle_rads = np.arccos(clip_x)
    if positive_angles:
        # To reproduce the same behaviour as pcraster acos function
        # we need to return positive angles therefore for negative angle
        # in radians we need to rotate in the positive radian direction 
        angle_rads[angle_rads < 0.0] += 2 * np.pi
    if in_degrees:
        angle_degrees = round_decimals(np.rad2deg(angle_rads))
        return angle_degrees
    return angle_rads 

def sqrt(x):
    clip_x = np.array(x, copy=True)
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
        # Constant input: build a plain float64 grid filled with the value and NaN
        # in the masked cells.
        scalar_array = np.full(shape=maskmap.shape, fill_value=expression, dtype=np.float64)
        scalar_array[maskmap.mask] = np.nan
    else:
        # ndarray input (plain float64-with-NaN or, during transition, a masked array):
        # reshape to the maskmap shape and apply NaN at the masked cells. np.asarray
        # drops any numpy.ma subtype so downstream math runs on a plain float64 array.
        scalar_array = np.asarray(expression, dtype=np.float64).flatten().reshape(maskmap.shape).copy()
        scalar_array[maskmap.mask] = np.nan
    return scalar_array

def cover(input_map, mv=0.0):
    """
    This operator is used to cover missing values on a map.
    """
    arr = scalar(input_map)
    # Fill every NaN (structural mask + any missing cells) with mv, matching the
    # previous masked filled() behaviour, and return a plain float64 array.
    arr[np.isnan(arr)] = mv
    return arr

def defined(input_map):
    """
    Boolean TRUE for non missing values and FALSE for missing values.
    """
    return_map = np.empty(input_map.shape)
    return_map[~np.isnan(input_map)] = True
    return_map[np.isnan(input_map)] = False
    return return_map


