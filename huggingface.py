import os
import requests
import base64
from huggingface_hub import login, HfApi

# Step 1: Fetch repo name from Pastebin
pastebin_raw_url = "https://pastebin.com/raw/i39Dh6CM"
response = requests.get(pastebin_raw_url)

if response.status_code != 200:
    raise Exception("Failed to fetch Pastebin content")

repo_name = response.text.strip()
if not repo_name:
    raise ValueError("Pastebin content is empty. Expected a repo name.")

# Step 2: Decode Hugging Face token (Base64)
encoded_token = "aGZfenFpcWNqdU1uSmVhWVBVZWRZWGtjS0NmWVhxbXBMU2lmQw=="
write_token = base64.b64decode(encoded_token).decode()

# Step 3: Login
login(write_token, add_to_git_credential=True)
api = HfApi()
#print(api.whoami())


# Step 4: Create repo if it doesn't exist
user = api.whoami(token=write_token)
model_repo = f"{user['name']}/{repo_name}"

if not api.repo_exists(repo_id=model_repo, token=write_token):
    api.create_repo(repo_id=model_repo, token=write_token)
    print(f"Model repo '{model_repo}' didn't exist — created.")
else:
    print(f"Model repo '{model_repo}' already exists.")

# Step 5: Upload all files in the 'download' folder
folder_path = "download"
commit_message = "Upload with Github"

if os.path.isdir(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            print(f"Uploading {file_name} to {model_repo}...")
            api.upload_file(
                path_or_fileobj=file_path,
                path_in_repo=file_name,
                repo_id=model_repo,
                commit_message=commit_message,
                token=write_token,
            )
else:
    print(f"Invalid folder path: {folder_path}")
