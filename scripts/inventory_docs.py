#!/usr/bin/env python3
"""
Inventory script for Rails documentation
Shows what versions and documentation types we have available
"""
import os
from pathlib import Path

def inventory_docs():
    docs_dir = Path("data/docs")
    if not docs_dir.exists():
        print("No docs directory found!")
        return
    
    versions = sorted([d.name for d in docs_dir.iterdir() if d.is_dir()])
    
    print("Rails Documentation Inventory")
    print("=" * 50)
    print(f"Total versions: {len(versions)}")
    print("\nVersions available:")
    
    for version in versions:
        version_dir = docs_dir / version
        print(f"\n📁 {version}:")
        
        # Check for upgrade guide
        upgrade_guide = version_dir / "guides" / "source" / "upgrading_ruby_on_rails.md"
        if upgrade_guide.exists():
            print("  ✅ Upgrade guide available")
        else:
            print("  ❌ No upgrade guide")
        
        # Check for changelogs
        changelog_files = list(version_dir.glob("**/CHANGELOG.md"))
        print(f"  📄 {len(changelog_files)} changelog files")
        
        # Check guides count
        guides_dir = version_dir / "guides" / "source"
        if guides_dir.exists():
            guide_count = len([f for f in guides_dir.iterdir() if f.suffix == '.md'])
            print(f"  📚 {guide_count} guide files")
            
        # Show size
        total_size = sum(f.stat().st_size for f in version_dir.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        print(f"  💾 {size_mb:.1f} MB")

    print("\n" + "=" * 50)
    print("Upgrade Path Coverage:")
    
    # Show upgrade paths
    major_versions = {
        'v4.2.11': '4.2.x (Legacy)',
        'v5.0.0': '5.0.x (Application Record)',
        'v5.1.7': '5.1.x (Yarn, Webpacker)',
        'v5.2.0': '5.2.x (Active Storage)',
        'v5.2.6': '5.2.x (Stable)',
        'v6.0.0': '6.0.x (Zeitwerk)',
        'v6.1.0': '6.1.x (Horizontal Sharding)',
        'v6.1.7': '6.1.x (Stable)',
        'v7.0.8': '7.0.x (Import maps, Turbo)',
    }
    
    for version in versions:
        description = major_versions.get(version, "Standard version")
        print(f"  {version} → {description}")

if __name__ == "__main__":
    inventory_docs()
