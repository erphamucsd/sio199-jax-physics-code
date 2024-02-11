'''
Date: 2/1/2024
For storing all variables related to the model's grid space.
'''

import jax.numpy as np
from jax import jit

from params import kx, il, iy
from physical_constants import akap, omega

# Vertical level parameters
hsg = np.zeros(kx + 1) # Half sigma levels
dhs = np.zeros(kx) # Sigma level thicknesses
fsg = np.zeros(kx) # Full sigma levels
dhsr = np.zeros(kx) # 1/(2*sigma level thicknesses)
fsgr = np.zeros(kx) # akap/(2*full sigma levels)

# Functions of latitude and longitude
radang = np.zeros(il) # Latitudes in radians
coriol = np.zeros(il) # Coriolis parameter as a function of latitude
sia = np.zeros(il) # sine(latitude)
coa = np.zeros(il) # cosine(latitude)
sia_half = np.zeros(iy) # sine(latitude) over one hemisphere only
coa_half = np.zeros(iy) # cosine(latitude) over one hemisphere only
cosg = np.zeros(il) # Same as coa (TODO: remove)
cosgr = np.zeros(il) # 1/coa
cosgr2 = np.zeros(il) # 1/coa^2

@jit
def initialize_geometry(hsg, dhs, fsg, dhsr, fsgr, radang, coriol, sia, coa, sia_half, coa_half, cosg, cosgr, cosgr2):

    # Definition of model levels
    if kx == 5:
        hsg[:6] = np.array([0.000, 0.150, 0.350, 0.650, 0.900, 1.000])
    elif kx == 7:
        hsg[:8] = np.array([0.020, 0.140, 0.260, 0.420, 0.600, 0.770, 0.900, 1.000])
    elif kx == 8:
        hsg[:9] = np.array([0.000, 0.050, 0.140, 0.260, 0.420, 0.600, 0.770, 0.900, 1.000])

    '''
    # Layer thicknesses and full (u,v,T) levels
    for k in range(1, kx + 1):
        dhs[k - 1] = hsg[k] - hsg[k - 1]
        fsg[k - 1] = 0.5 * (hsg[k] + hsg[k - 1])
    '''

    # Layer thicknesses and full (u,v,T) levels
    dhs = hsg[1:] - hsg[:-1]
    fsg = 0.5 * (hsg[1:] + hsg[:-1])

    '''
    # Additional functions of sigma
    for k in range(1, kx + 1):
        dhsr[k - 1] = 0.5 / dhs[k - 1]
        fsgr[k - 1] = akap / (2. * fsg[k - 1])
    '''

    # Additional functions of sigma
    dhsr = 0.5 / dhs
    fsgr = akap / (2.0 * fsg)

    # Horizontal functions

    '''
    # Latitudes and functions of latitude
    # NB: J=1 is Southernmost point!
    for j in range(1, iy + 1):
        jj = il + 1 - j
        sia_half[j - 1] = np.cos(3.141592654 * (j - 0.25) / (il + 0.5))
        coa_half[j - 1] = np.sqrt(1.0 - sia_half[j - 1] ** 2.0)
        sia[j - 1] = -sia_half[j - 1]
        sia[jj - 1] = sia_half[j - 1]
        coa[j - 1] = coa_half[j - 1]
        coa[jj - 1] = coa_half[j - 1]
        radang[j - 1] = -np.arcsin(sia_half[j - 1])
        radang[jj - 1] = np.arcsin(sia_half[j - 1])
    '''

    # Latitudes and functions of latitude
    # NB: J=1 is Southernmost point!
    j = np.arange(1, iy + 1)
    jj = il + 1 - j

    sia_half = np.cos(3.141592654 * (j - 0.25) / (il + 0.5))
    coa_half = np.sqrt(1.0 - sia_half ** 2.0)

    sia = -sia_half
    sia = np.where(jj > 0, np.concatenate([sia_half, sia_half[::-1]]), sia)

    coa = coa_half
    coa = np.where(jj > 0, np.concatenate([coa_half, coa_half[::-1]]), coa)

    radang = -np.arcsin(sia_half)
    radang = np.where(jj > 0, np.concatenate([radang, radang[::-1]]), radang)

    '''
    # Expand cosine and its reciprocal to cover both hemispheres
    for j in range(1, iy + 1):
        jj = il + 1 - j
        cosg[j - 1] = coa_half[j - 1]
        cosg[jj - 1] = coa_half[j - 1]
        cosgr[j - 1] = 1. / coa_half[j - 1]
        cosgr[jj - 1] = 1. / coa_half[j - 1]
        cosgr2[j - 1] = 1. / (coa_half[j - 1] ** 2)
        cosgr2[jj - 1] = 1. / (coa_half[j - 1] ** 2)
    '''

    # Expand cosine and its reciprocal to cover both hemispheres
    cosg = coa_half
    cosg = np.where(jj > 0, np.concatenate([cosg, cosg[::-1]]), cosg)

    cosgr = 1. / coa_half
    cosgr = np.where(jj > 0, np.concatenate([cosgr, cosgr[::-1]]), cosgr)

    cosgr2 = 1. / (coa_half ** 2)
    cosgr2 = np.where(jj > 0, np.concatenate([cosgr2, cosgr2[::-1]]), cosgr2)

    coriol = 2.0 * omega * sia

    return hsg, dhs, fsg, dhsr, fsgr, radang, coriol, sia, coa, sia_half, coa_half, cosg, cosgr, cosgr2

# Initialize geometry
initialize_geometry()