# Rails Upgrade Assistant - Usage Examples

## Example 1: Basic ApplicationRecord Upgrade

**Query**: `ApplicationRecord Rails 5`

**Expected Suggestions**:
- Convert models from `ActiveRecord::Base` to `ApplicationRecord`
- Add `self.abstract_class = true` if missing
- Update generator templates

## Example 2: JavaScript/Turbo Migration

**Query**: `Turbo Rails 7 JavaScript migration`

**Expected Suggestions**:
- Replace Turbolinks with Turbo
- Update stimulus controllers
- Modify import maps configuration

## Example 3: Configuration Updates

**Query**: `load_defaults Rails 6 configuration`

**Expected Suggestions**:
- Add `config.load_defaults` for version
- Update security headers
- Configure new framework defaults

## GUI Workflow

### Step 1: Launch GUI
```bash
.venv\Scripts\Activate.ps1
python rails_upgrade_gui.py
```

### Step 2: Enter Query
- Type your upgrade query in the search box
- Click "🔍 Search & Generate Suggestions"
- Wait for AI to analyze and generate suggestions

### Step 3: Review Suggestions
- Navigate through suggestions with Previous/Next
- Compare old vs new code side-by-side
- Read explanations and confidence levels

### Step 4: Make Decisions
- ✅ **Accept**: Good suggestion, will implement
- ❌ **Reject**: Not applicable or incorrect
- ⏭️ **Skip**: Maybe implement later

### Step 5: Generate Report
- Switch to "📊 Report" tab
- Click "🔄 Refresh Report" to see summary
- Click "💾 Export Report" to save as JSON/text

## Command Line Testing

For quick testing without GUI:

```bash
# Basic usage
python rails_upgrade_suggestions.py "ApplicationRecord Rails 5"

# Save to file
python rails_upgrade_suggestions.py "Turbo Rails 7" --output turbo_suggestions.json

# More context
python rails_upgrade_suggestions.py "ActiveStorage uploads" --max-results 8
```

## Sample Report Output

```
================================================================================
RAILS UPGRADE ASSISTANT REPORT
================================================================================
Generated: 2025-08-13 14:30:45
Total Suggestions: 5

SUMMARY:
  ✅ Accepted: 3
  ❌ Rejected: 1
  ⏭️ Skipped: 1
  ⏳ Pending: 0

DETAILED SUGGESTIONS:
--------------------------------------------------

1. ✅ app/models/application_record.rb
   Status: Accepted
   Confidence: High
   Query: ApplicationRecord Rails 5
   Explanation: Convert from ActiveRecord::Base to ApplicationRecord pattern

2. ❌ config/routes.rb  
   Status: Rejected
   Confidence: Medium
   Query: ApplicationRecord Rails 5
   Explanation: Suggested route changes not applicable to our app
```

## Best Practices

### 1. Use Specific Queries
- ✅ "ApplicationRecord Rails 5.0 upgrade"
- ❌ "Help with Rails"

### 2. Review All Suggestions
- AI suggestions are recommendations, not absolute truth
- Test in development environment first
- Consider your app's specific context

### 3. Iterative Approach
- Start with core framework changes
- Then tackle specific features
- Save reports for tracking progress

### 4. Export and Share
- Export reports as JSON for team review
- Include in upgrade documentation
- Track implementation status over time
