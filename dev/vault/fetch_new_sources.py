import json
import os
import requests
import PyPDF2
import datetime
from pathlib import Path
import io

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "dev" / "source" / "source_registry.json"
VAULT_DIR = REPO_ROOT / "dev" / "vault"

def fetch_and_extract(source_id):
    # 1. Read registry
    registry = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
    sources = registry.get('sources', [])
    
    target = next((s for s in sources if s['source_id'] == source_id), None)
    if not target:
        print(f"Source {source_id} not found in registry.")
        return
        
    url = target.get('url_primary') or target.get('url_landing')
    if not url.endswith('.pdf'):
        print(f"Source {source_id} is not a PDF. URL: {url}")
        return
        
    print(f"Fetching {source_id} from {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch {source_id}. Status: {resp.status_code}")
        return
        
    # 2. Extract PDF text
    pdf_file = io.BytesIO(resp.content)
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(reader.pages)
        print(f"PDF loaded, {num_pages} pages found.")
    except Exception as e:
        print(f"Failed to read PDF {source_id}: {e}")
        return
        
    # extract up to 30 pages to avoid massive files in Phase 3 prototype
    pages_to_extract = min(num_pages, 30)
    extracted_text = []
    
    for i in range(pages_to_extract):
        page = reader.pages[i]
        text = page.extract_text()
        extracted_text.append(f"=== Page {i+1} ===\n{text}")
        
    full_text = "\n\n".join(extracted_text)
    
    # 3. Create vault folder
    target_dir = VAULT_DIR / source_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 4. Write README.md
    readme_content = f"""# vault/{source_id} — {target.get('title')}

**source_id:** `{source_id}`
**URL:** {url}
**提取範圍:** 第1頁至第{pages_to_extract}頁
"""
    (target_dir / "README.md").write_text(readme_content, encoding='utf-8')
    
    # 5. Write extract txt format expected by extract_candidates.py
    today = datetime.datetime.now().strftime('%Y%m%d')
    topic_tags = ",".join(target.get("topic_tags", ["general"]))
    
    extract_header = f"""# source_id: {source_id}
# title: {target.get('title')}
# extracted: {today}
# total_pages: {num_pages}
# extracted_pages: 1-{pages_to_extract}
# url: {url}
# fact_type: policy
# topic_tags: {topic_tags}

"""
    extract_file = target_dir / f"extract_{source_id}_{today}.txt"
    extract_file.write_text(extract_header + full_text, encoding='utf-8')
    
    print(f"Successfully extracted {source_id} to {extract_file.relative_to(REPO_ROOT)}")

if __name__ == "__main__":
    targets = ["g01", "g03", "coa_imc_1_19"]
    for t in targets:
        fetch_and_extract(t)
