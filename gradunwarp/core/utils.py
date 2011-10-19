### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the gradunwarp package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
import numpy as np
from collections import namedtuple
import math
from math import sqrt, cos, pi


# This is a container class that has 3 np.arrays which contain
# the x, y and z coordinates respectively. For example, the output
# of a meshgrid belongs to this
# x, y, z = meshgrid(np.arange(5), np.arange(6), np.arange(7))
# cv = CoordsVector(x=x, y=y, z=z)
CoordsVector = namedtuple('CoordsVector', 'x, y, z')


def transform_coordinates(A, M):
    ''' 4x4 matrix M operates on orthogonal coordinates arrays
    A1, A2, A3 to give B1, B2, B3
    '''
    A1 = A.x
    A2 = A.y
    A3 = A.z
    B1 = A1 * M[0, 0] + A2 * M[0, 1] + A3 * M[0, 2] + M[0, 3]
    B2 = A1 * M[1, 0] + A2 * M[1, 1] + A3 * M[1, 2] + M[1, 3]
    B3 = A1 * M[2, 0] + A2 * M[2, 1] + A3 * M[2, 2] + M[2, 3]
    return CoordsVector(B1, B2, B3)


def get_vol_affine(cls, infile):
    nibimage = nib.load(infile)
    return nibimage.get_data(), nibimage.get_affine()


# memoized factorial
class Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}

    def __call__(self, *args):
        if not args in self.memo:
            self.memo[args] = self.f(*args)
        return self.memo[args]

factorial = Memoize(math.factorial)


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
# This is taken from a numpy ticket which adds N-d support to meshgrid
# URL : http://projects.scipy.org/numpy/ticket/966
# License : http://docs.scipy.org/doc/numpy/license.html
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
def meshgrid(*xi, **kwargs):
    """
    Return coordinate matrices from one or more coordinate vectors.

    Make N-D coordinate arrays for vectorized evaluations of
    N-D scalar/vector fields over N-D grids, given
    one-dimensional coordinate arrays x1, x2,..., xn.

    Parameters
    ----------
    x1, x2,..., xn : array_like
        1-D arrays representing the coordinates of a grid.
    indexing : 'xy' or 'ij' (optional)
        cartesian ('xy', default) or matrix ('ij') indexing of output
    sparse : True or False (default) (optional)
         If True a sparse grid is returned in order to conserve memory.
    copy : True (default) or False (optional)
        If False a view into the original arrays are returned in order to
        conserve memory

    Returns
    -------
    X1, X2,..., XN : ndarray
        For vectors `x1`, `x2`,..., 'xn' with lengths ``Ni=len(xi)`` ,
        return ``(N1, N2, N3,...Nn)`` shaped arrays if indexing='ij'
        or ``(N2, N1, N3,...Nn)`` shaped arrays if indexing='xy'
        with the elements of `xi` repeated to fill the matrix along
        the first dimension for `x1`, the second for `x2` and so on.

    See Also
    --------
    index_tricks.mgrid : Construct a multi-dimensional "meshgrid"
                     using indexing notation.
    index_tricks.ogrid : Construct an open multi-dimensional "meshgrid"
                     using indexing notation.

    Examples
    --------
    >>> x = np.linspace(0,1,3)   # coordinates along x axis
    >>> y = np.linspace(0,1,2)   # coordinates along y axis
    >>> xv, yv = meshgrid(x,y)   # extend x and y for a 2D xy grid
    >>> xv
    array([[ 0. ,  0.5,  1. ],
           [ 0. ,  0.5,  1. ]])
    >>> yv
    array([[ 0.,  0.,  0.],
           [ 1.,  1.,  1.]])
    >>> xv, yv = meshgrid(x,y, sparse=True)  # make sparse output arrays
    >>> xv
    array([[ 0. ,  0.5,  1. ]])
    >>> yv
    array([[ 0.],
           [ 1.]])

    >>> meshgrid(x,y,sparse=True,indexing='ij')  # change to matrix indexing
    [array([[ 0. ],
           [ 0.5],
           [ 1. ]]), array([[ 0.,  1.]])]
    >>> meshgrid(x,y,indexing='ij')
    [array([[ 0. ,  0. ],
           [ 0.5,  0.5],
           [ 1. ,  1. ]]), array([[ 0.,  1.],
           [ 0.,  1.],
           [ 0.,  1.]])]

    >>> meshgrid(0,1,5)  # just a 3D point
    [array([[[0]]]), array([[[1]]]), array([[[5]]])]
    >>> map(np.squeeze,meshgrid(0,1,5))  # just a 3D point
    [array(0), array(1), array(5)]
    >>> meshgrid(3)
    array([3])
    >>> meshgrid(y)      # 1D grid; y is just returned
    array([ 0.,  1.])

    `meshgrid` is very useful to evaluate functions on a grid.

    >>> x = np.arange(-5, 5, 0.1)
    >>> y = np.arange(-5, 5, 0.1)
    >>> xx, yy = meshgrid(x, y, sparse=True)
    >>> z = np.sin(xx**2+yy**2)/(xx**2+yy**2)
    """
    copy = kwargs.get('copy', True)
    args = np.atleast_1d(*xi)
    if not isinstance(args, list):
        if args.size > 0:
            return args.copy() if copy else args
        else:
            raise TypeError('meshgrid() take 1 or more arguments (0 given)')

    sparse = kwargs.get('sparse', False)
    indexing = kwargs.get('indexing', 'xy')  # 'ij'

    ndim = len(args)
    s0 = (1,) * ndim
    output = [x.reshape(s0[:i] + (-1, ) + s0[i + 1::]) \
              for i, x in enumerate(args)]

    shape = [x.size for x in output]

    if indexing == 'xy':
        # switch first and second axis
        output[0].shape = (1, -1) + (1, ) * (ndim - 2)
        output[1].shape = (-1, 1) + (1, ) * (ndim - 2)
        shape[0], shape[1] = shape[1], shape[0]

    if sparse:
        if copy:
            return [x.copy() for x in output]
        else:
            return output
    else:
        # Return the full N-D matrix (not only the 1-D vector)
        if copy:
            mult_fact = np.ones(shape, dtype=int)
            return [x * mult_fact for x in output]
        else:
            return np.broadcast_arrays(*output)


def ndgrid(*args, **kwargs):
    """
    Same as calling meshgrid with indexing='ij' (see meshgrid for
    documentation).
    """
    kwargs['indexing'] = 'ij'
    return meshgrid(*args, **kwargs)


def odd_factorial_fn(k):
    f = k
    while k >= 3:
        k -= 2
        f *= k
    return f

odd_factorial = Memoize(odd_factorial_fn)


# From the scipy ticket
# http://projects.scipy.org/scipy/attachment/ticket/1296/assoc_legendre.py
def legendre(nu, mu, x):
    """Compute the associated Legendre polynomial with degree nu and order mu.
    This function uses the recursion formula in the degree nu.
    (Abramowitz & Stegun, Section 8.5.)
    """
    if mu < 0 or mu > nu:
        raise ValueError('require 0 <= mu <= nu, but mu=%d and nu=%d' \
                         % (nu, mu))
    if abs(x) > 1:
        raise ValueError('require -1 <= x <= 1, but x=%f', x)

    # Compute the initial term in the recursion.
    if mu == 0:
        p_nu = 1.0
    else:
        s = 1
        if mu & 1:
            s = -1
        z = sqrt(1 - x ** 2)
        p_nu = s * odd_factorial(2 * mu - 1) * z ** mu

    if mu == nu:
        return p_nu

    # Compute the next term in the recursion.
    p_nu_prev = p_nu
    p_nu = x * (2 * mu + 1) * p_nu

    if nu == mu + 1:
        return p_nu

    # Iterate the recursion relation.
    for n in xrange(mu + 2, nu + 1):
        result = (x * (2 * n - 1) * p_nu - (n + mu - 1) * p_nu_prev) / (n - mu)
        p_nu_prev = p_nu
        p_nu = result

    return result


if __name__ == '__main__':
    import doctest
    doctest.testmod()
