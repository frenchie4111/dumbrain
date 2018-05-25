#!/bin/bash

source openai_login.secret.sh

docker build -t $DOCKER_REGISTRY/retro-entry:dqn.v2 -f Dockerfile.evaluate .
docker push $DOCKER_REGISTRY/retro-entry:dqn.v2

retro-contest job submit -t $DOCKER_REGISTRY/retro-entry:dqn.v2
