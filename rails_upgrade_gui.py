#!/usr/bin/env python3
"""
Rails Upgrade GUI Agent

A graphical interface for the Rails upgrade assistant that:
1. Shows old vs new code suggestions
2. Allows user review and acceptance
3. Generates reports of all suggestions and their status
4. Provides a better user experience than CLI

Usage:
  python rails_upgrade_gui.py
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.retriever.retriever import Retriever
    from src.model.local_llm import LocalLLM
    from src.analyzer.project_scanner import RailsProjectScanner
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are available")
    sys.exit(1)

class RailsUpgradeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rails Upgrade Assistant")
        self.root.geometry("1400x900")
        
        # Initialize components
        index_path = "data/faiss_combined.index"
        meta_path = "data/meta_combined.jsonl"
        self.retriever = Retriever(index_path, meta_path)
        self.scanner = RailsProjectScanner()
        
        # LLM selection (local LLM only)
        self.use_local_llm = True
        self.llm = None
        self.local_llm = None
        self._initialize_llm()
        
        # Track suggestions and their status
        self.suggestions = []
        self.current_suggestion_index = 0
        self.project_analysis = None
        
        # Mode selection
        self.current_mode = "query"  # "query" or "project"
        
        self.create_widgets()
    
    def _initialize_llm(self):
        """Initialize the Local LLM."""
        try:
            if self.local_llm is None:
                self.local_llm = LocalLLM(use_4bit=True)
            self.llm = self.local_llm
        except Exception as e:
            messagebox.showerror("LLM Error", f"Failed to initialize Local LLM: {str(e)}")
            self.llm = None
        
    def create_widgets(self):
        """Create the GUI layout."""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title and LLM selection
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="🚀 Rails Upgrade Assistant", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # LLM selection frame - Local LLM only
        llm_frame = ttk.Frame(header_frame)
        llm_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Label(llm_frame, text="AI Model:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.llm_var = tk.StringVar(value="Local LLM")
        llm_label = ttk.Label(llm_frame, textvariable=self.llm_var, font=("Arial", 10, "bold"))
        llm_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # LLM status indicator
        self.llm_status_var = tk.StringVar(value="🟢 Ready" if self.llm else "🔴 Error")
        ttk.Label(llm_frame, textvariable=self.llm_status_var, font=("Arial", 9)).pack(side=tk.LEFT)
        
        # Mode selection section - Make this the main choice
        self.create_mode_selection(main_frame)
        
        # Content area (will be populated based on mode selection)
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Choose a mode above to get started")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Initially show mode selection
        self.show_mode_selection()
        
    def create_mode_selection(self, parent):
        """Create the mode selection interface."""
        # Mode selection section
        mode_frame = ttk.LabelFrame(parent, text="Choose Your Mode", padding="20")
        mode_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        mode_frame.columnconfigure(0, weight=1)
        mode_frame.columnconfigure(1, weight=1)
        
        # Mode selection variable
        self.mode_var = tk.StringVar(value="")
        
        # Query Mode Card
        query_card = ttk.Frame(mode_frame, relief="raised", borderwidth=2, padding="15")
        query_card.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        query_title = ttk.Label(query_card, text="💬 Query Mode", font=("Arial", 14, "bold"))
        query_title.pack(anchor=tk.W)
        
        query_desc = ttk.Label(query_card, text=
                              "• Ask questions like 'Rails 7 upgrade deprecations'\n"
                              "• Get instant AI answers with documentation references\n"
                              "• Perfect for quick Rails upgrade guidance\n"
                              "• Example queries provided for common scenarios",
                              font=("Arial", 10), foreground="gray", justify=tk.LEFT)
        query_desc.pack(anchor=tk.W, pady=(10, 15))
        
        query_btn = ttk.Button(query_card, text="Start Query Mode", 
                              command=lambda: self.select_mode("query"),
                              style="Accent.TButton")
        query_btn.pack(anchor=tk.W)
        
        # Project Mode Card  
        project_card = ttk.Frame(mode_frame, relief="raised", borderwidth=2, padding="15")
        project_card.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        project_title = ttk.Label(project_card, text="📁 Project Mode", font=("Arial", 14, "bold"))
        project_title.pack(anchor=tk.W)
        
        project_desc = ttk.Label(project_card, text=
                                "• Browse and select your Rails project directory\n"
                                "• Get comprehensive upgrade suggestions\n"
                                "• Review code changes side-by-side\n"
                                "• Apply changes with automatic backups\n"
                                "• Track all modifications and generate reports",
                                font=("Arial", 10), foreground="gray", justify=tk.LEFT)
        project_desc.pack(anchor=tk.W, pady=(10, 15))
        
        project_btn = ttk.Button(project_card, text="Start Project Mode", 
                                command=lambda: self.select_mode("project"),
                                style="Accent.TButton")
        project_btn.pack(anchor=tk.W)
        
    def create_review_tab(self):
        """Create the code review tab."""
        review_frame = ttk.Frame(self.notebook)
        self.notebook.add(review_frame, text="Code Review")
        
        # Configure grid weights
        review_frame.columnconfigure(0, weight=1)
        review_frame.columnconfigure(1, weight=1)
        review_frame.rowconfigure(1, weight=1)
        
        # Suggestion navigation
        nav_frame = ttk.Frame(review_frame)
        nav_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        nav_frame.columnconfigure(1, weight=1)
        
        ttk.Button(nav_frame, text="◀ Previous", command=self.previous_suggestion).grid(row=0, column=0)
        
        self.suggestion_label = ttk.Label(nav_frame, text="No suggestions loaded", 
                                         font=("Arial", 11, "bold"))
        self.suggestion_label.grid(row=0, column=1, padx=(10, 10))
        
        ttk.Button(nav_frame, text="Next ▶", command=self.next_suggestion).grid(row=0, column=2)
        
        # Old vs New code comparison
        # Old code section
        old_frame = ttk.LabelFrame(review_frame, text="📜 Current Code", padding="5")
        old_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        old_frame.columnconfigure(0, weight=1)
        old_frame.rowconfigure(0, weight=1)
        
        self.old_code_text = scrolledtext.ScrolledText(old_frame, wrap=tk.WORD, 
                                                      font=("Consolas", 10),
                                                      background="#fff8dc")
        self.old_code_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # New code section
        new_frame = ttk.LabelFrame(review_frame, text="✨ Suggested Code", padding="5")
        new_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        new_frame.columnconfigure(0, weight=1)
        new_frame.rowconfigure(0, weight=1)
        
        self.new_code_text = scrolledtext.ScrolledText(new_frame, wrap=tk.WORD, 
                                                      font=("Consolas", 10),
                                                      background="#f0fff0")
        self.new_code_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Suggestion details and actions
        details_frame = ttk.LabelFrame(review_frame, text="Suggestion Details", padding="5")
        details_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        details_frame.columnconfigure(0, weight=1)
        
        # File path and confidence
        self.file_path_var = tk.StringVar()
        ttk.Label(details_frame, text="File:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(details_frame, textvariable=self.file_path_var).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        self.confidence_var = tk.StringVar()
        ttk.Label(details_frame, text="Confidence:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(details_frame, textvariable=self.confidence_var).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # Explanation
        ttk.Label(details_frame, text="Explanation:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(5, 0))
        self.explanation_text = tk.Text(details_frame, height=3, wrap=tk.WORD, font=("Arial", 9))
        self.explanation_text.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        
        # Action buttons
        action_frame = ttk.Frame(details_frame)
        action_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(action_frame, text="✅ Accept", command=self.accept_suggestion,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="❌ Reject", command=self.reject_suggestion).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="⏭️ Skip", command=self.skip_suggestion).pack(side=tk.LEFT)
        
    def create_analysis_tab(self):
        """Create the project analysis tab."""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="📊 Project Analysis")
        
        # Configure grid
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(1, weight=1)
        
        # Analysis summary
        summary_frame = ttk.LabelFrame(analysis_frame, text="Project Summary", padding="5")
        summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        summary_frame.columnconfigure(1, weight=1)
        
        # Project info labels
        ttk.Label(summary_frame, text="Project Path:").grid(row=0, column=0, sticky=tk.W)
        self.project_path_label = ttk.Label(summary_frame, text="No project scanned", foreground="gray")
        self.project_path_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(summary_frame, text="Rails Version:").grid(row=1, column=0, sticky=tk.W)
        self.rails_version_label = ttk.Label(summary_frame, text="Unknown", foreground="gray")
        self.rails_version_label.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(summary_frame, text="Issues Found:").grid(row=2, column=0, sticky=tk.W)
        self.issues_count_label = ttk.Label(summary_frame, text="0", foreground="gray")
        self.issues_count_label.grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        # Upgrade priorities
        priorities_frame = ttk.LabelFrame(analysis_frame, text="Upgrade Priorities", padding="5")
        priorities_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        priorities_frame.columnconfigure(0, weight=1)
        priorities_frame.rowconfigure(0, weight=1)
        
        self.priorities_text = scrolledtext.ScrolledText(priorities_frame, wrap=tk.WORD, 
                                                        font=("Arial", 10), height=15)
        self.priorities_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
    def show_mode_selection(self):
        """Show the initial mode selection screen."""
        self.current_mode = None
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Show welcome message
        welcome_frame = ttk.Frame(self.content_frame)
        welcome_frame.pack(expand=True, fill=tk.BOTH)
        
        welcome_label = ttk.Label(welcome_frame, 
                                 text="Welcome! Please choose a mode above to get started.",
                                 font=("Arial", 12), foreground="gray")
        welcome_label.pack(expand=True)
        
        self.status_var.set("Choose a mode above to get started")
        
    def select_mode(self, mode):
        """Handle mode selection and switch to the appropriate interface."""
        self.current_mode = mode
        
        if mode == "query":
            self.create_query_interface()
        elif mode == "project":
            self.create_project_interface()
            
    def create_query_interface(self):
        """Create the query mode interface."""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Query input section
        input_frame = ttk.LabelFrame(self.content_frame, text="💬 Query Mode - Ask Your Rails Question", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Query input
        ttk.Label(input_frame, text="Ask your Rails question:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.query_var = tk.StringVar()
        query_entry = ttk.Entry(input_frame, textvariable=self.query_var, font=("Arial", 11))
        query_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ask_btn = ttk.Button(input_frame, text="💬 Ask AI", command=self.ask_query,
                            style="Accent.TButton")
        ask_btn.grid(row=0, column=2)
        
        # Example queries
        examples_frame = ttk.Frame(input_frame)
        examples_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(examples_frame, text="💡 Example questions:", font=("Arial", 9)).pack(anchor=tk.W)
        
        examples = [
            "Rails 7 upgrade deprecations",
            "ActionCable WebSocket Rails 6 to 7", 
            "Strong parameters best practices",
            "Rails security vulnerabilities",
            "Performance improvements Rails 6"
        ]
        
        examples_container = ttk.Frame(examples_frame)
        examples_container.pack(fill=tk.X, padx=(10, 0))
        
        for i, example in enumerate(examples):
            example_btn = ttk.Button(examples_container, text=f"• {example}", 
                                   command=lambda e=example: self.set_example_query(e))
            example_btn.grid(row=i//2, column=i%2, sticky=tk.W, padx=(0, 20), pady=2)
            
        # Response area
        response_frame = ttk.LabelFrame(self.content_frame, text="💬 AI Response", padding="10")
        response_frame.pack(fill=tk.BOTH, expand=True)
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(1, weight=1)
        
        # Response header
        header_frame = ttk.Frame(response_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.response_title = ttk.Label(header_frame, text="Ask a question to get AI guidance", 
                                       font=("Arial", 12, "bold"))
        self.response_title.pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="🔄 Clear", command=self.clear_response).pack(side=tk.RIGHT)
        
        # Response display
        self.response_text = scrolledtext.ScrolledText(response_frame, wrap=tk.WORD, font=("Arial", 10))
        self.response_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Insert welcome message
        welcome_msg = """🚀 Welcome to Query Mode!

Ask any Rails upgrade question and get instant AI-powered answers with documentation references.

💡 Try asking about:
• Specific Rails version upgrades
• Deprecated methods and their replacements  
• Security best practices
• Performance optimization tips
• Migration strategies

Example: "How do I upgrade from Rails 6 to Rails 7?"
"""
        self.response_text.insert(1.0, welcome_msg)
        
        # Back button
        back_btn = ttk.Button(response_frame, text="⬅️ Back to Mode Selection", 
                             command=self.show_mode_selection)
        back_btn.grid(row=2, column=0, pady=(10, 0), sticky=tk.W)
        
        self.status_var.set("💬 Query Mode - Ask any Rails upgrade question")
        
    def create_project_interface(self):
        """Create the project mode interface."""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Project input section
        input_frame = ttk.LabelFrame(self.content_frame, text="📁 Project Mode - Scan Your Rails Project", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Project selection
        ttk.Label(input_frame, text="Rails Project:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.project_path_var = tk.StringVar()
        project_entry = ttk.Entry(input_frame, textvariable=self.project_path_var, font=("Arial", 11))
        project_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(input_frame, text="📁 Browse", command=self.browse_project).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(input_frame, text="🔍 Scan Project", command=self.scan_project, 
                  style="Accent.TButton").grid(row=0, column=3)
        
        # Quick actions
        actions_frame = ttk.Frame(input_frame)
        actions_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(actions_frame, text="🚀 Quick actions:", font=("Arial", 9)).pack(anchor=tk.W)
        
        actions_container = ttk.Frame(actions_frame)
        actions_container.pack(fill=tk.X, padx=(10, 0))
        
        ttk.Button(actions_container, text="📋 Use Sample Project", 
                  command=self.use_sample_project).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_container, text="📄 View Last Report", 
                  command=self.view_last_report).pack(side=tk.LEFT)
        
        # Tabbed content area
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create project mode tabs
        self.create_review_tab()
        self.create_analysis_tab() 
        self.create_report_tab()
        
        # Back button
        back_btn = ttk.Button(self.content_frame, text="⬅️ Back to Mode Selection", 
                             command=self.show_mode_selection)
        back_btn.pack(pady=(10, 0), anchor=tk.W)
        
        self.status_var.set("📁 Project Mode - Browse and select your Rails project to scan")
        
    def set_example_query(self, query):
        """Set an example query in the input field."""
        self.query_var.set(query)
        
    def ask_query(self):
        """Handle query mode AI requests."""
        query = self.query_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a question")
            return
            
        self.status_var.set("🤖 Getting AI response...")
        self.root.update()
        
        try:
            # Search for relevant content
            results = self.retriever.search(query, top_k=5)
            
            # Debug: Check if we're getting good results
            print(f"🔍 Search results for '{query}':")
            print(f"   Found {len(results)} results")
            for i, result in enumerate(results[:2]):
                text = result.get('text', '')
                meta = result.get('meta', {})
                source = meta.get('source', 'Unknown')
                print(f"   {i+1}. Source: {source}")
                print(f"      Text preview: {text[:100]}...")
            
            # Generate AI response
            context_parts = []
            for result in results:
                text = result.get('text', '')
                meta = result.get('meta', {})
                source = meta.get('source', 'Unknown')
                if text.strip():  # Only add non-empty text
                    context_parts.append(f"[Source: {source}]:\n{text}\n")
                
            context = "\n".join(context_parts)
            
            # If no good context, provide fallback Rails 7 information
            if len(context.strip()) < 100:
                context = self._get_rails7_fallback_context()
                print("📝 Using fallback Rails 7 context")
            
            # Create a more conversational prompt for query mode
            prompt = f"""You are a Rails upgrade expert. Answer this specific question about Rails upgrades.

Question: {query}

Rails Documentation Context:
{context}

Based on the context above, provide a clear, helpful answer about Rails upgrades. Focus on:
- Specific deprecations and changes
- Code examples showing before/after
- Practical upgrade steps
- Version-specific considerations

If the question is about Rails 7 specifically, cover the major changes like Zeitwerk, Hotwire, asset pipeline changes, and deprecated features.

Answer:"""

            response = self.llm.generate(prompt, max_new_tokens=800, temperature=0.3)
            
            # Clean the response - stop at common hallucination patterns
            cleaned_response = self._clean_llm_response(response)
            
            # Display the response
            self.response_title.config(text=f"💬 Response to: {query}")
            self.response_text.delete(1.0, tk.END)
            
            formatted_response = f"""❓ Question: {query}

🤖 AI Response:
Answer: 
{cleaned_response}

📚 Sources consulted:
"""
            
            for i, result in enumerate(results[:3], 1):
                meta = result.get('meta', {})
                source = meta.get('source', 'Unknown')
                formatted_response += f"{i}. {source}\n"
                
            self.response_text.insert(1.0, formatted_response)
            self.status_var.set("✅ AI response generated")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get AI response: {str(e)}")
            self.status_var.set("❌ Error getting response")
    
    def _clean_llm_response(self, response):
        """Clean LLM response to remove hallucinations and unrelated content."""
        if not response:
            return "No response generated."
        
        # Common patterns that indicate the model started hallucinating
        stop_patterns = [
            "---\nlayout:",
            "layout: post",
            "title:",
            "date:",
            "categories:",
            "author:",
            "Building a CLI",
            "import argparse",
            "pip install",
            "```bash\npip install",
            "Let's take a look at",
            "For example, let's imagine",
            "Firstly, install",
            "Then you can proceed"
        ]
        
        # Split response into lines for processing
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Check if this line contains any stop pattern
            should_stop = False
            for pattern in stop_patterns:
                if pattern.lower() in line.lower():
                    should_stop = True
                    break
            
            if should_stop:
                break
                
            cleaned_lines.append(line)
        
        # Join back and do final cleanup
        cleaned = '\n'.join(cleaned_lines).strip()
        
        # Remove trailing incomplete sentences or code blocks
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3].strip()
        
        # If response is too short, return original
        if len(cleaned) < 50:
            return response
            
        return cleaned
    
    def _get_rails7_fallback_context(self):
        """Provide fallback Rails 7 context when search results are insufficient."""
        return """
[Source: Rails 7.0 Release Notes]:
Rails 7 introduces several significant changes and deprecations:

1. **Zeitwerk becomes the default autoloader** - Classic autoloader is deprecated
2. **Sprockets is no longer the default** - Rails 7 uses importmap-rails by default
3. **ActionText and ActionMailbox** - Now included by default
4. **Hotwire integration** - Turbo and Stimulus are default
5. **Active Storage variants** - New preprocessed variants API

Major Deprecations in Rails 7:
- `config.autoloader = :classic` is deprecated
- `Rails.application.config.force_ssl` behavior changes
- Several ActionView helpers deprecated
- Legacy connection handling in ActionCable
- Sass-rails gem no longer included by default

Breaking Changes:
- Ruby 2.7.0+ required (Ruby 3.0+ recommended)  
- Node.js 12+ required for asset pipeline
- PostgreSQL 10+, MySQL 5.7+, SQLite 3.16+ required
- Some gem dependencies updated with breaking changes

Upgrade Path:
1. Update Ruby to 2.7+ (preferably 3.0+)
2. Run `rails app:update` 
3. Address Zeitwerk compatibility
4. Update asset pipeline configuration
5. Test thoroughly with new defaults
"""
            
    def clear_response(self):
        """Clear the query response."""
        self.response_text.delete(1.0, tk.END)
        self.response_title.config(text="Ask a question to get AI guidance")
        self.query_var.set("")
        
    def use_sample_project(self):
        """Use the included sample project."""
        sample_path = os.path.join(os.path.dirname(__file__), "sample_rails_upgrade")
        if os.path.exists(sample_path):
            self.project_path_var.set(sample_path)
            self.status_var.set("📋 Sample project loaded - click 'Scan Project' to analyze")
        else:
            messagebox.showwarning("Warning", "Sample project not found")
            
    def view_last_report(self):
        """View the last generated report."""
        if self.suggestions:
            self.notebook.select(2)  # Switch to report tab
            self.update_report()
        else:
            messagebox.showinfo("Info", "No reports available - scan a project first")
        
    def create_report_tab(self):
        """Create the report tab."""
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="📊 Report")
        
        # Configure grid
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(1, weight=1)
        
        # Report controls
        controls_frame = ttk.Frame(report_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="🔄 Refresh Report", 
                  command=self.update_report).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="💾 Export Report", 
                  command=self.export_report).pack(side=tk.LEFT)
        
        # Report display
        self.report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, 
                                                    font=("Consolas", 10))
        self.report_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def search_and_generate(self):
        """Search for relevant content and generate upgrade suggestions."""
        query = self.query_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
            
        self.status_var.set("🔍 Searching for relevant content...")
        self.root.update()
        
        try:
            # Search for relevant content
            results = self.retriever.search(query, top_k=10)
            
            if not results:
                messagebox.showinfo("No Results", "No relevant content found for your query")
                return
                
            self.status_var.set("🤖 Generating upgrade suggestions...")
            self.root.update()
            
            # Generate suggestions using LLM
            suggestions = self.generate_suggestions(query, results)
            
            if suggestions:
                self.suggestions = suggestions
                self.current_suggestion_index = 0
                self.display_current_suggestion()
                self.update_report()
                self.status_var.set(f"✅ Generated {len(suggestions)} suggestions")
            else:
                messagebox.showinfo("No Suggestions", "No upgrade suggestions could be generated")
                self.status_var.set("❌ No suggestions generated")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("❌ Error occurred")
            
    def generate_suggestions(self, query, results):
        """Generate upgrade suggestions based on search results."""
        suggestions = []
        
        # Create context from search results
        context_parts = []
        for i, result in enumerate(results[:5]):  # Use top 5 results
            text = result.get('text', '')
            meta = result.get('meta', {})
            source = meta.get('source', 'Unknown')
            context_parts.append(f"[Result {i+1} from {source}]:\n{text}\n")
            
        context = "\n".join(context_parts)
        
        try:
            if self.use_local_llm and hasattr(self.llm, 'generate_rails_suggestion'):
                # Use structured local LLM method for better results
                suggestion = self.llm.generate_rails_suggestion(
                    query=query,
                    context=context,
                    max_tokens=1024
                )
                
                # Convert single suggestion to list format and add metadata
                if suggestion:
                    suggestion['status'] = 'pending'
                    suggestion['timestamp'] = datetime.now().isoformat()
                    suggestion['query'] = query
                    suggestions = [suggestion]
                    
            else:
                # Use Local LLM with JSON prompt
                prompt = f"""
Based on the Rails upgrade context below, generate specific code upgrade suggestions for: "{query}"

Context:
{context}

Please provide upgrade suggestions in the following JSON format:
{{
  "suggestions": [
    {{
      "file_path": "path/to/file.rb",
      "old_code": "# Current code that needs updating",
      "new_code": "# Updated code for newer Rails version", 
      "explanation": "Why this change is needed and what it improves",
      "confidence": "high|medium|low",
      "rails_version": "7.0",
      "change_type": "deprecation|new_feature|security|performance"
    }}
  ]
}}

Focus on practical, actionable code changes. Each suggestion should show a clear before/after comparison.
Maximum 3 suggestions per query.
"""

                response = self.llm.generate(prompt, max_new_tokens=2000)
                
                # Parse JSON response
                if response and response.strip():
                    # Extract JSON from response if it's wrapped in other text
                    start_idx = response.find('{')
                    end_idx = response.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = response[start_idx:end_idx]
                        data = json.loads(json_str)
                        
                        if 'suggestions' in data:
                            # Add metadata to each suggestion
                            for suggestion in data['suggestions']:
                                suggestion['status'] = 'pending'
                                suggestion['timestamp'] = datetime.now().isoformat()
                                suggestion['query'] = query
                                suggestion['generated_by'] = 'local_llm'
                                
                            suggestions = data['suggestions']
                            
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            
        return suggestions
        
    def display_current_suggestion(self):
        """Display the current suggestion in the UI."""
        if not self.suggestions or self.current_suggestion_index >= len(self.suggestions):
            self.clear_suggestion_display()
            return
            
        suggestion = self.suggestions[self.current_suggestion_index]
        
        # Update navigation label
        total = len(self.suggestions)
        current = self.current_suggestion_index + 1
        self.suggestion_label.config(text=f"Suggestion {current} of {total}")
        
        # Display code comparison
        self.old_code_text.delete(1.0, tk.END)
        self.old_code_text.insert(1.0, suggestion.get('old_code', ''))
        
        self.new_code_text.delete(1.0, tk.END)
        self.new_code_text.insert(1.0, suggestion.get('new_code', ''))
        
        # Display details
        self.file_path_var.set(suggestion.get('file_path', 'Unknown'))
        confidence = suggestion.get('confidence', 'unknown')
        status = suggestion.get('status', 'pending')
        self.confidence_var.set(f"{confidence.title()} - Status: {status.title()}")
        
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.insert(1.0, suggestion.get('explanation', ''))
        
    def clear_suggestion_display(self):
        """Clear the suggestion display when no suggestions are available."""
        self.suggestion_label.config(text="No suggestions available")
        self.old_code_text.delete(1.0, tk.END)
        self.new_code_text.delete(1.0, tk.END)
        self.file_path_var.set("")
        self.confidence_var.set("")
        self.explanation_text.delete(1.0, tk.END)
        
    def previous_suggestion(self):
        """Navigate to previous suggestion."""
        if self.suggestions and self.current_suggestion_index > 0:
            self.current_suggestion_index -= 1
            self.display_current_suggestion()
            
    def next_suggestion(self):
        """Navigate to next suggestion."""
        if self.suggestions and self.current_suggestion_index < len(self.suggestions) - 1:
            self.current_suggestion_index += 1
            self.display_current_suggestion()
            
    def accept_suggestion(self):
        """Accept the current suggestion."""
        if self.suggestions and self.current_suggestion_index < len(self.suggestions):
            self.suggestions[self.current_suggestion_index]['status'] = 'accepted'
            self.display_current_suggestion()  # Refresh display
            self.status_var.set("✅ Suggestion accepted")
            
    def reject_suggestion(self):
        """Reject the current suggestion."""
        if self.suggestions and self.current_suggestion_index < len(self.suggestions):
            self.suggestions[self.current_suggestion_index]['status'] = 'rejected'
            self.display_current_suggestion()  # Refresh display
            self.status_var.set("❌ Suggestion rejected")
            
    def skip_suggestion(self):
        """Skip the current suggestion."""
        if self.suggestions and self.current_suggestion_index < len(self.suggestions):
            self.suggestions[self.current_suggestion_index]['status'] = 'skipped'
            self.display_current_suggestion()  # Refresh display
            self.status_var.set("⏭️ Suggestion skipped")
            
    def update_report(self):
        """Update the report display."""
        if not self.suggestions:
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, "No suggestions to report on.")
            return
            
        # Generate report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("RAILS UPGRADE ASSISTANT REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total Suggestions: {len(self.suggestions)}")
        report_lines.append("")
        
        # Summary statistics
        accepted = len([s for s in self.suggestions if s['status'] == 'accepted'])
        rejected = len([s for s in self.suggestions if s['status'] == 'rejected'])
        skipped = len([s for s in self.suggestions if s['status'] == 'skipped'])
        pending = len([s for s in self.suggestions if s['status'] == 'pending'])
        
        report_lines.append("SUMMARY:")
        report_lines.append(f"  ✅ Accepted: {accepted}")
        report_lines.append(f"  ❌ Rejected: {rejected}")
        report_lines.append(f"  ⏭️ Skipped: {skipped}")
        report_lines.append(f"  ⏳ Pending: {pending}")
        report_lines.append("")
        
        # Detailed suggestions
        report_lines.append("DETAILED SUGGESTIONS:")
        report_lines.append("-" * 50)
        
        for i, suggestion in enumerate(self.suggestions):
            status_emoji = {
                'accepted': '✅',
                'rejected': '❌', 
                'skipped': '⏭️',
                'pending': '⏳'
            }.get(suggestion['status'], '❓')
            
            report_lines.append(f"\n{i+1}. {status_emoji} {suggestion.get('file_path', 'Unknown file')}")
            report_lines.append(f"   Status: {suggestion['status'].title()}")
            report_lines.append(f"   Confidence: {suggestion.get('confidence', 'unknown').title()}")
            report_lines.append(f"   Query: {suggestion.get('query', 'Unknown')}")
            report_lines.append(f"   Explanation: {suggestion.get('explanation', 'No explanation')}")
            
        # Display report
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, "\n".join(report_lines))
        
    def browse_project(self):
        """Browse for a Rails project directory."""
        project_dir = filedialog.askdirectory(
            title="Select Rails Project Directory"
        )
        
        if project_dir:
            self.project_path_var.set(project_dir)
            
    def scan_project(self):
        """Scan the selected Rails project."""
        project_path = self.project_path_var.get().strip()
        
        if not project_path:
            messagebox.showwarning("Warning", "Please select a Rails project directory")
            return
            
        if not os.path.exists(project_path):
            messagebox.showerror("Error", f"Directory does not exist: {project_path}")
            return
            
        self.status_var.set("🔍 Scanning Rails project...")
        self.root.update()
        
        try:
            # Scan the project
            self.project_analysis = self.scanner.scan_project(project_path)
            
            if not self.project_analysis['is_rails_project']:
                messagebox.showwarning("Warning", 
                                     "The selected directory does not appear to be a Rails project.\n"
                                     "Make sure it contains a Gemfile with Rails dependency.")
                return
                
            # Update UI with analysis results
            self.update_analysis_display()
            
            # Generate suggestions from the analysis
            if self.project_analysis['suggestions']:
                self.suggestions = self.project_analysis['suggestions']
                self.current_suggestion_index = 0
                self.display_current_suggestion()
                self.update_report()
                
                # Switch to Code Review tab
                self.notebook.select(0)
                
                self.status_var.set(f"✅ Scanned project: {len(self.suggestions)} suggestions generated")
            else:
                self.status_var.set("✅ Project scanned: No issues found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan project: {str(e)}")
            self.status_var.set("❌ Project scan failed")
            
    def update_analysis_display(self):
        """Update the project analysis tab with scan results."""
        if not self.project_analysis:
            return
            
        # Update project info
        self.project_path_label.config(text=self.project_analysis['project_path'], foreground="black")
        
        rails_version = self.project_analysis.get('rails_version', 'Unknown')
        self.rails_version_label.config(text=rails_version, foreground="black")
        
        total_issues = self.project_analysis.get('summary', {}).get('total_issues', 0)
        self.issues_count_label.config(text=str(total_issues), foreground="black")
        
        # Update priorities display
        self.priorities_text.delete(1.0, tk.END)
        
        # Get upgrade priorities
        priorities = self.scanner.get_upgrade_priority(self.project_analysis)
        
        analysis_content = []
        analysis_content.append("=" * 60)
        analysis_content.append("RAILS PROJECT ANALYSIS REPORT")
        analysis_content.append("=" * 60)
        analysis_content.append("")
        
        # Project overview
        analysis_content.append("📋 PROJECT OVERVIEW:")
        analysis_content.append(f"   Path: {self.project_analysis['project_path']}")
        analysis_content.append(f"   Rails Version: {rails_version}")
        analysis_content.append(f"   Total Issues: {total_issues}")
        analysis_content.append("")
        
        # Upgrade priorities
        analysis_content.append("🎯 UPGRADE PRIORITIES:")
        for i, priority in enumerate(priorities, 1):
            analysis_content.append(f"   {i}. {priority}")
        if not priorities:
            analysis_content.append("   ✅ No critical issues found")
        analysis_content.append("")
        
        # Issue breakdown
        summary = self.project_analysis.get('summary', {})
        if summary.get('by_severity'):
            analysis_content.append("📊 ISSUES BY SEVERITY:")
            for severity, count in summary['by_severity'].items():
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
                analysis_content.append(f"   {severity_icon} {severity.title()}: {count}")
            analysis_content.append("")
            
        if summary.get('by_category'):
            analysis_content.append("🏷️ ISSUES BY CATEGORY:")
            for category, count in summary['by_category'].items():
                category_name = category.replace('_', ' ').title().replace('Rails ', 'Rails ')
                analysis_content.append(f"   • {category_name}: {count}")
            analysis_content.append("")
        
        # Detailed suggestions
        suggestions = self.project_analysis.get('suggestions', [])
        if suggestions:
            analysis_content.append("📝 DETAILED SUGGESTIONS:")
            analysis_content.append("-" * 40)
            
            for i, suggestion in enumerate(suggestions[:10], 1):  # Show first 10
                file_path = suggestion.get('file_path', 'Unknown')
                # Show relative path for readability
                if self.project_analysis['project_path'] in file_path:
                    file_path = file_path.replace(self.project_analysis['project_path'], '').lstrip('\\/')
                    
                severity = suggestion.get('severity', 'medium')
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
                
                analysis_content.append(f"\n{i}. {severity_icon} {file_path}")
                analysis_content.append(f"   Line {suggestion.get('line_number', '?')}: {suggestion.get('explanation', 'No explanation')}")
                analysis_content.append(f"   Confidence: {suggestion.get('confidence', 'unknown').title()}")
                
            if len(suggestions) > 10:
                analysis_content.append(f"\n... and {len(suggestions) - 10} more suggestions")
                analysis_content.append("Switch to Code Review tab to see all suggestions")
            
        self.priorities_text.insert(1.0, "\n".join(analysis_content))
        
        # Switch to analysis tab
        self.notebook.select(1)
        
    def export_report(self):
        """Export the report to a file."""
        if not self.suggestions:
            messagebox.showwarning("Warning", "No suggestions to export")
            return
            
        # Ask user for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            title="Export Report"
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    # Export as JSON
                    report_data = {
                        'generated_at': datetime.now().isoformat(),
                        'total_suggestions': len(self.suggestions),
                        'summary': {
                            'accepted': len([s for s in self.suggestions if s['status'] == 'accepted']),
                            'rejected': len([s for s in self.suggestions if s['status'] == 'rejected']),
                            'skipped': len([s for s in self.suggestions if s['status'] == 'skipped']),
                            'pending': len([s for s in self.suggestions if s['status'] == 'pending'])
                        },
                        'suggestions': self.suggestions
                    }
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(report_data, f, indent=2, ensure_ascii=False)
                else:
                    # Export as text
                    report_content = self.report_text.get(1.0, tk.END)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(report_content)
                        
                messagebox.showinfo("Success", f"Report exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")

def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = RailsUpgradeGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
