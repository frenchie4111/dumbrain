import gym
import numpy as np
from collections import deque

class AllowBacktracking(gym.Wrapper):
    """
    Use deltas in max(X) as the reward, rather than deltas
    in X. This way, agents are not discouraged too heavily
    from exploring backwards if there is no way to advance
    head-on in the level.
    """
    def __init__(self, env):
        super(AllowBacktracking, self).__init__(env)
        self._cur_x = 0
        self._max_x = 0

    def reset(self, **kwargs): # pylint: disable=E0202
        self._cur_x = 0
        self._max_x = 0
        return self.env.reset(**kwargs)

    def step(self, action): # pylint: disable=E0202
        obs, rew, done, info = self.env.step(action)
        self._cur_x += rew
        rew = max(0, self._cur_x - self._max_x)
        self._max_x = max(self._max_x, self._cur_x)
        return obs, rew, done, info

class Render(gym.Wrapper):
    def step(self, action): # pylint: disable=E0202
        obs, rew, done, info = self.env.step(action)
        self.env.render()
        return obs, rew, done, info

class SonicDiscretizer(gym.ActionWrapper):
    """
    Wrap a gym-retro environment and make it use discrete
    actions for the Sonic game.
    """
    def __init__(self, env):
        super(SonicDiscretizer, self).__init__(env)
        buttons = ["B", "A", "MODE", "START", "UP", "DOWN", "LEFT", "RIGHT", "C", "Y", "X", "Z"]
        actions = [['LEFT'], ['RIGHT'], ['LEFT', 'DOWN'], ['RIGHT', 'DOWN'], ['DOWN'],
                   ['DOWN', 'B'], ['B']]
        self._actions = []
        for action in actions:
            arr = np.array([False] * 12)
            for button in action:
                arr[ buttons.index( button ) ] = True
            self._actions.append( arr )
        self.action_space = gym.spaces.Discrete(len(self._actions))

    def action(self, a): # pylint: disable=W0221
        return self._actions[ a ].copy()

class StuckReset(gym.Wrapper):
    def __init__(self, env):
        super(StuckReset, self).__init__(env)
        self.last_rewards = deque( maxlen=100 )

    def reset(self, **kwargs): # pylint: disable=E0202
        self.last_rewards = deque( maxlen=100 )
        return self.env.reset(**kwargs)

    def step(self, action): # pylint: disable=E0202
        obs, rew, done, info = self.env.step(action)

        self.last_rewards.append( rew )
        if( len( self.last_rewards ) == 100 ):
            sum_of_last_rewards = 0
            for i in self.last_rewards:
                sum_of_last_rewards += abs( i )
            if( sum_of_last_rewards < 20 ):
                print( 'Resetting due to lack of movement' )
                done = True
                rew = -100

        return obs, rew, done, info
