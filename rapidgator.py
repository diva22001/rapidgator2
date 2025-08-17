import argparse
import requests
import subprocess
import re
import os
from urllib.parse import urlparse

# === KONFIGURASI ===
LOGIN_EMAIL = os.getenv('RAPIDGATOR_EMAIL', 'sdserver200@gmail.com')  # Gunakan Secrets
PASSWORD = os.getenv('RAPIDGATOR_PASSWORD', 'kk123456')               # Gunakan Secrets
TWO_FACTOR_CODE = ''
OUTPUT_PATH = 'download'

# === FUNGSI UTAMA ===
def is_valid_rapidgator_url(url):
    """Validasi format URL Rapidgator"""
    parsed = urlparse(url)
    return parsed.netloc == 'rapidgator.net' and '/file/' in parsed.path

def extract_file_id(url):
    """Ekstrak file ID dari URL"""
    match = re.search(r'/file/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None

def rapidgator_login(email, password, code=''):
    """Login ke Rapidgator API"""
    try:
        response = requests.get(
            'https://rapidgator.net/api/v2/user/login',
            params={'login': email, 'password': password, 'code': code}
        )
        data = response.json()
        if data.get('response'):
            return data['response']['token']
        print(f"Login gagal: {data.get('details', 'Unknown error')}")
    except Exception as e:
        print(f"Error login: {e}")
    return None

def download_file(file_id, token, output_dir):
    """Download file menggunakan API"""
    try:
        # Dapatkan info file
        info = requests.get(
            'https://rapidgator.net/api/v2/file/info',
            params={'file_id': file_id, 'token': token}
        ).json()

        if not info.get('response'):
            print(f"[ERROR] File ID {file_id} tidak valid")
            return False

        filename = info['response']['file']['name']
        filepath = os.path.join(output_dir, filename)

        # Dapatkan link download
        dl_data = requests.get(
            'https://rapidgator.net/api/v2/file/download',
            params={'file_id': file_id, 'token': token}
        ).json()

        if not dl_data.get('response'):
            print(f"[ERROR] Gagal mendapatkan link download untuk {filename}")
            return False

        # Proses download dengan aria2c
        subprocess.run([
            'aria2c', '-x', '16', '-s', '16',
            '-d', output_dir,
            '-o', filename,
            dl_data['response']['download_url']
        ], check=True)
        print(f"[SUKSES] Downloaded: {filename}")
        return True

    except Exception as e:
        print(f"[ERROR] Gagal download file ID {file_id}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', required=True, help='File teks berisi URL Rapidgator')
    args = parser.parse_args()

    # Buat folder output
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    # Baca dan validasi URL
    with open(args.input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    valid_urls = [url for url in urls if is_valid_rapidgator_url(url)]
    if not valid_urls:
        print("Tidak ada URL valid!")
        return

    # Login
    token = rapidgator_login(LOGIN_EMAIL, PASSWORD, TWO_FACTOR_CODE)
    if not token:
        return

    # Proses semua URL
    for url in valid_urls:
        file_id = extract_file_id(url)
        if file_id:
            download_file(file_id, token, OUTPUT_PATH)

if __name__ == "__main__":
    main()
