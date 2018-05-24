import abc

class RuleSet():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getBoardSize( self ):
        """Get the size of the board, as an integer (boards are always 1d)"""
        pass

    @abc.abstractmethod
    def getWinner( self, board ):
        """Return the winner of a given board"""
        pass

    def isValidMove( self, board, move ):
        """Return True is move is valid, else False"""
        return board[ move ] == 0

    def printBoard( self, board ):
        """Pretty print the board"""
        print( board )

class GenericRuleset( RuleSet ):
    def getBoardSize( self ):
        return 1

    def getWinner( self, board ):
        return board[ 0 ]

    def isValidMove( self, board, move ):
        return True
