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

 42| def main():
43|     rows = get_database_rows()
44|     print(f"✅ Found {len(rows)} rows in Notion DB.")
45| 
46|     for row in rows:
47|         page_id = row["id"]
48|         props = row["properties"]
49|         title = props.get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled")
50| 
51|         print(f"\n🔍 Checking page: {title} (ID: {page_id})")
52| 
53|         # Get the Figma link from the expected property
54|         figma_prop = props.get(FIGMA_PROPERTY)
55|         if not figma_prop:
56|             print(f"⚠️ Property '{FIGMA_PROPERTY}' not found in row.")
57|             continue
58| 
59|         figma_url = figma_prop.get("url")
60|         if not figma_url:
61|             print(f"⚠️ Row has no URL in '{FIGMA_PROPERTY}' field.")
62|             continue
63| 
64|         print(f"🔗 Figma URL found: {figma_url}")
65| 
66|         # Try to embed it
67|         status, res = embed_figma_link(page_id, figma_url)
68|         if status == 200:
69|             print(f"✅ Embed inserted into page '{title}'")
70|         else:
71|             print(f"❌ Failed to insert embed for '{title}' — status {status} — {res}")
