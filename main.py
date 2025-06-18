import requests
import os

NOTION_API_URL = "https://api.notion.com/v1"
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")
FIGMA_PROPERTY = os.environ.get("FIGMA_PROPERTY", "Figma Link")
NOTION_VERSION = "2022-06-28"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

def get_database_rows():
    url = f"{NOTION_API_URL}/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    return response.json()["results"]

def embed_figma_link(page_id, figma_url):
    embed_block = {
        "object": "block",
        "type": "embed",
        "embed": {
            "url": f"https://www.figma.com/embed?embed_host=notion&url={figma_url}"
        }
    }
    url = f"{NOTION_API_URL}/blocks/{page_id}/children"
    res = requests.patch(url, headers=headers, json={"children": [embed_block]})
    return res.status_code, res.json()

def main():
    rows = get_database_rows()
    for row in rows:
        props = row["properties"]
        page_id = row["id"]
        figma_prop = props.get(FIGMA_PROPERTY, {})
        if figma_prop.get("url"):
            figma_url = figma_prop["url"]
            status, data = embed_figma_link(page_id, figma_url)
            print(f"Inserted embed to {page_id}: {status}")

if __name__ == "__main__":
    main()
