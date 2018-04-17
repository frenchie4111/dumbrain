import random

import numpy as np

def getCard( sign=None ):
    """
    getCard returns a new card
    :param color: Valid: [-1, 1] The color of the card (red, black) (color determins if card is positive or negative) Omit for random
    >>> card = getCard( sign=-1 )
    >>> card < 0
    True
    >>> card = getCard( sign=1 )
    >>> card > 0
    True
    >>> cards = [getCard() for x in range( 1000 )]
    >>> max( cards ) == 10
    True
    >>> min( cards ) == -10 
    True
    """
    if sign is None:
        # 1/3 chance of -1, 2/3 chance of 1
        sign = np.random.choice( [ -1, 1, 1 ] )

    card = random.randint( 1, 10 )
    return card * sign

class Easy21State():
    def __init__( self, dealer_sum=None, player_sum=None, terminal=False ):
        if dealer_sum is None:
            dealer_sum = getCard(1)
        if player_sum is None:
            player_sum = getCard(1)
        self.dealer_sum = dealer_sum
        self.player_sum = player_sum
        self.terminal = terminal

    def __repr__( self ):
        return str([self.dealer_sum, self.player_sum, self.terminal])

    def state( self ):
        """
        >>> Easy21State( 1, 1 ).state()
        array([1, 1])
        """
        return np.array([ self.dealer_sum - 1, self.player_sum - 1 ])

    def clone( self ):
        return Easy21State( self.dealer_sum, self.player_sum, self.terminal )

class Easy21Environment():
    def __init__( self ):
        pass

    def getEmptyQSpace( self, dtype=np.float ):
        """
        Not sure of the best way to handle this
        dealer_sum, player_sum, action
        """
        return np.zeros( ( 10, 21, 2 ), dtype=dtype )

    def handleHit( self, state ):
        """
        >>> env = Easy21Environment()
        >>> before_state = Easy21State()
        >>> after_state, reward = env.handleHit( before_state )
        >>> before_state.player_sum != after_state.player_sum
        True
        >>> reward
        0
        >>> for i in range( 1000 ):
        ...     before_state, reward = env.handleHit( before_state )
        >>> before_state.terminal
        True
        >>> reward
        -1
        """
        state = state.clone()
        state.player_sum += getCard()
        if state.player_sum > 21 or state.player_sum < 1:
            state.terminal = True
            return state, -1
        return state, 0

    def handleStick( self, state ):
        """
        >>> env = Easy21Environment()
        >>> before_state = Easy21State()
        >>> after_state, reward = env.handleStick( before_state )
        >>> after_state.dealer_sum != before_state.dealer_sum and after_state.terminal
        True
        >>> reward
        -1
        """
        state = state.clone()
        while( state.dealer_sum < 17 ):
            state.dealer_sum += getCard()
        state.terminal = True
        if state.player_sum > state.dealer_sum: # Win
            return state, 1
        if state.player_sum < state.dealer_sum: # Lose
            return state, -1
        return state, 0 # Draw

    def step( self, state, action ):
        action_handlers = {
            0: self.handleHit,
            1: self.handleStick
        }
        state, reward = action_handlers[ action ]( state )
        return state, reward

if __name__ == '__main__':
    import doctest
    doctest.testmod()
