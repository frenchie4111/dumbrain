import retro
import scipy.misc
import matplotlib.pyplot as plt
import os
import numpy as np
import time

from TemplateMatcher import TemplateMatcher

def imageTo8BitColor( image ):
    assert image.shape[ -1 ] == 3 or image.shape[ -1 ] == 4
    
    output_image = np.zeros( image.shape[ 0 : 2 ], dtype=np.uint8 )

    output_image[ :, : ]  = ( image[ :, :, 0 ] / 32 ).astype( np.uint8 ) * 32 # << 4
    output_image[ :, : ] += ( image[ :, :, 1 ] / 32 ).astype( np.uint8 ) * 4  # << 2 
    output_image[ :, : ] += ( image[ :, :, 2 ] / 64 ).astype( np.uint8 )
    
    alpha = None
    if image.shape[ -1 ] == 4:
        alpha = image[ :, :, 3 ]

    return output_image, alpha

class EightBitTemplateMatcher( TemplateMatcher ):
    def preprocessFrame( self, frame ):
        return imageTo8BitColor( frame )[ 0 ]

    def preprocessTemplate( self, template ):
        return imageTo8BitColor( template )
