#!/usr/bin/env python3
"""
src/ingest/docs_fetcher.py

Usage:
  python src/ingest/docs_fetcher.py --tags v4.2.11 v7.0.8
  python src/ingest/docs_fetcher.py --include-intermediates
  python src/ingest/docs_fetcher.py --repo-dir /path/to/local/rails --out-dir data/docs

Notes:
- Requires git on PATH.
- By default clones into ./tmp/rails_repo (within project root).
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_URL = "https://github.com/rails/rails.git"
DEFAULT_REPO_DIR = Path.cwd() / "tmp" / "rails_repo"
DEFAULT_OUT_DIR = Path.cwd() / "data" / "docs"

# Representative intermediate tags (you can adjust)
INTERMEDIATE_TAGS = [
    "v4.2.11",
    "v5.0.0",
    "v5.2.6",
    "v6.0.0",
    "v6.1.7",
    "v7.0.8",
]

# Files/dirs to copy if present in repo root (relative to repo_dir)
COPY_PATHS = [
    "guides",                     # main rails guides
    "CHANGELOG.md",
    "activesupport/CHANGELOG.md",
    "activerecord/CHANGELOG.md",
    "actionpack/CHANGELOG.md",
    "railties/CHANGELOG.md"
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
                # First attempt: full clone
                print(f"Attempt {attempt + 1}/{max_attempts}: Cloning rails repo into {repo_dir}...")
                run(["git", "clone", repo_url, str(repo_dir)])
                return True
            else:
                # Subsequent attempts: shallow clone to reduce network load
                print(f"Attempt {attempt + 1}/{max_attempts}: Trying shallow clone...")
                run(["git", "clone", "--depth", "1", repo_url, str(repo_dir)])
                # Fetch tags after shallow clone
                print("Fetching tags...")
                run(["git", "fetch", "--tags"], cwd=str(repo_dir))
                return True
        except subprocess.CalledProcessError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if repo_dir.exists():
                print(f"Cleaning up partial clone at {repo_dir}")
                shutil.rmtree(repo_dir)
            
            if attempt < max_attempts - 1:
                wait_time = (attempt + 1) * 5  # Progressive backoff: 5s, 10s, 15s
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print("All clone attempts failed. Suggestions:")
                print("1. Check your internet connection")
                print("2. Try running with --no-fetch and manually clone the repo")
                print("3. Use a smaller tag list to reduce download size")
                print(f"   Manual clone command: git clone {repo_url} {repo_dir}")
                return False
    return False


def ensure_repo(repo_dir: Path):
    if repo_dir.exists():
        # update remote tags
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


def copy_paths_for_tag(repo_dir: Path, out_dir: Path, tag: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    # try list of likely paths
    candidates = [
        "guides",
        "rails_guides",  # old variations
        "guides/source",
        "CHANGELOG.md",
        "activesupport/CHANGELOG.md",
        "activerecord/CHANGELOG.md",
        "actionpack/CHANGELOG.md",
        "railties/CHANGELOG.md",
    ]
    for rel in candidates:
        src = repo_dir / rel
        if src.exists():
            dest = out_dir / Path(rel).name
            # Handle existing files/directories properly
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()  # Remove file
                    
            if src.is_dir():
                shutil.copytree(src, dest)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
            copied.append(str(src))
    # Also try to copy docs-style folders near guides
    return copied


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", type=str, default=str(DEFAULT_REPO_DIR), help="Local repo clone path")
    parser.add_argument("--out-dir", type=str, default=str(DEFAULT_OUT_DIR), help="Where to store docs (per-tag)")
    parser.add_argument("--tags", nargs="+", help="List of tags to fetch (overrides include-intermediates)")
    parser.add_argument("--include-intermediates", action="store_true", help="Use recommended intermediate tags")
    parser.add_argument("--no-fetch", action="store_true", help="Do not fetch/clone; use existing repo")
    parser.add_argument("--shallow", action="store_true", help="Force shallow clone (faster but limited history)")
    args = parser.parse_args()

    repo_dir = Path(args.repo_dir)
    out_dir = Path(args.out_dir)

    if not args.no_fetch:
        try:
            ensure_repo(repo_dir)
        except RuntimeError as e:
            print(f"\nFailed to set up repository: {e}")
            print("\nFallback options:")
            print(f"1. Run again with --no-fetch after manually cloning:")
            print(f"   git clone --depth 1 {REPO_URL} {repo_dir}")
            print("2. Try again later with better internet connection")
            print("3. Use a smaller tag subset with --tags v7.0.8")
            sys.exit(1)
    else:
        if not repo_dir.exists():
            raise FileNotFoundError(f"repo-dir {repo_dir} does not exist and --no-fetch was set")

    tags_to_use = []
    if args.tags:
        tags_to_use = args.tags
    elif args.include_intermediates:
        tags_to_use = INTERMEDIATE_TAGS
    else:
        # default minimal demo
        tags_to_use = ["v4.2.11", "v7.0.8"]

    print("Will fetch tags:", tags_to_use)
    original_branch = None
    try:
        # remember current branch/HEAD to restore later
        res = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(repo_dir), check=False)
        original_branch = res.stdout.strip() if res.returncode == 0 else None

        for tag in tags_to_use:
            checkout_tag(repo_dir, tag)
            tag_out = out_dir / tag
            if tag_out.exists():
                print(f"Removing old docs at {tag_out}")
                shutil.rmtree(tag_out)
            copied = copy_paths_for_tag(repo_dir, tag_out, tag)
            if copied:
                print(f"Copied for {tag}:")
                for p in copied:
                    print("  -", p)
            else:
                print(f"No expected docs found for tag {tag} (check if tag exists/has guides).")
    finally:
        # restore original branch if possible
        if original_branch:
            try:
                print(f"Restoring original branch: {original_branch}")
                run(["git", "checkout", original_branch], cwd=str(repo_dir))
            except Exception:
                print("Could not restore original branch; repo in detached state.")

    print("Done. Docs saved under:", out_dir)


if __name__ == "__main__":
    main()
