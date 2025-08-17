import requests
import subprocess
import re
import os

# === CONFIG ===
login_email = 'sdserver200@gmail.com'
password = 'kk123456'
two_factor_code = ''  # Leave blank if 2FA not enabled
pastebin_link = "https://pastebin.com/raw/EBiRrTGp?nocache=1"
output_path = 'download'

# === UTILS ===

# Resolve shortened links like tinyurl, bit.ly
def resolve_short_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        final_url = response.url
        print(f"Resolved {url} -> {final_url}")
        return final_url
    except Exception as e:
        print(f"Failed to resolve short URL {url}: {e}")
        return url

# Extract file IDs from Pastebin URLs
def fetch_links_from_pastebin(pastebin_link):
    try:
        response = requests.get(pastebin_link)
        response.raise_for_status()
        urls = response.text.strip().split('\n')
        file_ids = []
        for url in urls:
            resolved_url = resolve_short_url(url)
            match = re.search(r'/file/([a-zA-Z0-9]{32})', resolved_url)
            if match:
                file_id = match.group(1)
                file_ids.append(file_id)
        print("File IDs extracted:", file_ids)
        return file_ids
    except Exception as e:
        print("Error fetching links from Pastebin:", e)
        return []

# Login to Rapidgator
def rapidgator_login(email, password, code=''):
    login_url = 'https://rapidgator.net/api/v2/user/login'
    login_params = {
        'login': email,
        'password': password,
        'code': code
    }
    try:
        response = requests.get(login_url, params=login_params)
        data = response.json()
        if response.status_code == 200 and data.get('response'):
            token = data['response']['token']
            print('Login successful.')
            return token
        else:
            print('Login failed:', data.get('details', 'Unknown error'))
            return None
    except Exception as e:
        print("Login error:", e)
        return None

# === MAIN ===
if __name__ == "__main__":
    # Make sure output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Step 1: Login
    token = rapidgator_login(login_email, password, two_factor_code)
    if not token:
        exit()
#    token = "mufsvol931dus8ftda3g27forn"
    # Step 2: Extract file IDs from Pastebin
    file_ids = fetch_links_from_pastebin(pastebin_link)
    if not file_ids:
        print("No valid file IDs found.")
        exit()

    # URLs
    info_url = 'https://rapidgator.net/api/v2/file/info'
    download_url = 'https://rapidgator.net/api/v2/file/download'

    # Step 3: Loop over files
    for file_id in file_ids:
        # Get file info
        info_params = {
            'file_id': file_id,
            'token': token
        }
        try:
            info_response = requests.get(info_url, params=info_params)
            info_data = info_response.json()
        except Exception as e:
            print(f"Failed to get info for {file_id}: {e}")
            continue

        if info_response.status_code == 200 and info_data.get('response'):
            file_info = info_data['response']['file']
            filename = file_info['name']
            print(f"File found: {filename}")

            # Get download URL
            download_params = {
                'file_id': file_id,
                'token': token
            }
            try:
                dl_response = requests.get(download_url, params=download_params)
                dl_data = dl_response.json()
            except Exception as e:
                print(f"Failed to get download URL: {e}")
                continue

            if dl_response.status_code == 200 and dl_data.get('response'):
                download_link = dl_data['response']['download_url']
                print(f"Downloading {filename}...")

                try:
                    subprocess.run([
                        'aria2c', '-x', '16',
                        '-d', output_path,
                        '-o', filename,
                        download_link
                    ], check=True)
                    print(f"Downloaded: {filename}")
                except subprocess.CalledProcessError as e:
                    print(f"aria2c failed for {filename}: {e}")
            else:
                print(f"Failed to get download URL for {filename}")
        else:
            print(f"Could not fetch info for file ID: {file_id}")
