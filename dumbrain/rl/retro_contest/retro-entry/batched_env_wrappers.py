import tensorflow as tf

from abc import ABCMeta, abstractmethod
from anyrl.envs.wrappers import BatchedWrapper

import gym

class BatchedObservationWrapper( BatchedWrapper ):
    __metaclass__ = ABCMeta

    def __init__( self, env, **args ):
        super( BatchedObservationWrapper, self ).__init__( env, **args )
        old_space = env.observation_space
        low, high = self.observation( [ old_space.low, old_space.high ] )
        self.observation_space = gym.spaces.Box( low, high, dtype=old_space.dtype )

    @abstractmethod
    def observation( self, obses ):
        pass

    def reset_wait( self, **args ):
        obses = super().reset_wait( **args )
        obses = self.observation( obses )
        return obses

    def step_wait( self, **args ):
        obses, rews, dones, infos = super().step_wait( **args )
        obses = self.observation( obses )
        return obses, rews, dones, infos

class BatchedResizeImageWrapper( BatchedObservationWrapper ):
    def __init__( self, env, size=( 84, 84 ), method=tf.image.ResizeMethod.AREA, **args ):
        config = tf.ConfigProto( device_count={ 'GPU': 0 } )
        self._sess = tf.Session( config=config )
        self._images = tf.placeholder( tf.float32, shape=( None, ) + env.observation_space.shape )
        self._resized = tf.cast( tf.image.resize_images( self._images, size, method=method ), tf.int32 )

        super( BatchedResizeImageWrapper, self ).__init__( env, **args )

    def observation( self, obses ):
        return self._sess.run( self._resized, { self._images: obses } )
