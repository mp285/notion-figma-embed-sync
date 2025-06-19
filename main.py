import os
import requests

# ✅ WORKING values from manual test
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
FIGMA_PROPERTY = os.getenv("FIGMA_PROPERTY")

# Test file and node confirmed working
FILE_KEY = "PsmOeJT9b1tJbYSPXfyTj2"
NODE_ID = "1%3A68"
PAGE_ID = os.getenv("TEST_PAGE_ID")  # Optional: a Notion page ID to update


def fetch_figma_image(file_key, node_id):
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&format=jpg"
    print(f"📡 Requesting image: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ Figma export failed:", response.text)
        return None
    return response.json().get("images", {}).get(node_id)


def update_notion_thumbnail(page_id, image_url):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "properties": {
            "Thumbnail": {
                "type": "files",
                "files": [
                    {"type": "external", "name": "figma-image.jpg", "external": {"url": image_url}}
                ]
            }
        }
    }
    res = requests.patch(url, headers=headers, json=payload)
    if res.status_code == 200:
        print("✅ Thumbnail added to Notion page")
    else:
        print("❌ Failed to update Notion:", res.text)


if __name__ == "__main__":
    print("🚀 Testing Figma → Notion thumbnail sync")
    image_url = fetch_figma_image(FILE_KEY, NODE_ID)
    if image_url and PAGE_ID:
        update_notion_thumbnail(PAGE_ID, image_url)
    elif not PAGE_ID:
        print("⚠️ Skipping Notion update: TEST_PAGE_ID not set in environment")
