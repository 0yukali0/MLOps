#!/bin/bash
source .venv/bin/activate
python main.py > nohup.log 2>&1
