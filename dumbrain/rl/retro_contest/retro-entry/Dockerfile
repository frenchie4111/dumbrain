FROM openai/retro-agent:tensorflow

RUN apt-get update && \
    apt-get install -y libgtk2.0-dev && \
    rm -rf /var/lib/apt/lists/*

# Baselines has some unneeded and cumbersome dependencies,
# so we manually fetch the deps we need.
RUN . ~/venv/bin/activate && \
    pip install scipy tqdm joblib zmq dill progressbar2 cloudpickle opencv-python keras gym anyrl gym-retro && \
    pip install --no-deps git+https://github.com/openai/baselines.git

RUN . ~/venv/bin/activate && \
    pip install gputil retrowrapper losswise

RUN . ~/venv/bin/activate && \
    python --version && \
    pip install -U git+git://github.com/frenchie4111/dumbrain.git && \
    python -m dumbrain.rl.retro_contest.install_games
