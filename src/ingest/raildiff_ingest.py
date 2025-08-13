#!/usr/bin/env python3
"""
src/ingest/raildiff_ingest.py

Processes RailsDiff JSON files and creates semantic text chunks that describe
code changes between Rails versions. These chunks are formatted for embedding
alongside regular Rails documentation.

Usage:
  python src/ingest/raildiff_ingest.py --raildiff-dir data/raildiff --out data/raildiff_chunks.jsonl
"""
import argparse
import json
from pathlib import Path
import re

def clean_code_line(line: str) -> str:
    """Clean a code line by removing common prefixes and extra whitespace."""
    # Remove diff markers like +, -, and leading whitespace
    line = re.sub(r'^[+-]?\s*', '', line)
    return line.strip()

def extract_meaningful_changes(before_code: list, after_code: list) -> list:
    """
    Extract meaningful changes by comparing before/after code.
    Returns a list of change descriptions.
    """
    changes = []
    
    # If only additions (new file or new content)
    if not before_code and after_code:
        # Summarize new content
        significant_lines = [line for line in after_code if line.strip() and not line.strip().startswith('#')]
        if significant_lines:
            if len(significant_lines) <= 3:
                changes.append(f"Added: {' | '.join(significant_lines)}")
            else:
                changes.append(f"Added new content including: {' | '.join(significant_lines[:2])}... ({len(significant_lines)} lines)")
    
    # If only removals (deleted content)
    elif before_code and not after_code:
        significant_lines = [line for line in before_code if line.strip() and not line.strip().startswith('#')]
        if significant_lines:
            if len(significant_lines) <= 3:
                changes.append(f"Removed: {' | '.join(significant_lines)}")
            else:
                changes.append(f"Removed content including: {' | '.join(significant_lines[:2])}... ({len(significant_lines)} lines)")
    
    # If both before and after exist (modifications)
    elif before_code and after_code:
        # Look for specific patterns
        before_str = ' '.join(before_code)
        after_str = ' '.join(after_code)
        
        # Rails version changes
        version_match_before = re.search(r'rails[\'"]?\s*,?\s*[\'"]~?>\s*([\d.]+)', before_str, re.IGNORECASE)
        version_match_after = re.search(r'rails[\'"]?\s*,?\s*[\'"]~?>\s*([\d.]+)', after_str, re.IGNORECASE)
        
        if version_match_before and version_match_after:
            changes.append(f"Rails version changed from {version_match_before.group(1)} to {version_match_after.group(1)}")
        
        # load_defaults changes
        defaults_before = re.search(r'load_defaults\s+([\d.]+)', before_str)
        defaults_after = re.search(r'load_defaults\s+([\d.]+)', after_str)
        
        if defaults_before and defaults_after:
            changes.append(f"Load defaults changed from {defaults_before.group(1)} to {defaults_after.group(1)}")
        
        # Class inheritance changes (ActiveRecord::Base -> ApplicationRecord)
        if 'ActiveRecord::Base' in before_str and 'ApplicationRecord' in after_str:
            changes.append("Model inheritance changed from ActiveRecord::Base to ApplicationRecord")
        
        # JavaScript/Asset changes
        if 'turbolinks' in before_str.lower() and 'turbo-rails' in after_str.lower():
            changes.append("JavaScript: Migrated from Turbolinks to Turbo Rails")
        
        if 'javascript_pack_tag' in before_str and 'javascript_importmap_tags' in after_str:
            changes.append("Asset pipeline: Changed from Webpacker to Import Maps")
        
        # Require changes
        require_before = re.findall(r'require\s+[\'"]([^\'"]+)[\'"]', before_str)
        require_after = re.findall(r'require\s+[\'"]([^\'"]+)[\'"]', after_str)
        
        if require_before != require_after:
            removed_requires = set(require_before) - set(require_after)
            added_requires = set(require_after) - set(require_before)
            
            for req in removed_requires:
                changes.append(f"Removed require: {req}")
            for req in added_requires:
                changes.append(f"Added require: {req}")
        
        # If no specific patterns found, do a general comparison
        if not changes:
            # Look for simple replacements
            if len(before_code) == 1 and len(after_code) == 1:
                changes.append(f"Changed '{clean_code_line(before_code[0])}' to '{clean_code_line(after_code[0])}'")
            elif len(before_code) <= 3 and len(after_code) <= 3:
                before_clean = [clean_code_line(line) for line in before_code if line.strip()]
                after_clean = [clean_code_line(line) for line in after_code if line.strip()]
                if before_clean and after_clean:
                    changes.append(f"Modified from: {' | '.join(before_clean)} → to: {' | '.join(after_clean)}")
    
    return changes

def create_semantic_chunks(raildiff_data: dict) -> list:
    """
    Convert raildiff data into semantic text chunks for embedding.
    """
    old_version = raildiff_data['old_version']
    new_version = raildiff_data['new_version']
    diffs = raildiff_data.get('diffs', [])
    
    chunks = []
    chunk_id = 0
    
    # Create an overview chunk
    file_count = len(diffs)
    files_changed = [diff['file_path'] for diff in diffs[:5]]  # First 5 files
    overview_text = f"Upgrading from Rails {old_version} to {new_version}: {file_count} files changed"
    if files_changed:
        overview_text += f". Key files modified: {', '.join(files_changed)}"
        if file_count > 5:
            overview_text += f" and {file_count - 5} others"
    
    chunks.append({
        "id": chunk_id,
        "text": overview_text,
        "meta": {
            "id": chunk_id,
            "old_version": old_version,
            "new_version": new_version,
            "source_type": "raildiff_overview",
            "source_path": f"raildiff/{old_version}_to_{new_version}",
            "file_path": "overview"
        }
    })
    chunk_id += 1
    
    # Process each file diff
    for diff in diffs:
        file_path = diff['file_path']
        before_code = diff.get('before_code', [])
        after_code = diff.get('after_code', [])
        
        # Extract meaningful changes
        changes = extract_meaningful_changes(before_code, after_code)
        
        if changes:
            # Create a chunk for this file's changes
            change_text = f"In Rails {old_version} to {new_version} upgrade, {file_path} changes: {'; '.join(changes)}"
            
            chunks.append({
                "id": chunk_id,
                "text": change_text,
                "meta": {
                    "id": chunk_id,
                    "old_version": old_version,
                    "new_version": new_version,
                    "source_type": "raildiff_file",
                    "source_path": f"raildiff/{old_version}_to_{new_version}",
                    "file_path": file_path,
                    "changes_count": len(changes)
                }
            })
            chunk_id += 1
            
            # If there are many changes, create separate chunks for detailed changes
            if len(changes) > 3:
                for i, change in enumerate(changes):
                    detail_text = f"Rails {old_version} to {new_version}: {file_path} - {change}"
                    chunks.append({
                        "id": chunk_id,
                        "text": detail_text,
                        "meta": {
                            "id": chunk_id,
                            "old_version": old_version,
                            "new_version": new_version,
                            "source_type": "raildiff_detail",
                            "source_path": f"raildiff/{old_version}_to_{new_version}",
                            "file_path": file_path,
                            "change_index": i
                        }
                    })
                    chunk_id += 1
    
    return chunks

def process_raildiff_files(raildiff_dir: Path, output_path: Path, start_id: int = 0):
    """
    Process all RailsDiff JSON files and create semantic chunks.
    """
    all_chunks = []
    chunk_id = start_id
    
    json_files = list(raildiff_dir.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in {raildiff_dir}")
        return
    
    print(f"Processing {len(json_files)} RailsDiff files...")
    
    for json_file in sorted(json_files):
        print(f"Processing: {json_file.name}")
        
        try:
            with json_file.open('r', encoding='utf-8') as f:
                raildiff_data = json.load(f)
            
            chunks = create_semantic_chunks(raildiff_data)
            
            # Update chunk IDs to be unique
            for chunk in chunks:
                chunk['id'] = chunk_id
                chunk['meta']['id'] = chunk_id
                chunk_id += 1
            
            all_chunks.extend(chunks)
            print(f"  Created {len(chunks)} chunks (IDs {chunk_id - len(chunks)} to {chunk_id - 1})")
            
        except Exception as e:
            print(f"  Error processing {json_file}: {e}")
    
    # Write all chunks to output file
    with output_path.open('w', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Created {len(all_chunks)} semantic chunks")
    print(f"📁 Saved to: {output_path}")
    
    # Show sample chunks
    print("\n📋 Sample chunks:")
    for i, chunk in enumerate(all_chunks[:3]):
        print(f"{i+1}. [{chunk['id']}] {chunk['text']}")
    
    return len(all_chunks)

def main():
    parser = argparse.ArgumentParser(description="Process RailsDiff data into semantic chunks")
    parser.add_argument("--raildiff-dir", type=str, default="data/raildiff",
                       help="Directory containing RailsDiff JSON files")
    parser.add_argument("--out", type=str, default="data/raildiff_chunks.jsonl",
                       help="Output file for semantic chunks")
    parser.add_argument("--start-id", type=int, default=0,
                       help="Starting ID for chunks (use this to avoid conflicts with existing chunks)")
    
    args = parser.parse_args()
    
    raildiff_dir = Path(args.raildiff_dir)
    output_path = Path(args.out)
    
    if not raildiff_dir.exists():
        print(f"❌ RailsDiff directory not found: {raildiff_dir}")
        return
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    process_raildiff_files(raildiff_dir, output_path, args.start_id)

if __name__ == "__main__":
    main()
