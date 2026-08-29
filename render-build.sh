#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install ffmpeg on Render
apt-get update && apt-get install -y ffmpeg