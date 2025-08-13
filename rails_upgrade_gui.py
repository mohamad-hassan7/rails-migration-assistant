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
    from src.model.gemini_llm import GeminiLLM
    from src.model.local_llm import LocalLLM
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
        
        # LLM selection (start with Gemini, can switch to local)
        self.use_local_llm = False
        self.llm = None
        self.local_llm = None
        self._initialize_llm()
        
        # Track suggestions and their status
        self.suggestions = []
        self.current_suggestion_index = 0
        
        self.create_widgets()
    
    def _initialize_llm(self):
        """Initialize the LLM based on user preference."""
        try:
            if not self.use_local_llm:
                self.llm = GeminiLLM()
            else:
                if self.local_llm is None:
                    self.local_llm = LocalLLM(use_4bit=True)
                self.llm = self.local_llm
        except Exception as e:
            messagebox.showerror("LLM Error", f"Failed to initialize LLM: {str(e)}")
            # Fallback to the other option
            self.use_local_llm = not self.use_local_llm
            try:
                if not self.use_local_llm:
                    self.llm = GeminiLLM()
                else:
                    if self.local_llm is None:
                        self.local_llm = LocalLLM(use_4bit=True)
                    self.llm = self.local_llm
            except Exception as e2:
                messagebox.showerror("Critical Error", f"Failed to initialize any LLM: {str(e2)}")
                self.llm = None
        
    def create_widgets(self):
        """Create the GUI layout."""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title and LLM selection
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="🚀 Rails Upgrade Assistant", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # LLM selection frame
        llm_frame = ttk.Frame(header_frame)
        llm_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Label(llm_frame, text="AI Model:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.llm_var = tk.StringVar(value="Gemini API" if not self.use_local_llm else "Local LLM")
        llm_combo = ttk.Combobox(llm_frame, textvariable=self.llm_var, 
                                values=["Gemini API", "Local LLM"], state="readonly", width=12)
        llm_combo.pack(side=tk.LEFT, padx=(0, 5))
        llm_combo.bind("<<ComboboxSelected>>", self.on_llm_change)
        
        # LLM status indicator
        self.llm_status_var = tk.StringVar(value="🟢 Ready" if self.llm else "🔴 Error")
        ttk.Label(llm_frame, textvariable=self.llm_status_var, font=("Arial", 9)).pack(side=tk.LEFT)
        
        # Query input section
        query_frame = ttk.LabelFrame(main_frame, text="Search Query", padding="5")
        query_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        query_frame.columnconfigure(0, weight=1)
        
        self.query_var = tk.StringVar()
        query_entry = ttk.Entry(query_frame, textvariable=self.query_var, font=("Arial", 11))
        query_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Enhanced search button with model info
        search_btn = ttk.Button(query_frame, text="🔍 Generate AI Suggestions", 
                               command=self.search_and_generate)
        search_btn.grid(row=0, column=1)
        
        # Main content area with notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tab 1: Code Review
        self.create_review_tab()
        
        # Tab 2: Report
        self.create_report_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Enter a search query to get started")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
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
    
    def on_llm_change(self, event=None):
        """Handle LLM model change."""
        selected_llm = self.llm_var.get()
        
        if selected_llm == "Local LLM" and not self.use_local_llm:
            self.status_var.set("🔄 Switching to Local LLM...")
            self.root.update()
            
            try:
                self.use_local_llm = True
                self._initialize_llm()
                self.llm_status_var.set("🟢 Local Ready")
                self.status_var.set("✅ Switched to Local LLM")
                
                # Show model info
                if hasattr(self.llm, 'get_model_info'):
                    info = self.llm.get_model_info()
                    messagebox.showinfo("Local LLM", 
                                       f"Model: {info['name'].split('/')[-1]}\n"
                                       f"Quantization: {info['quantization']}\n"
                                       f"Device: {info['device']}\n\n"
                                       f"✅ Ready for secure, offline processing!")
                
            except Exception as e:
                self.use_local_llm = False
                self.llm_var.set("Gemini API")
                self.llm_status_var.set("🔴 Local Failed")
                messagebox.showerror("Local LLM Error", 
                                   f"Failed to load local model: {str(e)}\n\n"
                                   f"Falling back to Gemini API.")
                
        elif selected_llm == "Gemini API" and self.use_local_llm:
            self.status_var.set("🔄 Switching to Gemini API...")
            self.root.update()
            
            try:
                self.use_local_llm = False
                self._initialize_llm()
                self.llm_status_var.set("🟢 API Ready")
                self.status_var.set("✅ Switched to Gemini API")
                
            except Exception as e:
                self.use_local_llm = True
                self.llm_var.set("Local LLM")
                self.llm_status_var.set("🔴 API Failed")
                messagebox.showerror("Gemini API Error", 
                                   f"Failed to initialize Gemini API: {str(e)}\n\n"
                                   f"Please check your API key.")
            
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
                # Use Gemini API with JSON prompt
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
                                suggestion['generated_by'] = 'gemini_api'
                                
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
