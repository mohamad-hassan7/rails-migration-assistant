# Examples Directory

Sample files, patches, and configuration examples for the Rails Upgrade Assistant.

## 📁 Contents

```
examples/
├── example_safe_patch.patch      # Sample safe patch file
├── rails_deduplication_plan.json # Documentation deduplication strategy
└── README.md                     # This file
```

## 📄 File Descriptions

### `example_safe_patch.patch`
A sample patch file demonstrating safe Rails upgrade patterns:
```bash
# View the patch
cat examples/example_safe_patch.patch

# Apply patch (example only - test first!)
git apply examples/example_safe_patch.patch
```

**Contents:**
- Safe ApplicationRecord migration patterns
- Backward-compatible configuration changes
- Best practices for gradual upgrades

**Use cases:**
- Understanding patch format for Rails upgrades
- Template for creating your own safe patches
- Learning safe upgrade patterns

### `rails_deduplication_plan.json`
Configuration file for documentation deduplication:
```bash
# View deduplication strategy
cat examples/rails_deduplication_plan.json | jq '.'
```

**Contents:**
- File patterns to preserve vs remove
- Version-specific handling rules
- Deduplication algorithm configuration

**Use cases:**
- Understanding how deduplication works
- Customizing deduplication for your needs
- Reference for similar data optimization tasks

## 🎯 Usage Examples

### Understanding Safe Patches
```bash
# Study the patch format
head -20 examples/example_safe_patch.patch

# See what files would be changed
git apply --stat examples/example_safe_patch.patch

# Check for conflicts (don't actually apply)
git apply --check examples/example_safe_patch.patch
```

### Deduplication Configuration
```bash
# Pretty-print the deduplication plan
python -m json.tool examples/rails_deduplication_plan.json

# Use as reference for custom deduplication
cp examples/rails_deduplication_plan.json my_deduplication_plan.json
```

## 📋 Example Categories

### Patch Examples
- **Safe patterns**: Changes that don't break existing functionality
- **Gradual upgrades**: Step-by-step upgrade approaches
- **Rollback strategies**: How to undo changes if needed

### Configuration Examples  
- **Deduplication**: Data optimization strategies
- **Search tuning**: FAISS and embedding configuration
- **AI prompts**: Example prompts for better suggestions

### Code Examples
- **ApplicationRecord migration**: Rails 4→5 base class changes
- **Turbo integration**: Rails 6→7 JavaScript updates
- **Configuration updates**: Rails 6 load_defaults patterns

## 🔧 Creating New Examples

### Patch Files
When creating new patch examples:
```bash
# Generate patch from git changes
git diff > examples/my_upgrade.patch

# Or from specific commits
git format-patch -1 HEAD --stdout > examples/feature_upgrade.patch
```

**Best practices:**
- Include context lines for clarity
- Test patches in clean environment
- Document what the patch accomplishes
- Include rollback instructions

### Configuration Files
When adding configuration examples:
```json
{
  "description": "What this configuration does",
  "use_case": "When to use this configuration",
  "settings": {
    "key": "value"
  },
  "notes": [
    "Important considerations",
    "Potential side effects"
  ]
}
```

### Code Examples
Structure for code examples:
```
examples/
├── rails_5_upgrade/
│   ├── before/          # Code before upgrade
│   │   └── app/models/
│   ├── after/           # Code after upgrade
│   │   └── app/models/
│   └── README.md        # Explanation
```

## 📊 Example Templates

### Rails Version Upgrade Template
```
examples/rails_X_to_Y_upgrade/
├── README.md                    # Upgrade overview
├── before/                      # Pre-upgrade state
│   ├── Gemfile
│   ├── config/application.rb
│   └── app/models/application_record.rb
├── after/                       # Post-upgrade state  
│   ├── Gemfile
│   ├── config/application.rb
│   └── app/models/application_record.rb
├── upgrade.patch               # Automated patch
├── manual_steps.md            # Manual changes needed
└── testing_checklist.md      # What to test
```

### Configuration Template
```json
{
  "name": "Configuration Name",
  "description": "What this configures",
  "rails_versions": ["6.0", "6.1", "7.0"],
  "difficulty": "easy|medium|hard",
  "estimated_time": "30 minutes",
  "prerequisites": [
    "Rails knowledge required",
    "System requirements"
  ],
  "configuration": {
    "setting_1": "value_1",
    "setting_2": "value_2"
  },
  "validation": {
    "how_to_test": "Commands to verify configuration works",
    "expected_output": "What success looks like"
  },
  "troubleshooting": {
    "common_issues": "Typical problems and solutions"
  }
}
```

## 🎯 Contributing Examples

### What Makes Good Examples
1. **Real-world relevance**: Based on actual upgrade scenarios
2. **Clear documentation**: Explain what, why, and how
3. **Tested thoroughly**: Verify examples work as described
4. **Incremental complexity**: Start simple, add complexity gradually
5. **Multiple approaches**: Show different ways to solve problems

### Contribution Process
1. **Identify gap**: What examples are missing?
2. **Create example**: Build working, tested example
3. **Document thoroughly**: README with clear instructions
4. **Test with others**: Have someone else follow your instructions
5. **Submit PR**: Add to examples directory

## 🚨 Important Notes

### Safety Warnings
- **Test first**: Never apply patches directly to production
- **Backup always**: Ensure you can rollback changes
- **Understand impact**: Know what each change does
- **Version compatibility**: Check Rails version requirements

### Example Limitations
- **Sample only**: Examples may not fit your specific application
- **Simplified**: Real applications have more complexity
- **Version specific**: Some examples only work with specific Rails versions
- **Testing required**: Always test in your development environment

## 📚 Additional Resources

### Related Documentation
- **GUI Guide**: `docs/GUI_README.md` - How to use the GUI
- **Safety Guide**: `docs/SAFETY_IMPROVEMENTS.md` - Safe upgrade practices
- **Tools Guide**: `tools/README.md` - Utility scripts for upgrades

### External Resources
- **Rails Upgrade Guide**: Official Rails documentation
- **RailsDiff**: Compare Rails versions online
- **Rails Security**: Security-specific upgrade considerations

---

**Looking for specific examples?** Check the individual files or create an issue requesting examples for your use case.
