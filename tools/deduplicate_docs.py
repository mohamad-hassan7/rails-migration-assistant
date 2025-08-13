#!/usr/bin/env python3
"""
Rails Documentation Deduplication Script
Removes redundant content across Rails versions while preserving critical upgrade information.
"""

import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict
import shutil

class RailsDocDeduplicator:
    def __init__(self, docs_path: Path):
        self.docs_path = Path(docs_path)
        self.versions = []
        self.file_hashes = defaultdict(list)  # filename -> [(version, hash, size)]
        self.dedup_stats = {
            "total_files_scanned": 0,
            "duplicate_files_found": 0,
            "bytes_saved": 0,
            "files_removed": 0
        }
        
    def scan_versions(self):
        """Scan all version directories and catalog files"""
        print("🔍 Scanning Rails documentation versions...")
        
        for version_dir in sorted(self.docs_path.iterdir()):
            if version_dir.is_dir() and version_dir.name.startswith('v'):
                self.versions.append(version_dir.name)
                source_dir = version_dir / "source"
                
                if source_dir.exists():
                    for file_path in source_dir.rglob("*.md"):
                        self._analyze_file(file_path, version_dir.name)
        
        print(f"✅ Scanned {len(self.versions)} versions: {', '.join(self.versions)}")
        print(f"📊 Total files analyzed: {self.dedup_stats['total_files_scanned']}")
    
    def _analyze_file(self, file_path: Path, version: str):
        """Analyze a single file and compute its hash"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            file_size = len(content.encode('utf-8'))
            
            filename = file_path.name
            self.file_hashes[filename].append((version, file_hash, file_size, file_path))
            self.dedup_stats["total_files_scanned"] += 1
            
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    def identify_duplicates(self):
        """Identify files that are identical or nearly identical across versions"""
        print("\n🔍 Identifying duplicate files...")
        
        duplicates = {}
        
        for filename, file_info in self.file_hashes.items():
            if len(file_info) > 1:  # File exists in multiple versions
                # Group by hash to find identical files
                hash_groups = defaultdict(list)
                for version, file_hash, size, path in file_info:
                    hash_groups[file_hash].append((version, size, path))
                
                # Find groups with multiple versions (duplicates)
                for file_hash, versions_info in hash_groups.items():
                    if len(versions_info) > 1:
                        duplicates[filename] = {
                            "hash": file_hash,
                            "versions": versions_info,
                            "duplicate_count": len(versions_info),
                            "size": versions_info[0][1]  # All same size since same hash
                        }
        
        self.duplicates = duplicates
        self.dedup_stats["duplicate_files_found"] = len(duplicates)
        
        print(f"📊 Found {len(duplicates)} files with duplicates across versions")
        return duplicates
    
    def categorize_files(self):
        """Categorize files into different deduplication strategies"""
        print("\n📝 Categorizing files for deduplication strategy...")
        
        categories = {
            "historical_releases": [],      # Old release notes (keep latest only)
            "current_release_notes": [],    # Current version release notes (keep all)
            "upgrade_guides": [],           # Critical for upgrades (keep all)
            "evolving_guides": [],          # Core guides that evolve (keep strategic versions)
            "static_guides": [],            # Rarely changing guides (deduplicate aggressively)
            "feature_guides": []            # New feature guides (version-specific)
        }
        
        for filename, dup_info in self.duplicates.items():
            if "_release_notes.md" in filename:
                # Extract version from filename (e.g., "5_2_release_notes.md" -> "5.2")
                try:
                    version_str = filename.replace("_release_notes.md", "").replace("_", ".")
                    version_num = float(version_str)
                    
                    if version_num < 5.0:  # Historical releases
                        categories["historical_releases"].append((filename, dup_info))
                    else:  # Recent releases
                        categories["current_release_notes"].append((filename, dup_info))
                except:
                    categories["current_release_notes"].append((filename, dup_info))
            
            elif filename == "upgrading_ruby_on_rails.md":
                categories["upgrade_guides"].append((filename, dup_info))
            
            elif any(keyword in filename for keyword in ["active_record", "action_controller", "routing"]):
                categories["evolving_guides"].append((filename, dup_info))
            
            elif any(keyword in filename for keyword in ["action_cable", "active_storage", "action_text", "active_job"]):
                categories["feature_guides"].append((filename, dup_info))
            
            else:
                categories["static_guides"].append((filename, dup_info))
        
        self.categories = categories
        
        # Print categorization summary
        for category, files in categories.items():
            if files:
                print(f"  📂 {category}: {len(files)} files")
        
        return categories
    
    def create_deduplication_plan(self):
        """Create a plan for which files to keep vs remove"""
        print("\n📋 Creating deduplication plan...")
        
        plan = {
            "keep_files": [],
            "remove_files": [],
            "reasoning": {}
        }
        
        # Strategy 1: Historical release notes - keep only the latest version
        for filename, dup_info in self.categories["historical_releases"]:
            versions_info = dup_info["versions"]
            latest_version = max(versions_info, key=lambda x: x[0])  # Sort by version string
            
            for version, size, path in versions_info:
                if version == latest_version[0]:
                    plan["keep_files"].append(str(path))
                else:
                    plan["remove_files"].append(str(path))
            
            plan["reasoning"][filename] = f"Historical release notes - kept {latest_version[0]}, removed {len(versions_info)-1} duplicates"
        
        # Strategy 2: Current release notes and upgrade guides - keep ALL
        for category in ["current_release_notes", "upgrade_guides"]:
            for filename, dup_info in self.categories[category]:
                for version, size, path in dup_info["versions"]:
                    plan["keep_files"].append(str(path))
                plan["reasoning"][filename] = f"Critical for upgrades - kept all {len(dup_info['versions'])} versions"
        
        # Strategy 3: Evolving guides - keep strategic versions (oldest, newest, and middle)
        for filename, dup_info in self.categories["evolving_guides"]:
            versions_info = sorted(dup_info["versions"], key=lambda x: x[0])  # Sort by version
            
            if len(versions_info) <= 3:
                # Keep all if 3 or fewer versions
                for version, size, path in versions_info:
                    plan["keep_files"].append(str(path))
                plan["reasoning"][filename] = f"Evolving guide - kept all {len(versions_info)} versions (≤3)"
            else:
                # Keep first, middle, and last
                keep_indices = [0, len(versions_info)//2, -1]
                for i, (version, size, path) in enumerate(versions_info):
                    if i in keep_indices:
                        plan["keep_files"].append(str(path))
                    else:
                        plan["remove_files"].append(str(path))
                plan["reasoning"][filename] = f"Evolving guide - kept 3 strategic versions, removed {len(versions_info)-3}"
        
        # Strategy 4: Static guides and feature guides - keep only the latest
        for category in ["static_guides", "feature_guides"]:
            for filename, dup_info in self.categories[category]:
                versions_info = sorted(dup_info["versions"], key=lambda x: x[0])
                latest = versions_info[-1]  # Keep the latest version
                
                for version, size, path in versions_info:
                    if version == latest[0]:
                        plan["keep_files"].append(str(path))
                    else:
                        plan["remove_files"].append(str(path))
                
                plan["reasoning"][filename] = f"Static/Feature guide - kept latest ({latest[0]}), removed {len(versions_info)-1}"
        
        self.plan = plan
        
        # Calculate savings
        total_removed = len(plan["remove_files"])
        bytes_saved = sum(dup_info["size"] * (dup_info["duplicate_count"] - 1) 
                         for dup_info in self.duplicates.values())
        
        self.dedup_stats["files_removed"] = total_removed
        self.dedup_stats["bytes_saved"] = bytes_saved
        
        print(f"📊 Deduplication plan created:")
        print(f"  🗂️  Files to keep: {len(plan['keep_files'])}")
        print(f"  🗑️  Files to remove: {total_removed}")
        print(f"  💾 Estimated space saved: {bytes_saved / (1024*1024):.1f} MB")
        
        return plan
    
    def save_plan(self, output_file: Path):
        """Save the deduplication plan to a JSON file"""
        plan_data = {
            "metadata": {
                "versions_analyzed": self.versions,
                "total_files_scanned": self.dedup_stats["total_files_scanned"],
                "duplicate_files_found": self.dedup_stats["duplicate_files_found"],
                "files_to_remove": self.dedup_stats["files_removed"],
                "estimated_bytes_saved": self.dedup_stats["bytes_saved"]
            },
            "plan": self.plan,
            "categories": {k: len(v) for k, v in self.categories.items()}
        }
        
        output_file.write_text(json.dumps(plan_data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"💾 Deduplication plan saved to: {output_file}")
    
    def execute_plan(self, dry_run=True):
        """Execute the deduplication plan (with dry-run option)"""
        if dry_run:
            print("\n🧪 DRY RUN - No files will actually be deleted")
        else:
            print("\n🔥 EXECUTING DEDUPLICATION - Files will be permanently deleted!")
            response = input("Are you sure? Type 'YES' to proceed: ")
            if response != 'YES':
                print("❌ Deduplication cancelled")
                return
        
        removed_count = 0
        for file_path in self.plan["remove_files"]:
            if dry_run:
                print(f"  🗑️  Would remove: {file_path}")
            else:
                try:
                    Path(file_path).unlink()
                    print(f"  ✅ Removed: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ Error removing {file_path}: {e}")
        
        if not dry_run:
            print(f"\n✅ Deduplication complete! Removed {removed_count} files")
        else:
            print(f"\n📋 Dry run complete. Would remove {len(self.plan['remove_files'])} files")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Rails Documentation Deduplication Tool")
    parser.add_argument("--execute", action="store_true", help="Execute deduplication (removes files permanently)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without executing")
    args = parser.parse_args()
    
    docs_path = Path("data/docs")
    
    if not docs_path.exists():
        print("❌ Error: data/docs directory not found")
        return
    
    print("🚀 Rails Documentation Deduplication Tool")
    print("=" * 50)
    
    # Check if we already have a saved plan
    plan_file = Path("rails_deduplication_plan.json")
    if plan_file.exists() and (args.execute or args.dry_run):
        print("📋 Loading existing deduplication plan...")
        plan_data = json.loads(plan_file.read_text(encoding='utf-8'))
        
        # Create a simplified deduplicator just for execution
        class SimpleDedupe:
            def __init__(self, plan):
                self.plan = plan["plan"]
            
            def execute_plan(self, dry_run=True):
                """Execute the deduplication plan (with dry-run option)"""
                if dry_run:
                    print("\n🧪 DRY RUN - No files will actually be deleted")
                else:
                    print("\n🔥 EXECUTING DEDUPLICATION - Files will be permanently deleted!")
                    response = input("Are you sure? Type 'YES' to proceed: ")
                    if response != 'YES':
                        print("❌ Deduplication cancelled")
                        return
                
                removed_count = 0
                for file_path in self.plan["remove_files"]:
                    if dry_run:
                        print(f"  🗑️  Would remove: {file_path}")
                    else:
                        try:
                            Path(file_path).unlink()
                            print(f"  ✅ Removed: {file_path}")
                            removed_count += 1
                        except Exception as e:
                            print(f"  ❌ Error removing {file_path}: {e}")
                
                if not dry_run:
                    print(f"\n✅ Deduplication complete! Removed {removed_count} files")
                else:
                    print(f"\n📋 Dry run complete. Would remove {len(self.plan['remove_files'])} files")
        
        deduplicator = SimpleDedupe(plan_data)
        
        if args.execute:
            deduplicator.execute_plan(dry_run=False)
        else:
            deduplicator.execute_plan(dry_run=True)
        return
    
    deduplicator = RailsDocDeduplicator(docs_path)
    
    # Step 1: Scan all versions
    deduplicator.scan_versions()
    
    # Step 2: Identify duplicates
    duplicates = deduplicator.identify_duplicates()
    
    if not duplicates:
        print("✨ No duplicates found! Your dataset is already optimized.")
        return
    
    # Step 3: Categorize files
    deduplicator.categorize_files()
    
    # Step 4: Create deduplication plan
    deduplicator.create_deduplication_plan()
    
    # Step 5: Save plan
    deduplicator.save_plan(plan_file)
    
    # Step 6: Show plan summary
    print("\n📋 DEDUPLICATION SUMMARY:")
    for filename, reasoning in deduplicator.plan["reasoning"].items():
        print(f"  📄 {filename}: {reasoning}")
    
    # Step 7: Ask user what to do
    print(f"\n🎯 Next steps:")
    print(f"  1. Review the plan in: {plan_file}")
    print(f"  2. Run dry-run: python deduplicate_docs.py --dry-run")
    print(f"  3. Execute: python deduplicate_docs.py --execute")
    
    if args.execute:
        deduplicator.execute_plan(dry_run=False)
    elif args.dry_run:
        deduplicator.execute_plan(dry_run=True)
    else:
        # Execute dry run by default when no specific action requested
        deduplicator.execute_plan(dry_run=True)

if __name__ == "__main__":
    main()
