import argparse
import requests
import subprocess
import re
import os
from urllib.parse import urlparse

# === CONFIG ===
LOGIN_EMAIL = 'sdserver200@gmail.com'
PASSWORD = 'kk123456'
TWO_FACTOR_CODE = ''  # Kosongkan jika tidak pakai 2FA
OUTPUT_PATH = 'download'

# === UTILS ===
def is_valid_rapidgator_url(url):
    """Validasi format URL Rapidgator"""
    parsed = urlparse(url)
    return parsed.netloc == 'rapidgator.net' and '/file/' in parsed.path

def extract_file_id(url):
    """Ekstrak file ID dari URL Rapidgator"""
    match = re.search(r'/file/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None

def rapidgator_login(email, password, code=''):
    """Login ke Rapidgator dan dapatkan token"""
    login_url = 'https://rapidgator.net/api/v2/user/login'
    params = {'login': email, 'password': password, 'code': code}
    try:
        response = requests.get(login_url, params=params)
        data = response.json()
        if data.get('response'):
            return data['response']['token']
        print('Login gagal:', data.get('details', 'Unknown error'))
    except Exception as e:
        print('Error login:', e)
    return None

def download_file(file_id, token, output_dir):
    """Download file menggunakan API Rapidgator"""
    info_url = 'https://rapidgator.net/api/v2/file/info'
    dl_url = 'https://rapidgator.net/api/v2/file/download'
    
    # Dapatkan info file
    info = requests.get(info_url, params={'file_id': file_id, 'token': token}).json()
    if not info.get('response'):
        print(f'[ERROR] File ID {file_id} tidak valid')
        return False

    filename = info['response']['file']['name']
    filepath = os.path.join(output_dir, filename)

    # Dapatkan link download
    dl_data = requests.get(dl_url, params={'file_id': file_id, 'token': token}).json()
    if not dl_data.get('response'):
        print(f'[ERROR] Gagal mendapatkan link download untuk {filename}')
        return False

    # Download dengan aria2c
    try:
        subprocess.run([
            'aria2c', '-x', '16', '-s', '16',
            '-d', output_dir,
            '-o', filename,
            dl_data['response']['download_url']
        ], check=True)
        print(f'[SUKSES] Downloaded: {filename}')
        return True
    except subprocess.CalledProcessError as e:
        print(f'[ERROR] Gagal download {filename}: {e}')
        return False

# === MAIN ===
def main():
    parser = argparse.ArgumentParser(description='Downloader Rapidgator')
    parser.add_argument('--input-file', help='File teks berisi list URL Rapidgator', required=True)
    args = parser.parse_args()

    # Buat folder output
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    # Baca URL dari file
    with open(args.input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    # Validasi URL
    valid_urls = []
    for url in urls:
        if is_valid_rapidgator_url(url):
            valid_urls.append(url)
        else:
            print(f'[SKIP] URL tidak valid: {url}')

    if not valid_urls:
        print('Tidak ada URL valid untuk diproses!')
        return

    # Login
    token = rapidgator_login(LOGIN_EMAIL, PASSWORD, TWO_FACTOR_CODE)
    if not token:
        return

    # Proses download
    for url in valid_urls:
        file_id = extract_file_id(url)
        if file_id:
            download_file(file_id, token, OUTPUT_PATH)

if __name__ == '__main__':
    main()
