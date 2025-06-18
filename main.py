import os
import requests
import re
from urllib.parse import unquote

def extract_file_and_node_id(url):
    match = re.search(r"figma.com/(?:file|design)/([a-zA-Z0-9]+)(?:/[^?]*)?(?:\?.*?node-id=([^&]+))?", url)
    if not match:
        print(f"❌ Could not parse Figma URL: {url}")
        return None, None

    file_key = match.group(1)
    node_id = match.group(2)
    if node_id:
        node_id = unquote(node_id)
        node_id = node_id.replace(":", "%3A")
    else:
        print(f"❌ No node ID found in Figma URL: {url}")

    return file_key, node_id

def get_database_rows():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["results"]

def update_notion_page(page_id, image_url):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    data = {
        "properties": {
            "Thumbnail": {
                "type": "files",
                "files": [
                    {"type": "external", "name": "Figma Image", "external": {"url": image_url}}
                ]
            }
        }
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ Updated Notion page thumbnail.")
    else:
        print("❌ Failed to update Notion page.", response.text)

def fetch_figma_image(file_key, node_id):
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&format=jpg"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to fetch JPG from Figma API.", response.text)
        return None

    image_url = response.json().get("images", {}).get(node_id)
    print("🖼️ Image URL:", image_url)
    return image_url

if __name__ == "__main__":
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    DATABASE_ID = os.getenv("DATABASE_ID")
    FIGMA_PROPERTY = os.getenv("FIGMA_PROPERTY")
    FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")

    rows = get_database_rows()
    print(f"✅ Found {len(rows)} rows in Notion DB.")

    for row in rows:
        page_id = row["id"]
        figma_url = row["properties"].get(FIGMA_PROPERTY, {}).get("url")
        if not figma_url:
            print(f"⚠️ No Figma URL found for page {page_id}")
            continue

        print(f"🔍 Processing: {row['properties'].get('Name', {}).get('title', [{'text': {'content': page_id}}])[0]['text']['content']} (Page ID: {page_id})")
        print("🔗 Figma URL:", figma_url)

        file_key, node_id = extract_file_and_node_id(figma_url)
        if not file_key or not node_id:
            continue

        image_url = fetch_figma_image(file_key, node_id)
        if image_url:
            update_notion_page(page_id, image_url)
