#!/usr/bin/env python3
"""
analyze_guides.py

Analyze which guides are truly evolving vs duplicated across Rails versions.
"""
import hashlib
from pathlib import Path
from collections import defaultdict

def get_file_hash(file_path: Path) -> str:
    """Get MD5 hash of file content"""
    if not file_path.exists():
        return "missing"
    try:
        content = file_path.read_text(encoding='utf-8')
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    except:
        try:
            content = file_path.read_text(encoding='latin-1')
            return hashlib.md5(content.encode('utf-8')).hexdigest()
        except:
            return "error"

def analyze_guides():
    docs_dir = Path("data/docs")
    versions = [d.name for d in docs_dir.iterdir() if d.is_dir()]
    versions = sorted(versions)
    
    # Get all unique guide files
    all_guides = set()
    for version in versions:
        guides_dir = docs_dir / version / "guides" / "source"
        if guides_dir.exists():
            for guide in guides_dir.glob("*.md"):
                all_guides.add(guide.name)
    
    print("📊 RAILS GUIDES EVOLUTION ANALYSIS")
    print("=" * 60)
    print(f"Versions analyzed: {', '.join(versions)}")
    print(f"Total unique guide files found: {len(all_guides)}")
    print()
    
    # Analyze each guide
    duplicates = []
    evolving = []
    partial = []
    
    for guide in sorted(all_guides):
        print(f"📖 {guide}")
        print("-" * 40)
        
        # Check presence and hash across versions
        version_data = {}
        for version in versions:
            guide_path = docs_dir / version / "guides" / "source" / guide
            if guide_path.exists():
                file_hash = get_file_hash(guide_path)
                size = guide_path.stat().st_size if guide_path.exists() else 0
                version_data[version] = {'hash': file_hash, 'size': size}
                print(f"  {version}: {size:,} bytes")
            else:
                print(f"  {version}: MISSING")
        
        # Analyze evolution pattern
        existing_versions = [v for v in versions if v in version_data]
        if len(existing_versions) == 0:
            continue
        
        hashes = [version_data[v]['hash'] for v in existing_versions]
        unique_hashes = set(hashes)
        
        if len(unique_hashes) == 1:
            # All versions are identical
            duplicates.append((guide, existing_versions, version_data[existing_versions[0]]['size']))
            print(f"  ❌ DUPLICATE: Same content across all {len(existing_versions)} versions")
        elif len(existing_versions) == len(versions):
            # Present in all versions but different
            evolving.append((guide, existing_versions, [version_data[v]['size'] for v in existing_versions]))
            print(f"  ✅ EVOLVING: Different content across all {len(existing_versions)} versions")
        else:
            # Present in some versions
            partial.append((guide, existing_versions, len(unique_hashes)))
            print(f"  🔄 PARTIAL: Present in {len(existing_versions)}/{len(versions)} versions, {len(unique_hashes)} unique versions")
        
        print()
    
    # Summary
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"✅ EVOLVING guides ({len(evolving)}): Keep all versions")
    for guide, versions, sizes in evolving[:10]:  # Show first 10
        size_range = f"{min(sizes):,}-{max(sizes):,} bytes"
        print(f"   • {guide} ({size_range})")
    if len(evolving) > 10:
        print(f"   ... and {len(evolving) - 10} more")
    
    print(f"\n❌ DUPLICATE guides ({len(duplicates)}): Keep only one version")
    for guide, versions, size in duplicates[:10]:  # Show first 10
        print(f"   • {guide} ({size:,} bytes) - identical across {len(versions)} versions")
    if len(duplicates) > 10:
        print(f"   ... and {len(duplicates) - 10} more")
    
    print(f"\n🔄 PARTIAL guides ({len(partial)}): Review individually")
    for guide, versions, unique_count in partial[:10]:  # Show first 10
        print(f"   • {guide} - in {len(versions)} versions, {unique_count} unique")
    if len(partial) > 10:
        print(f"   ... and {len(partial) - 10} more")
    
    return duplicates, evolving, partial

if __name__ == "__main__":
    duplicates, evolving, partial = analyze_guides()
