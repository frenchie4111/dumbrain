#!/bin/bash

paperspace jobs create \
    --container "frenchie4111/anyrl-openai-gym:0.1" \
    --machineType "P100" \
    --command "python rainbow.py" \
    --ports 8888:22