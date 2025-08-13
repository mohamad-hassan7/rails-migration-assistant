# Rails Upgrade Assistant GUI

A comprehensive graphical interface for Rails application upgrades that combines documentation search with AI-powered code suggestions.

## Features

### 🔍 **Smart Search & Analysis**
- Searches through Rails documentation and RailsDiff code changes
- Uses Gemini AI to generate contextual upgrade suggestions
- Combines official guides with real code diff examples

### 👀 **Visual Code Review**
- Side-by-side comparison of current vs suggested code
- Syntax highlighting for Ruby/Rails code
- Clear file paths and confidence indicators
- Detailed explanations for each suggestion

### ✅ **Interactive Review Process**
- Accept, reject, or skip individual suggestions
- Navigate through multiple suggestions easily
- Real-time status tracking

### 📊 **Comprehensive Reporting**
- Summary statistics (accepted/rejected/pending)
- Detailed suggestion history
- Export reports as JSON or text files
- Track upgrade progress over time

## Installation

1. Ensure you have the required dependencies:
```bash
# Activate your virtual environment
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install if not already installed
pip install google-generativeai faiss-cpu numpy
```

2. Set up your Gemini API key:
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac  
export GEMINI_API_KEY=your_api_key_here
```

## Usage

### GUI Application
```bash
python rails_upgrade_gui.py
```

### Command Line (for testing)
```bash
# Basic usage
python rails_upgrade_suggestions.py "ApplicationRecord Rails 5"

# Save suggestions to file
python rails_upgrade_suggestions.py "Turbo Rails 7" --output suggestions.json

# Use more search results for context
python rails_upgrade_suggestions.py "ActiveStorage" --max-results 8
```

## How It Works

1. **Search Phase**: Enter a query like "ApplicationRecord Rails 5" or "Turbo JavaScript migration"

2. **AI Analysis**: The system:
   - Searches through Rails documentation and code diffs
   - Feeds relevant context to Gemini AI
   - Generates specific code upgrade suggestions

3. **Review Phase**: For each suggestion you can:
   - See current code vs suggested changes
   - Read detailed explanations
   - Accept, reject, or skip the suggestion

4. **Reporting**: Generate comprehensive reports of all suggestions and their status

## Example Queries

- `"ApplicationRecord Rails 5"` - Get suggestions for Rails 4→5 upgrade
- `"Turbo Rails 7 JavaScript"` - JavaScript migration for Rails 7
- `"ActionCable Rails 6"` - WebSocket upgrades
- `"ActiveStorage file uploads"` - File handling improvements
- `"load_defaults configuration"` - Configuration updates

## GUI Components

### Code Review Tab
- **Navigation**: Previous/Next buttons to browse suggestions
- **Code Comparison**: Side-by-side old vs new code
- **Suggestion Details**: File path, confidence level, explanation
- **Action Buttons**: Accept, Reject, Skip

### Report Tab  
- **Summary Statistics**: Overview of suggestion status
- **Detailed List**: All suggestions with metadata
- **Export Options**: Save as JSON or text file

## File Structure

```
rails_upgrade_gui.py          # Main GUI application
rails_upgrade_suggestions.py  # Command-line version for testing
src/
  retriever/retriever.py      # Search functionality
  model/gemini_llm.py         # AI integration
data/
  chunks_combined.jsonl       # Documentation embeddings
  faiss_combined.index        # Vector search index
  raildiff/                   # Code diff data
```

## Tips for Best Results

1. **Specific Queries**: Use specific Rails features or version numbers
   - Good: "ApplicationRecord Rails 5.0"
   - Less good: "Rails upgrade help"

2. **Review Carefully**: AI suggestions should be reviewed by experienced developers
   - Check compatibility with your Rails version
   - Test suggestions in a development environment first

3. **Iterative Process**: Use multiple queries for different aspects
   - First: "Rails 6 to 7 JavaScript"  
   - Then: "Rails 7 ActionCable"
   - Finally: "Rails 7 configuration"

## Troubleshooting

### Import Errors
If you see import errors, ensure all `__init__.py` files exist:
```bash
# Check if files exist
ls src/*//__init__.py

# Create if missing
touch src/retriever/__init__.py
touch src/model/__init__.py
# etc.
```

### No Suggestions Generated
- Check your Gemini API key is set correctly
- Try more specific queries with Rails version numbers
- Ensure the FAISS index files exist in the `data/` directory

### GUI Not Opening
- Ensure tkinter is available (usually built into Python)
- Try running from command line to see error messages
- Check that virtual environment is activated

## Advanced Usage

### Custom Suggestion Processing
The suggestion format is JSON with these fields:
```json
{
  "file_path": "app/models/application_record.rb",
  "old_code": "Current code here...",
  "new_code": "Updated code here...",
  "explanation": "Why this change is needed...",
  "confidence": "high|medium|low",
  "rails_version": "7.0",
  "status": "pending|accepted|rejected|skipped"
}
```

### Batch Processing
Use the command-line version for processing multiple queries:
```bash
# Process multiple upgrade aspects
python rails_upgrade_suggestions.py "ApplicationRecord" -o app_record.json
python rails_upgrade_suggestions.py "ActionCable" -o cable.json  
python rails_upgrade_suggestions.py "Turbo" -o turbo.json
```

## Contributing

This is a Rails upgrade assistance tool. To improve it:

1. Add more RailsDiff data for additional version pairs
2. Enhance the prompt engineering for better AI suggestions
3. Add more sophisticated code parsing and validation
4. Implement automated testing of suggestions

## License

This tool is designed for Rails application upgrades and uses the Rails documentation and community resources.
