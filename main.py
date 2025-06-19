import os, requests
import re

def parse_figma_url(url):
    match = re.search(r'figma\.com/(?:file|design)/([a-zA-Z0-9]+)', url)
    file_key = match.group(1) if match else None

    node_match = re.search(r'node-id=([^&]+)', url)
    node_id = node_match.group(1) if node_match else None

    return file_key, node_id

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")
FIGMA_PROPERTY = os.getenv("FIGMA_PROPERTY")
THUMB_PROP = os.getenv("THUMBNAIL_PROPERTY")

headers_notion = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
headers_figma = {
    "X-Figma-Token": FIGMA_TOKEN
}

def query_db():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    r = requests.post(url, headers=headers_notion)
    r.raise_for_status()
    return r.json()["results"]

def export_figma(file_key, node_id):
    url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&format=jpg"
    r = requests.get(url, headers=headers_figma)
    r.raise_for_status()
    return r.json().get("images", {}).get(node_id)

def update_page(page_id, thumb_url):
    data = {
        "page_id": page_id,
        "properties": {
            THUMB_PROP: {"files": [{"name": "Figma export", "external": {"url": thumb_url}}]}
        }
    }
    r = requests.patch(f"https://api.notion.com/v1/pages/" + page_id,
                       headers=headers_notion, json=data)
    r.raise_for_status()

def main():
    rows = query_db()
    print(f"🟢 Found {len(rows)} rows in Notion DB.")
    for row in rows:
        page_id = row["id"]
        props = row["properties"]
        fig_url = props.get(FIGMA_PROPERTY, {}).get("url")
        if not fig_url:
            continue

        file_key, node_id = parse_figma_url(fig_url)
        if not file_key or not node_id:
            print(f"⚠️  Skipping: Could not extract file_key or node_id from {fig_url}")
            continue

        img_url = export_figma(file_key, node_id)

        if img_url:
            update_page(page_id, img_url)
            print(f"✅ Updated thumbnail on page {page_id}.")
        else:
            print(f"❌ No image from Figma for {page_id}.")

if __name__ == "__main__":
    main()
