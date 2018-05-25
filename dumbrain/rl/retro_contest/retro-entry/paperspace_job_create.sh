#!/bin/bash

paperspace jobs create \
    --container "frenchie4111/anyrl-openai-gym:0.1" \
    --machineType "P4000" \
    --command "python train.py /artifacts/model/" \
    --ports 8888:22