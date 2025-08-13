#!/usr/bin/env python3
"""
Simple Rails upgrade knowledge test
Shows what documentation we have and demonstrates basic concept
"""
from pathlib import Path

def test_upgrade_knowledge():
    """Test what Rails upgrade knowledge we have"""
    
    print("Rails Upgrade Agent - Knowledge Test")
    print("=" * 50)
    
    # Load Rails 4.2.11 to 5.0.0 upgrade info
    docs_dir = Path("data/docs")
    
    print("🔍 Checking Rails 4.2.11 upgrade guide...")
    rails_42_guide = docs_dir / "v4.2.11" / "guides" / "source" / "upgrading_ruby_on_rails.md"
    
    if rails_42_guide.exists():
        with open(rails_42_guide, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find Rails 4.2 to 5.0 specific section
        lines = content.split('\n')
        rails5_section = []
        in_rails5_section = False
        
        for line in lines:
            if 'Upgrading from Rails 4.2 to Rails 5.0' in line:
                in_rails5_section = True
            elif 'Upgrading from Rails 4.1 to Rails 4.2' in line or 'Upgrading from Rails 5.0 to Rails 5.1' in line:
                in_rails5_section = False
            
            if in_rails5_section and line.strip():
                rails5_section.append(line)
                
        if rails5_section:
            print("✅ Found Rails 4.2 → 5.0 upgrade section:")
            print("\n".join(rails5_section[:15]))  # First 15 lines
            print("...")
        else:
            # Look for general Rails 5 requirements
            for i, line in enumerate(lines):
                if 'Rails 5' in line and ('require' in line.lower() or 'ruby' in line.lower()):
                    print(f"✅ Found Rails 5 info: {line.strip()}")
                    # Show next few lines for context
                    for j in range(1, 4):
                        if i+j < len(lines) and lines[i+j].strip():
                            print(f"   {lines[i+j].strip()}")
                    break
    
    print("\n" + "-" * 50)
    print("🔍 Checking Rails 5.0.0 changelog...")
    rails5_changelog = docs_dir / "v5.0.0" / "CHANGELOG.md"
    
    if rails5_changelog.exists():
        with open(rails5_changelog, 'r', encoding='utf-8') as f:
            changelog_content = f.read()
            
        # Show first significant changes
        lines = changelog_content.split('\n')
        print("✅ Found Rails 5.0.0 changelog highlights:")
        
        for line in lines[:20]:
            if line.strip() and ('*' in line or '#' in line):
                print(f"   {line.strip()}")
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    
    # Count total documentation files
    total_files = 0
    total_size = 0
    
    for version_dir in docs_dir.iterdir():
        if version_dir.is_dir():
            for file_path in version_dir.rglob('*.md'):
                total_files += 1
                total_size += file_path.stat().st_size
    
    print(f"   📄 {total_files} documentation files")
    print(f"   💾 {total_size / (1024*1024):.1f} MB total documentation")
    print(f"   🎯 Ready for Rails upgrade agent implementation")

if __name__ == "__main__":
    test_upgrade_knowledge()
