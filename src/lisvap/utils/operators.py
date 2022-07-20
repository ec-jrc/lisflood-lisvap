import pcraster.operations

try:
    from pcraster.multicore import _operations as operations
except (ImportError, NameError):
    from pcraster import operations

sin = operations.sin
cos = operations.cos
tan = operations.tan
asin = operations.asin
sqrt = operations.sqrt
sqr = operations.sqr
maximum = operations.max
ifthenelse = operations.ifthenelse
exp = pcraster.operations.exp
abs = operations.abs

# sin = np.sin
# cos = np.cos
# tan = np.tan
# asin = np.arcsin
# sqrt = np.sqrt
# sqr = np.square
# exp = np.exp
# maximum = np.maximum
# ifthenelse = np.where

cover = operations.cover
scalar = operations.scalar
