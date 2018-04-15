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
    def __init__( self, dealer_sum=getCard( 1 ), player_sum=getCard( 1 ), terminal=False ):
        self.dealer_sum = dealer_sum
        self.player_sum = player_sum
        self.terminal = terminal

    def __repr__( self ):
        return str([self.dealer_sum, self.player_sum, self.terminal])

    def clone( self ):
        return Easy21State( self.dealer_sum, self.player_sum, self.terminal )

class Easy21Environment():
    def __init__( self ):
        pass

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
        if state.player_sum > 21:
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
            0: self.handleHit( state ),
            1: self.handleStick( state )
        }
        state, reward = action_handlers[ action ]( state )
        return state, reward

if __name__ == '__main__':
    import doctest
    doctest.testmod()
