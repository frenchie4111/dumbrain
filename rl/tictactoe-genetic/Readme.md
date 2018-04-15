# Tic Tac Toe - Genetic

In order to build some intuition around how competitive genetic algorithms
could work, I blindly implemented one here to play tic-tac-toe.

The training process works by doing the following:
 - Generating a population of players with randomized weights (players are a basic 2 layer NN)
 - Running N matches with two randomly chosen players
 - Some % of players with the most wins are "breeded" to make new population (averaged with some noise)
 - Process is repeated with new population

For validation, the players are run against a random player

See [notebook](tictactoe.ipynb)

## Genetic Lib

I have also started generalizing this algorithm into a library so that I can easily
test different strategies / games / etc.


## Future plans

 - Fix issue with ties not being properly counted (optimize for not-losing rather than winning)
 - Implement connect4 for a more advanced challenge
 - Implement a basic "play against the bot" script for fun
 - Implement a version of the decision that uses a combination of forward looking MDP and
 the current NN based approach
