import requests
import os
import re

# --- 🔐 ENV SETUP ---
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")
FIGMA_PROPERTY = os.environ.get("FIGMA_PROPERTY", "Figma Link")
FIGMA_TOKEN = os.environ.get("FIGMA_TOKEN")
NOTION_VERSION = "2022-06-28"

NOTION_API_URL = "https://api.notion.com/v1"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

# --- 🔍 HELPERS ---

def extract_file_and_node_id(url):
    """
    Extract file_id and node_id from a Figma file URL
    """
    file_match = re.search(r"figma\.com/file/([\w\d]+)", url)
    node_match = re.search(r"node-id=([\w\d%:-]+)", url)

    if not file_match:
        return None, None
    file_id = file_match.group(1)
    node_id = node_match.group(1).replace(":", "%3A") if node_match else "0%3A1"

    return file_id, node_id

def get_figma_image_url(file_id, node_id):
    figma_headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/images/{file_id}?ids={node_id}&format=png"
    response = requests.get(url, headers=figma_headers)
    data = response.json()
    return data.get("images", {}).get(node_id)

def get_database_rows():
    url = f"{NOTION_API_URL}/databases/{DATABASE_ID}/query"
    payload = {"page_size": 10}
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    data = response.json()
    if "results" not in data:
        raise ValueError("❌ No 'results' in Notion response.")
    return data["results"]

def embed_figma_link(page_id, figma_url):
    embed_url = f"https://www.figma.com/embed?embed_host=notion&url={figma_url}"
    embed_block = {
        "object": "block",
        "type": "embed",
        "embed": {"url": embed_url}
    }
    url = f"{NOTION_API_URL}/blocks/{page_id}/children"
    res = requests.patch(url, headers=headers, json={"children": [embed_block]})
    return res.status_code, res.json()

def update_thumbnail(row_id, image_url):
    url = f"{NOTION_API_URL}/pages/{row_id}"
    payload = {
        "properties": {
            "Thumbnail": {"url": image_url}
        }
    }
    res = requests.patch(url, headers=headers, json=payload)
    return res.status_code

# --- 🚀 MAIN ---

def main():
    rows = get_database_rows()
    print(f"✅ Found {len(rows)} rows in Notion DB.")

    for row in rows:
        page_id = row["id"]
        props = row["properties"]
        title = props.get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled")
        print(f"\n🔍 Processing: {title} (Page ID: {page_id})")

        figma_prop = props.get(FIGMA_PROPERTY)
        if not figma_prop or not figma_prop.get("url"):
            print("⚠️ No valid Figma URL found.")
            continue

        figma_url = figma_prop["url"]
        print(f"🔗 Figma URL: {figma_url}")

        # 🧼 Auto-convert /design/ URLs to /file/
        if 'figma.com/design/' in figma_url:
            figma_url = figma_url.replace('/design/', '/file/')
            print(f"🔁 Converted /design/ link to /file/: {figma_url}")

        # 🛑 Skip if thumbnail already exists
        if props.get("Thumbnail", {}).get("url"):
            print("⏩ Skipping — Thumbnail already exists")
            continue

        # ➤ Insert embed
        status, _ = embed_figma_link(page_id, figma_url)
        print(f"📥 Embed insert status: {status}")

        # ➤ Parse file + node ID
        file_id, node_id = extract_file_and_node_id(figma_url)
        if not file_id:
            print("❌ Could not parse file ID from Figma URL.")
            continue

        # ➤ Get image URL
        image_url = get_figma_image_url(file_id, node_id)
        if image_url:
            print(f"🖼 Figma thumbnail: {image_url}")
            update_status = update_thumbnail(page_id, image_url)
            print(f"🔁 Notion update status: {update_status}")
        else:
            print("❌ Failed to fetch Figma thumbnail.")

if __name__ == "__main__":
    main()
