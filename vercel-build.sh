#!/bin/bash

# install dependencies
pip install -r requirements.txt

# remove unnecessary files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# create necessary directories
mkdir -p /vercel/output/static
mkdir -p /vercel/output/templates

# copy only necessary files
cp -r app /vercel/output/
cp run.py /vercel/output/
cp -r static /vercel/output/static
cp -r templates /vercel/output/templates