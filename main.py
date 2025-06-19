import os, requests

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")
FIGMA_PROPERTY = os.getenv("FIGMA_PROPERTY")
THUMB_PROP = os.getenv("THUMBNAIL_PROPERTY")

headers_notion = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}
head_figma = {"X-Figma-Token": FIGMA_TOKEN}

def query_db():
    r = requests.post(f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
                      headers=headers_notion)
    r.raise_for_status()
    return r.json()["results"]

def export_figma(file_key, node_id):
    url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&format=jpg"
    r = requests.get(url, headers=head_figma)
    r.raise_for_status()
    return r.json().get("images", {}).get(node_id)

def update_page(page_id, thumb_url):
    data = {
        "page_id": page_id,
        "properties": {
            THUMB_PROP: {"files": [{"name": "Figma export", "external": {"url": thumb_url}}]}
        }
    }
    r = requests.patch("https://api.notion.com/v1/pages/" + page_id,
                       headers=headers_notion, json=data)
    r.raise_for_status()

def main():
    rows = query_db()
    print(f"✅ Found {len(rows)} rows in Notion DB.")
    for row in rows:
        page_id = row["id"]
        props = row["properties"]
        fig_url = props.get(FIGMA_PROPERTY, {}).get("url")
        if not fig_url:
            continue

        file_key = fig_url.split("/file/")[-1].split("/")[0]
        node_id = fig_url.split("node-id=")[-1].split("&")[0]
        img_url = export_figma(file_key, node_id)

        if img_url:
            update_page(page_id, img_url)
            print(f"🖼️ Updated thumbnail on page {page_id}.")
        else:
            print(f"❌ No image from Figma for {page_id}.")

if __name__ == "__main__":
    main()
