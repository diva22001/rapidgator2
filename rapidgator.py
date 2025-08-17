import argparse
import requests
import subprocess
import re
import os

# === CONFIG ===
login_email = 'sdserver200@gmail.com'
password = 'kk123456'
two_factor_code = ''
output_path = 'download'

def extract_file_id(url):
    """Ekstrak file ID dari URL Rapidgator"""
    match = re.search(r'/file/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', help='File berisi list URL Rapidgator')
    args = parser.parse_args()

    # Baca URL dari file input
    with open(args.input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    # Ekstrak file IDs
    file_ids = []
    for url in urls:
        file_id = extract_file_id(url)
        if file_id:
            file_ids.append(file_id)
        else:
            print(f"URL tidak valid: {url}")

    if not file_ids:
        print("Tidak ada file ID yang valid!")
        return

    # Proses download (sisa kode tetap sama)
    token = rapidgator_login(login_email, password, two_factor_code)
    if not token:
        return

    for file_id in file_ids:
        download_file(file_id, token)

if __name__ == "__main__":
    main()
