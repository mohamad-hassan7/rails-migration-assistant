import os
import json
import requests
from bs4 import BeautifulSoup
from time import sleep

BASE_URL = "https://railsdiff.org"

# Version pairs to fetch
VERSION_PAIRS = [
    ("4.2.11", "5.0.0"),
    ("5.0.0", "5.1.7"),
    ("5.1.7", "5.2.0"),
    ("5.2.0", "5.2.6"),
    ("5.2.6", "6.0.0"),
    ("6.0.0", "6.1.0"),
    ("6.1.0", "6.1.7"),
    ("6.1.7", "7.0.8"),
]

SAVE_DIR = os.path.join("data", "raildiff")
os.makedirs(SAVE_DIR, exist_ok=True)

def fetch_and_parse_diff(old_version, new_version):
    """Fetch a RailsDiff page and extract structured changes."""
    url = f"{BASE_URL}/{old_version}/{new_version}"
    print(f"Fetching RailsDiff: {url}")
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"❌ Failed to fetch {url} (status {resp.status_code})")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        diffs = []

        # Each diff section (component/file)
        diff_sections = soup.select(".diff-file-wrapper")
        print(f"Found {len(diff_sections)} diff sections")
        
        for section in diff_sections:
            # Extract file path
            file_header = section.select_one(".diff-file-header")
            file_path = file_header.get_text(strip=True) if file_header else "unknown"

            # Extract code blocks (before/after)
            before_code = []
            after_code = []

            code_lines = section.select(".diff-line")
            for line in code_lines:
                classes = line.get("class", [])
                text = line.get_text().rstrip("\n")

                if "diff-line-added" in classes:
                    after_code.append(text)
                elif "diff-line-removed" in classes:
                    before_code.append(text)

            diffs.append({
                "file_path": file_path,
                "before_code": before_code,
                "after_code": after_code
            })

        print(f"✅ Parsed {len(diffs)} file changes")
        return diffs
        
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def save_diff(old_version, new_version, diffs):
    """Save diffs to JSON."""
    file_name = f"{old_version}_to_{new_version}.json"
    save_path = os.path.join(SAVE_DIR, file_name)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump({
            "old_version": old_version,
            "new_version": new_version,
            "diffs": diffs
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {save_path}")

if __name__ == "__main__":
    for old_ver, new_ver in VERSION_PAIRS:
        changes = fetch_and_parse_diff(old_ver, new_ver)
        if changes:
            save_diff(old_ver, new_ver, changes)
        sleep(2)  # polite delay
