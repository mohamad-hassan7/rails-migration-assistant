#!/usr/bin/env python3
"""
src/ingest/smart_docs_fetcher.py

Smart Rails documentation fetcher that avoids duplicates by strategically
selecting relevant content for each version.

Usage:
  python src/ingest/smart_docs_fetcher.py --tags v4.2.11 v7.0.8
  python src/ingest/smart_docs_fetcher.py --include-intermediates
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import re

REPO_URL = "https://github.com/rails/rails.git"
DEFAULT_REPO_DIR = Path.cwd() / "tmp" / "rails_repo"
DEFAULT_OUT_DIR = Path.cwd() / "data" / "docs"

# Representative intermediate tags
INTERMEDIATE_TAGS = [
    "v4.2.11",
    "v5.0.0", 
    "v5.2.6",
    "v6.0.0",
    "v6.1.7",
    "v7.0.8",
]

def run(cmd, cwd=None, check=True):
    print("> " + " ".join(cmd))
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and res.returncode != 0:
        print("ERROR:", res.stderr or res.stdout, file=sys.stderr)
        raise subprocess.CalledProcessError(res.returncode, cmd)
    return res

def clone_with_retry(repo_url: str, repo_dir: Path, max_attempts: int = 3):
    """Clone repository with retry logic and shallow clone option"""
    for attempt in range(max_attempts):
        try:
            if attempt == 0:
                print(f"Attempt {attempt + 1}/{max_attempts}: Cloning rails repo into {repo_dir}...")
                run(["git", "clone", repo_url, str(repo_dir)])
                return True
            else:
                print(f"Attempt {attempt + 1}/{max_attempts}: Trying shallow clone...")
                run(["git", "clone", "--depth", "1", repo_url, str(repo_dir)])
                print("Fetching tags...")
                run(["git", "fetch", "--tags"], cwd=str(repo_dir))
                return True
        except subprocess.CalledProcessError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if repo_dir.exists():
                print(f"Cleaning up partial clone at {repo_dir}")
                shutil.rmtree(repo_dir)
            
            if attempt < max_attempts - 1:
                wait_time = (attempt + 1) * 5
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print("All clone attempts failed.")
                return False
    return False

def ensure_repo(repo_dir: Path):
    if repo_dir.exists():
        print(f"Updating existing repo at {repo_dir}...")
        try:
            run(["git", "fetch", "--all", "--tags"], cwd=str(repo_dir))
        except subprocess.CalledProcessError:
            print("Warning: Failed to fetch updates. Proceeding with existing repo.")
    else:
        print(f"Cloning rails repo into {repo_dir} (this may take a while)...")
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        success = clone_with_retry(REPO_URL, repo_dir)
        if not success:
            raise RuntimeError("Failed to clone repository after multiple attempts")

def checkout_tag(repo_dir: Path, tag: str):
    print(f"Checking out tag {tag}...")
    run(["git", "checkout", "--detach", tag], cwd=str(repo_dir))

def get_version_from_tag(tag: str) -> tuple:
    """Extract major.minor version from tag (e.g., v6.1.7 -> (6, 1))"""
    match = re.match(r'v(\d+)\.(\d+)', tag)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (0, 0)

def should_include_release_note(file_path: Path, current_tag: str) -> bool:
    """
    Determine if a release note should be included for the current tag.
    Strategy: Only include release notes for CURRENT VERSION to avoid duplicates.
    """
    current_major, current_minor = get_version_from_tag(current_tag)
    
    # Extract version from filename (e.g., 5_2_release_notes.md -> (5, 2))
    match = re.match(r'(\d+)_(\d+)_release_notes\.md', file_path.name)
    if match:
        note_major, note_minor = int(match.group(1)), int(match.group(2))
        # Only include release notes for EXACTLY the current version to avoid duplicates
        return (note_major, note_minor) == (current_major, current_minor)
    
    # Include edge guides, upgrade guides, etc. (these are not version-specific)
    special_notes = [
        'edge_badge.png',
        'upgrading_ruby_on_rails.md', 
        'maintenance_policy.md',
        'development_dependencies_install.md'
    ]
    return file_path.name in special_notes or 'upgrade' in file_path.name.lower()

def should_include_guide(file_path: Path, current_tag: str) -> bool:
    """
    Determine if a guide should be included.
    Strategy: Include all guides except version-specific release notes.
    
    Based on analysis, most guides evolve meaningfully between versions,
    so we keep them all except for the obvious duplicates (release notes).
    """
    
    # For release notes, use strict version-specific filtering
    if 'release_notes' in file_path.name:
        return should_include_release_note(file_path, current_tag)
    
    # For all other guides, include them - they're either evolving 
    # or appear in specific versions for good reasons
    # (like action_cable_overview.md, action_text_overview.md, etc.)
    return True

def copy_smart_content(repo_dir: Path, out_dir: Path, tag: str):
    """
    Smart content copying that avoids duplicates by selecting relevant
    content for each version.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    copied_files = []
    
    # Copy CHANGELOG.md files (these are always version-specific)
    changelog_paths = [
        "CHANGELOG.md",
        "activesupport/CHANGELOG.md",
        "activerecord/CHANGELOG.md", 
        "actionpack/CHANGELOG.md",
        "railties/CHANGELOG.md",
        "actionview/CHANGELOG.md",
        "actionmailer/CHANGELOG.md",
        "activejob/CHANGELOG.md"
    ]
    
    for changelog_path in changelog_paths:
        src = repo_dir / changelog_path
        if src.exists():
            # Create nested structure for component changelogs
            if '/' in changelog_path:
                dest = out_dir / f"{changelog_path.replace('/', '_')}"
            else:
                dest = out_dir / changelog_path
            
            if dest.exists():
                dest.unlink()
            shutil.copy2(src, dest)
            copied_files.append(str(src))
    
    # Smart guides copying
    guides_src = repo_dir / "guides"
    if guides_src.exists():
        guides_dest = out_dir / "guides"
        guides_dest.mkdir(exist_ok=True)
        
        # Copy guides/source with filtering
        source_src = guides_src / "source"
        if source_src.exists():
            source_dest = guides_dest / "source"
            source_dest.mkdir(exist_ok=True)
            
            for item in source_src.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(source_src)
                    
                    # Apply smart filtering
                    if should_include_guide(item, tag):
                        dest_path = source_dest / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        if dest_path.exists():
                            dest_path.unlink()
                        shutil.copy2(item, dest_path)
                        copied_files.append(str(item))
    
    return copied_files

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", type=str, default=str(DEFAULT_REPO_DIR), help="Local repo clone path")
    parser.add_argument("--out-dir", type=str, default=str(DEFAULT_OUT_DIR), help="Where to store docs (per-tag)")
    parser.add_argument("--tags", nargs="+", help="List of tags to fetch")
    parser.add_argument("--include-intermediates", action="store_true", help="Use recommended intermediate tags")
    parser.add_argument("--no-fetch", action="store_true", help="Do not fetch/clone; use existing repo")
    args = parser.parse_args()

    repo_dir = Path(args.repo_dir)
    out_dir = Path(args.out_dir)

    if not args.no_fetch:
        try:
            ensure_repo(repo_dir)
        except RuntimeError as e:
            print(f"\nFailed to set up repository: {e}")
            sys.exit(1)
    else:
        if not repo_dir.exists():
            raise FileNotFoundError(f"repo-dir {repo_dir} does not exist and --no-fetch was set")

    # Determine tags to use
    if args.tags:
        tags_to_use = args.tags
    elif args.include_intermediates:
        tags_to_use = INTERMEDIATE_TAGS
    else:
        tags_to_use = ["v4.2.11", "v7.0.8"]

    print("Smart fetching for tags:", tags_to_use)
    print("Strategy: Version-appropriate release notes + evolving guides + version-specific changelogs")
    
    original_branch = None
    try:
        # Remember current branch/HEAD
        res = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(repo_dir), check=False)
        original_branch = res.stdout.strip() if res.returncode == 0 else None

        for tag in tags_to_use:
            print(f"\n=== Processing {tag} ===")
            checkout_tag(repo_dir, tag)
            tag_out = out_dir / tag
            
            if tag_out.exists():
                print(f"Removing old docs at {tag_out}")
                shutil.rmtree(tag_out)
            
            copied = copy_smart_content(repo_dir, tag_out, tag)
            
            print(f"Copied {len(copied)} files for {tag}")
            if copied:
                print("Sample files:")
                for p in copied[:5]:  # Show first 5 files
                    print(f"  - {p}")
                if len(copied) > 5:
                    print(f"  ... and {len(copied) - 5} more")
                    
    finally:
        # Restore original branch
        if original_branch:
            try:
                print(f"\nRestoring original branch: {original_branch}")
                run(["git", "checkout", original_branch], cwd=str(repo_dir))
            except Exception:
                print("Could not restore original branch; repo in detached state.")

    print(f"\n✅ Smart docs fetching complete! Docs saved under: {out_dir}")
    print("\nNext steps:")
    print("1. Run chunking: python -m src.retriever.chunk_docs --docs-dir data/docs --out data/chunks.jsonl")
    print("2. Build index: python -m src.retriever.build_index")

if __name__ == "__main__":
    main()
