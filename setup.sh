#!/bin/bash

mkdir ~/os_search
cd ~/os_search

python3 -m venv venv
source "./venv/bin/activate"

pip install transformers
pip install langchain
pip install langchain-huggingface
pip install langchain-community
pip install chromadb langchain-chroma
pip install pypdf
