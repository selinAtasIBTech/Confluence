import urllib.request
import json
import os
import re
import unicodedata
from html import unescape

# === Configuration ===
BASE_URL = "https://sdlc.ibtech.com.tr:444/confluence"
ROOT_PAGE_ID = "247638695"  # Change this to your root page ID

# === Load token from .env file ===
def load_token_from_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("CONFLUENCE_TOKEN="):
                return line.strip().split("=", 1)[1]
    raise Exception("Token not found in .env file!")

TOKEN = load_token_from_env()

# === Prepare API headers ===
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

# === Sanitize names for file/folder compatibility ===
def sanitize_name(name, max_length=30):
    import re, unicodedata

    # Replace Turkish characters
    replacements = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o',
        'ş': 's', 'ü': 'u',
        'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U',
    }
    for src, target in replacements.items():
        name = name.replace(src, target)

    # Normalize to ASCII
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')

    # Remove forbidden characters including dot (.)
    name = re.sub(r'[<>:"/\\|?*.\n\r\t]', '', name)
    name = re.sub(r'\s+', '_', name)  # replace spaces with underscores
    name = name.strip().lower()

    if not name:
        name = "untitled"

    return name[:max_length]



# === Strip HTML tags and decode entities ===
def html_to_text(html):
    text = re.sub(r'<[^>]+>', '', html)
    return unescape(text).strip()

# === Send GET request and return JSON ===
def send_request(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

# === Get all child pages (with pagination) ===
def get_child_pages(page_id):
    all_pages = []
    limit = 100
    start = 0
    while True:
        url = f"{BASE_URL}/rest/api/content/{page_id}/child/page?expand=body.storage&limit={limit}&start={start}"
        data = send_request(url)
        results = data.get("results", [])
        all_pages.extend(results)
        if len(results) < limit:
            break
        start += limit
    return all_pages

# === Save page content as .txt ===
def save_page_as_txt(page, folder_path):
    file_name = f"{page['id']}.txt"
    file_path = os.path.join(folder_path, file_name)

    if os.name == 'nt':
        file_path = r'\\?\\' + os.path.abspath(file_path)

    raw_html = page["body"]["storage"]["value"]
    plain_text = html_to_text(raw_html)

    with open(file_path, "w", encoding="utf-8") as file:
        # Add title at the top of the file
        file.write(f"### {page['title']}\n\n")
        file.write(plain_text)
    
    print(f"[✓] Saved: {file_path}")


def process_page_and_children(page_id, parent_folder):
    pages = get_child_pages(page_id)
    print(f"[•] Found {len(pages)} child pages under ID {page_id}")

    for page in pages:
        short_title = sanitize_name(page["title"])
        subfolder_name = f"{short_title}_{page['id']}"
        current_folder = os.path.join(parent_folder, subfolder_name)

        if os.name == 'nt':
            current_folder = r'\\?\\' + os.path.abspath(current_folder)

        os.makedirs(current_folder, exist_ok=True)

        print(f"→ Processing: {page['title']}")
        save_page_as_txt(page, current_folder)
        process_page_and_children(page["id"], current_folder)



# === Recursively process pages and create folders ===
def process_page_and_children(page_id, parent_folder):
    pages = get_child_pages(page_id)
    print(f"[•] Found {len(pages)} child pages under ID {page_id}")

    for page in pages:
        title = sanitize_name(page["title"])
        current_folder = os.path.join(parent_folder, title)
        os.makedirs(current_folder, exist_ok=True)

        print(f"→ Processing: {title}")
        save_page_as_txt(page, current_folder)

        # Recursive call
        process_page_and_children(page["id"], current_folder)

# === Get root page title to name the main folder ===
def get_page_title(page_id):
    url = f"{BASE_URL}/rest/api/content/{page_id}"
    data = send_request(url)
    return sanitize_name(data["title"])

# === Entry point ===
def main():
    root_title = get_page_title(ROOT_PAGE_ID)
    root_folder = os.path.join(os.getcwd(), root_title)
    os.makedirs(root_folder, exist_ok=True)

    print(f"[🔍] Starting export for: {root_title} (ID: {ROOT_PAGE_ID})")
    process_page_and_children(ROOT_PAGE_ID, root_folder)

if __name__ == "__main__":
    main()
