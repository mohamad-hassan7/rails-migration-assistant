# Project Structure Overview

A visual guide to understanding the Rails Upgrade Assistant project organization.

## 📁 Directory Tree

```
rails-upgrade-assistant/
├── 📄 Main Applications
│   ├── rails_upgrade_agent.py           # CLI-based upgrade agent
│   ├── rails_upgrade_gui.py             # GUI application with code review
│   └── rails_upgrade_suggestions.py     # Batch suggestion generator
│
├── 📁 src/ - Core Library
│   ├── analyzer/                        # Code analysis components
│   │   ├── __init__.py
│   │   ├── agent_runner.py              # Main agent orchestration
│   │   └── diff_detector.py             # Change detection logic
│   ├── ingest/                          # Data ingestion pipeline
│   │   ├── __init__.py
│   │   ├── docs_fetcher.py              # Basic documentation fetcher
│   │   ├── smart_docs_fetcher.py        # Intelligent doc fetching
│   │   ├── raildiff_fetcher.py          # RailsDiff web scraping
│   │   └── raildiff_ingest.py           # RailsDiff data processing
│   ├── model/                           # AI/LLM integration
│   │   ├── __init__.py
│   │   ├── gemini_llm.py                # Google Gemini API
│   │   └── local_llm.py                 # Local model support
│   ├── patcher/                         # Suggestion formatting
│   │   ├── __init__.py
│   │   └── suggestion_formatter.py      # Output formatting
│   └── retriever/                       # Search and retrieval
│       ├── __init__.py
│       ├── build_index.py               # FAISS index building
│       ├── chunk_docs.py                # Document chunking
│       └── retriever.py                 # Vector search engine
│
├── 📁 data/ - Knowledge Base
│   ├── chunks_combined.jsonl            # All document chunks
│   ├── faiss_combined.index            # Vector search index
│   ├── meta_combined.jsonl             # Chunk metadata
│   ├── docs/                           # Rails documentation
│   │   ├── v4.2.11/ → v7.0.8/         # Multiple Rails versions
│   │   └── [version]/guides/           # Version-specific guides
│   └── raildiff/                       # Code change data
│       ├── 4.2.11_to_5.0.0.json       # Version transition data
│       ├── 5.2.6_to_6.0.0.json        # Major upgrade diffs
│       └── 6.1.7_to_7.0.8.json        # Latest upgrades
│
├── 📁 demos/ - Interactive Demonstrations
│   ├── demo_search.py                  # Basic search demo
│   ├── rails_upgrade_demo.py           # Original agent demo
│   └── rails_upgrade_enhanced_demo.py  # Advanced dual-mode demo
│
├── 📁 tests/ - Test Suite
│   ├── test_gemini.py                  # AI integration tests
│   ├── test_knowledge.py               # Knowledge base tests
│   ├── test_rails_upgrade_agent.py     # Main agent tests
│   ├── test_retriever.py               # Search functionality tests
│   └── test_upgrade.py                 # Upgrade logic tests
│
├── 📁 tools/ - Utility Scripts
│   ├── analyze_guides.py               # Documentation analysis
│   ├── debug_raildiff.py              # RailsDiff debugging
│   ├── deduplicate_docs.py            # Data optimization
│   └── project_summary.py             # Project statistics
│
├── 📁 docs/ - Documentation
│   ├── GUI_README.md                   # GUI user guide
│   ├── GUI_EXAMPLES.md                 # Usage examples
│   ├── DEDUPLICATION_ANALYSIS.md       # Data optimization report
│   ├── RESULTS.md                      # Project achievements
│   ├── SAFETY_IMPROVEMENTS.md          # Security and safety
│   └── STATUS_REPORT.md                # Development status
│
├── 📁 examples/ - Sample Files
│   ├── example_safe_patch.patch        # Sample patch file
│   └── rails_deduplication_plan.json   # Deduplication config
│
├── 📁 scripts/ - Build Scripts
│   └── inventory_docs.py               # Documentation inventory
│
├── 📁 tmp/ - Temporary Files
│   └── rails_repo/                    # Cloned Rails repository
│
└── 📄 Configuration
    ├── .env                           # Environment variables
    ├── .gitignore                     # Git ignore rules
    ├── README.md                      # Main project documentation
    └── requirements.txt               # Python dependencies
```

## 🎯 Component Relationships

### Data Flow
```
📥 INPUT
├── User Query → GUI/CLI
├── Rails Docs → Smart Fetcher → Chunker → FAISS Index
└── RailsDiff → Web Scraper → Processor → Combined Index

🔄 PROCESSING  
├── Query → Embedder → Vector Search → Document Retrieval
├── Context + Query → Gemini AI → Upgrade Suggestions
└── Suggestions → Formatter → User Interface

📤 OUTPUT
├── GUI → Code Review Interface → Accept/Reject → Report
├── CLI → Formatted Suggestions → JSON/Text Export
└── Demo → Educational Output → Console Display
```

### Module Dependencies
```
Main Applications
├── rails_upgrade_gui.py
│   ├── → src.retriever.retriever (search)
│   ├── → src.model.gemini_llm (AI)
│   └── → tkinter (GUI)
├── rails_upgrade_suggestions.py  
│   ├── → src.retriever.retriever (search)
│   └── → src.model.gemini_llm (AI)
└── rails_upgrade_agent.py
    ├── → src.analyzer.agent_runner
    └── → src.retriever.retriever

Core Libraries
├── src.retriever.retriever
│   ├── → faiss (vector search)
│   ├── → sentence_transformers (embeddings)
│   └── → data/*.index (search indexes)
├── src.model.gemini_llm
│   ├── → google.generativeai (API)
│   └── → os.environ (API keys)
└── src.ingest.*
    ├── → requests + BeautifulSoup (web scraping)
    └── → json + pathlib (data processing)
```

## 🔧 Key Design Principles

### Modularity
- **Separation of Concerns**: Each module has a specific responsibility
- **Loose Coupling**: Components interact through well-defined interfaces
- **Easy Testing**: Each component can be tested independently

### Data Organization
- **Raw Data**: Original Rails docs and RailsDiff JSON
- **Processed Data**: Chunked, embedded, and indexed for search
- **Metadata**: Rich information for result filtering and display

### User Experience
- **Multiple Interfaces**: GUI for interactive use, CLI for automation
- **Progressive Disclosure**: Simple demos → advanced features → full GUI
- **Rich Output**: Formatted, categorized, actionable results

### Extensibility
- **Plugin Architecture**: Easy to add new data sources
- **Model Agnostic**: Support for different AI models (Gemini, local, etc.)
- **Configurable**: Environment variables and config files

## 📊 Size and Complexity

### Lines of Code (Approximate)
```
Main Applications:     ~1,500 lines
Core Library (src/):   ~2,000 lines  
Tests:                 ~800 lines
Tools:                 ~1,200 lines
Documentation:         ~3,000 lines
Total:                 ~8,500 lines
```

### Data Volumes
```
Documentation:         85,126 chunks
Vector Index:          ~400MB
RailsDiff Data:        12 chunks
Total Knowledge:       85,138 searchable items
```

## 🎯 Usage Patterns

### Development Workflow
1. **Data Preparation**: Use `tools/` to analyze and optimize data
2. **Testing**: Run `tests/` to verify functionality  
3. **Development**: Modify `src/` components
4. **Demo Testing**: Use `demos/` to verify changes work
5. **Production**: Run main applications

### User Workflow
1. **Learning**: Start with `demos/` to understand capabilities
2. **Quick Tasks**: Use CLI apps for specific queries
3. **Interactive Work**: Use GUI for comprehensive upgrade projects
4. **Team Collaboration**: Export reports and share findings

### Data Maintenance
1. **Regular Updates**: Fetch new Rails documentation
2. **Index Rebuilding**: Update search indexes when data changes
3. **Quality Assurance**: Run deduplication and analysis tools
4. **Performance Monitoring**: Track search speed and accuracy

---

This structure supports both ease of use and ease of maintenance, with clear separation between user-facing applications and underlying infrastructure.
