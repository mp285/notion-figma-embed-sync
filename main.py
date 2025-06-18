import requests
import os

# ✅ Load from GitHub Action Secrets
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")
FIGMA_PROPERTY = os.environ.get("FIGMA_PROPERTY", "Figma Link")
NOTION_VERSION = "2022-06-28"

# ✅ Headers for all requests
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

def get_database_rows():
    url = f"{NOTION_API_URL}/databases/{DATABASE_ID}/query"
    payload = {"page_size": 10}  # Limit for testing
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    data = response.json()
    print("🔍 Notion response:", data)
    if "results" not in data:
        raise ValueError("❌ No 'results' in response. Check token/DB ID.")
    return data["results"]

def embed_figma_link(page_id, figma_url):
    embed_url = f"https://www.figma.com/embed?embed_host=notion&url={figma_url}"
    embed_block = {
        "object": "block",
        "type": "embed",
        "embed": {
            "url": embed_url
        }
    }
    url = f"{NOTION_API_URL}/blocks/{page_id}/children"
    res = requests.patch(url, headers=headers, json={"children": [embed_block]})
    print(f"📥 Inserted embed: {res.status_code} for page {page_id}")
    return res.status_code, res.json()

  def main():
    rows = get_database_rows()
    print(f"✅ Found {len(rows)} rows in Notion DB.")

    for row in rows:
        page_id = row["id"]
        props = row["properties"]
        title = props.get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled")

        print(f"\n🔍 Checking page: {title} (ID: {page_id})")

        # Get the Figma link from the expected property
        figma_prop = props.get(FIGMA_PROPERTY)
        if not figma_prop:
            print(f"⚠️ Property '{FIGMA_PROPERTY}' not found in row.")
            continue

        figma_url = figma_prop.get("url")
        if not figma_url:
            print(f"⚠️ Row has no URL in '{FIGMA_PROPERTY}' field.")
            continue

        print(f"🔗 Figma URL found: {figma_url}")

        # Try to embed it
        status, res = embed_figma_link(page_id, figma_url)
        if status == 200:
            print(f"✅ Embed inserted into page '{title}'")
        else:
            print(f"❌ Failed to insert embed for '{title}' — status {status} — {res}")
