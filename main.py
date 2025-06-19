import os
import requests

# 🔧 Hardcoded test values
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")
TEST_FILE_KEY = "PsmOeJT9b1tJbYSPXfyTj2"
TEST_NODE_ID = "1%3A68"


def fetch_figma_image(file_key, node_id):
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&format=jpg"
    print(f"🔗 Requesting: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to fetch JPG from Figma API.", response.text)
        return None

    image_url = response.json().get("images", {}).get(node_id)
    print("🖼️ Figma Image URL:", image_url)
    return image_url


if __name__ == "__main__":
    print("🚀 Testing Figma JPG export...")
    fetch_figma_image(TEST_FILE_KEY, TEST_NODE_ID)
