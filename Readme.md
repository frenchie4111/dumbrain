# Dumbrain

A place to put all my random projects and tools for ai/ml/rl stuff

## Python module

This project is designed as an installable python module so that you can easily
use some of the built in tools.

```
pip install -U git+git://github.com/frenchie4111/dumbrain.git
```

```
from dumbrain.lib.download import downloadAndUnzip
downloadAndUnzip( 'http://aiml.mikelyons.org/datasets/sonic/Sonic%20Roms.zip', 'data/roms/' )
```

## Subdirectories

 - [dumbrain/ml](dumbrain/ml/) Machine Learning (Mostly Deep Learning) related things
     - [Fast.ai](dumbrain/ml/fast.ai) Some of the fast.ai lecture notes
     - [Kaggle](dumbrain/ml/kaggle) Kaggle entry related stuff
     - [Omniglot](dumbrain/ml/omniglot) Implementation of prototype networks to solve the
     Omniglot few-shot learning problem
     - [tensorflow](dumbrain/ml/tensorflow) A few super basic tensorflow tutorial
     solutions
 - [dumbrain/rl](dumbrain/rl/) Reinforcement Learning related things
     - [cartpole](dumbrain/rl/cartpole) Solutions for the cartpole problem from the
     [OpenAI Requests from Research](https://openai.com/requests-for-research/#cartpole)
     - [David Silver's RL Lectures](dumbrain/rl/david_silver_rl_lectures) Implementation of
     the easy21 excersize and a few other things discussed during the lectures
     - [OpenAI Sonic Retro Contest Entry](dumbrain/rl/retro_contest) A couple
     different projects I worked on as solutions the RL transfer learning competition
     put on by OpenAI in May-June 2018
     - [Genetic Tictactoe Gameplaying Algorithm/Genetic Lib](dumbrain/rl/tictactoe-genetic)
     Implementation of a simple deep genetic algorithm for playing tic-tac-toe, as well
     as a generic game library for testing game playing algorithms on arbitrary rulesets
