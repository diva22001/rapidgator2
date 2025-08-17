#!/bin/bash
set -e

# Install required Python packages
pip install requests
pip install huggingface-hub

# Download rapidgator.py and run it
curl -o rapidgator.py https://raw.githubusercontent.com/Bogyi2024/log/main/dep_download/rapidgator.py
python rapidgator.py

# Download huggingface.py and run it
curl -o huggingface.py https://raw.githubusercontent.com/Bogyi2024/log/main/dep_download/huggingface.py
python huggingface.py
