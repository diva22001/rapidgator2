#!/bin/bash
set -e

# Install dependensi
sudo apt-get update -y
sudo apt-get install -y rclone  # Install Rclone
pip install requests

# Unduh dan jalankan rapidgator.py
curl -o rapidgator.py https://raw.githubusercontent.com/Bogyi2024/log/main/dep_download/rapidgator.py
python rapidgator.py

# Konfigurasi Rclone dan upload ke Google Drive
rclone copy ./download gdrive:remote_folder -P  # Ganti 'remote_folder' dengan nama folder tujuan
