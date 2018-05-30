from keras import models
import tensorflow as tf
import numpy as np

from batched_env_wrappers import BatchedObservationWrapper

class CollisionMapWrapper( BatchedObservationWrapper ):
    """
    This wrapper performs the final operations for our model input. The output observations are
    a 2 channel image. Channel 1 is the collision map, generated with a loaded keras model, channel
    2 is the grayscale version of the image.


    About Color Correction: 
        The genesis that Sonic run on uses 9bit color and the emulator upsamples the color differently
    than the collision mapper. To solve for this we divide the colors by 32, floor, and multiply by 32. 
    This forces the collision mapper colors and observation colors to be equal.
    """
    def __init__( self, env, model_file='models/collision-model-20180525-005107.h5', **args ):
        self.model = models.load_model( model_file )

        self._sess = tf.Session()
        self._images = tf.placeholder( tf.float32, shape=( None, ) + env.observation_space.shape )

        self._correction_constant = tf.constant( 32, dtype=tf.float32 )
        self._normalization_constant = tf.constant( 255, dtype=tf.float32 )

        self._color_corrected_images = tf.floor( self._images / self._correction_constant ) * self._correction_constant

        self._grayscale = tf.image.rgb_to_grayscale( self._color_corrected_images )

        self._normalized_color_corrected_images = self._color_corrected_images / self._normalization_constant

        super( CollisionMapWrapper, self ).__init__( env, **args )
    
    def observation( self, obses ):
        normalized_color_corrected_images, grayscale = self._sess.run( [ self._normalized_color_corrected_images, self._grayscale ], { self._images: obses } )

        col_map = self.model.predict( normalized_color_corrected_images )

        # mult by 255, because the anyrl-py rainbow dqn automatically scales inputs down by 1/255
        test_zeros = np.zeros( grayscale.shape, dtype=np.int32 )
        grayscale = grayscale.astype( np.int32 )

        # return np.concatenate( ( col_map * 255, grayscale ), axis=-1 )
        cat = np.concatenate( ( test_zeros, grayscale ), axis=-1 )
        # print( cat )
        return cat

if __name__ == '__main__':
    import retro
    import matplotlib
    import matplotlib.pyplot as plt

    env = retro.make(
        game='SonicTheHedgehog2-Genesis', 
        state='MetropolisZone.Act1', 
        record='data/record/' 
    )
    wrapper = CollisionMapWrapper( env )

    fig, ( ax1, ax2, ax3 ) = plt.subplots( 1, 3 )

    ax1.xaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    ax2.xaxis.set_visible(False)
    ax2.yaxis.set_visible(False)
    ax3.xaxis.set_visible(False)
    ax3.yaxis.set_visible(False)

    obs = env.reset()

    env_im = ax1.imshow( obs )

    output = wrapper.observation( [ obs ] )

    print( output.shape )

    ax2.imshow( output[ 0, :, :, 0 ] )
    ax3.imshow( output[ 0, :, :, 1 ] )

    plt.show()
