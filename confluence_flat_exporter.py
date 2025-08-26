import urllib.request
import json
import os
import re
import unicodedata
from html import unescape

# === Configuration ===
BASE_URL = "https://sdlc.ibtech.com.tr:444/confluence"
ROOT_PAGE_ID = "2753081"  # root page ID

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

# === Sanitize name (for filename)
def sanitize_name(name, max_length=30):
    replacements = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o',
        'ş': 's', 'ü': 'u',
        'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U',
    }
    for src, target in replacements.items():
        name = name.replace(src, target)

    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    name = re.sub(r'[<>:"/\\|?*.\n\r\t]', '', name)
    name = re.sub(r'\s+', '_', name)
    name = name.strip().lower()

    return name[:max_length] if name else "untitled"

# === HTML to plain text
def html_to_text(html):
    text = re.sub(r'<[^>]+>', '', html)
    return unescape(text).strip()

# === Send GET request
def send_request(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

# === Get child pages (paginated)
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

# === Save all content into a single .txt file
def process_and_append_pages(page_id, file_handle):
    pages = get_child_pages(page_id)
    print(f"[•] Found {len(pages)} child pages under ID {page_id}")

    for page in pages:
        print(f"→ Processing: {page['title']}")
        raw_html = page["body"]["storage"]["value"]
        plain_text = html_to_text(raw_html)

        file_handle.write(f"\n\n{'='*80}\n")
        file_handle.write(f"### {page['title']} (ID: {page['id']})\n\n")
        file_handle.write(plain_text)
        file_handle.write(f"\n{'='*80}\n")

        # Recursive
        process_and_append_pages(page["id"], file_handle)

# === Get root title to name the file
def get_page_title(page_id):
    url = f"{BASE_URL}/rest/api/content/{page_id}"
    data = send_request(url)
    return sanitize_name(data["title"])

# === Main runner
def main():
    root_title = get_page_title(ROOT_PAGE_ID)
    output_file = os.path.join(os.getcwd(), f"{root_title}_{ROOT_PAGE_ID}.txt")

    if os.name == 'nt':
        output_file = r'\\?\\' + os.path.abspath(output_file)

    print(f"[🔍] Starting flat export for: {root_title} (ID: {ROOT_PAGE_ID})")
    
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(f"# Export from Confluence Root Page: {root_title} (ID: {ROOT_PAGE_ID})\n")
        file.write("="*80 + "\n")
        process_and_append_pages(ROOT_PAGE_ID, file)

    print(f"[✅] All content written to: {output_file}")

if __name__ == "__main__":
    main()
