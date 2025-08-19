#!/usr/bin/env python3
"""
Rails Migration Assistant - Professional GUI Application
======================================================

A comprehensive tool for migrating Ruby on Rails applications between major versions.
Features local AI-powered analysis, security scanning, and automated upgrade suggestions.

Author: Rails Migration Assistant Team
Version: 2.0
License: MIT
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
import queue
from datetime import datetime
from typing import List, Dict, Any
import traceback

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Import the analyzer
    from src.analyzer.hybrid_analyzer import HybridRailsAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import analyzer: {e}")
    print("   Some features may be limited.")
    ANALYZER_AVAILABLE = False

class RailsMigrationAssistantGUI:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Rails Migration Assistant - Professional Edition")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set application icon and styling
        try:
            # Professional color scheme
            self.root.configure(bg='#f8f9fa')
            style = ttk.Style()
            style.theme_use('clam')
        except Exception:
            pass  # Fallback to default styling
        
        # Variables
        self.project_path_var = tk.StringVar()
        self.target_version_var = tk.StringVar(value="7.0")
        self.backup_enabled_var = tk.BooleanVar(value=True)
        self.backup_location = None  # User-selected backup location
        self.status_var = tk.StringVar(value="🔄 Initializing...")
        
        # Analysis state
        self.suggestions = []
        self.current_suggestion_index = 0
        self.is_scanning = False
        
        # Initialize analyzer with error handling
        self.analyzer = None
        if ANALYZER_AVAILABLE:
            try:
                print("🚀 Initializing Rails Migration Assistant...")
                self.analyzer = HybridRailsAnalyzer()
                self.status_var.set("✅ Rails Migration Assistant ready")
                print("✅ Initialization complete!")
            except Exception as e:
                error_msg = f"❌ Error initializing analyzer: {str(e)[:100]}..."
                self.status_var.set(error_msg)
                print(f"❌ Initialization failed: {e}")
                traceback.print_exc()
        else:
            self.status_var.set("❌ Analyzer not available - check installation")
        
        # Threading
        self.progress_queue = queue.Queue()
        self.scanning_thread = None
        
        # Create interface
        self.create_widgets()
        self.check_progress_queue()
        
    def create_widgets(self):
        """Create the simple GUI layout."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 Rails Upgrade Assistant", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Project selection
        project_frame = ttk.LabelFrame(main_frame, text="📁 Select Rails Project", padding="10")
        project_frame.pack(fill=tk.X, pady=(0, 10))
        
        project_inner = ttk.Frame(project_frame)
        project_inner.pack(fill=tk.X)
        
        ttk.Entry(project_inner, textvariable=self.project_path_var, 
                 font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(project_inner, text="Browse", 
                  command=self.browse_project).pack(side=tk.RIGHT)
        
        # Analysis controls
        control_frame = ttk.LabelFrame(main_frame, text="🔧 Analysis Options", padding="10")
        control_frame.pack(fill=tk.X, pady=10)
        
        # Controls layout
        controls_inner = ttk.Frame(control_frame)
        controls_inner.pack(fill=tk.X)
        
        # Target version
        ttk.Label(controls_inner, text="Target Version:").pack(side=tk.LEFT, padx=(0, 5))
        version_combo = ttk.Combobox(controls_inner, textvariable=self.target_version_var,
                                   values=["6.0", "6.1", "7.0", "7.1"], 
                                   state="readonly", width=8)
        version_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Backup checkbox with location selection
        backup_frame = ttk.Frame(controls_inner)
        backup_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        backup_check = ttk.Checkbutton(backup_frame, text="Create backup before changes",
                                      variable=self.backup_enabled_var)
        backup_check.pack(side=tk.LEFT)
        
        ttk.Button(backup_frame, text="📁 Choose Location", 
                  command=self.choose_backup_location).pack(side=tk.LEFT, padx=(5, 0))
        
        # Analyze button
        self.scan_button = ttk.Button(controls_inner, text="🔍 Analyze Project", 
                                     command=self.scan_project,
                                     style="Accent.TButton")
        self.scan_button.pack(side=tk.RIGHT)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="📊 Analysis Results", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create notebook for results
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Code Review tab
        self.create_code_review_tab()
        
        # Analysis tab
        self.create_analysis_tab()
        
        # Report tab
        self.create_report_tab()
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
    def create_code_review_tab(self):
        """Create the code review tab."""
        review_frame = ttk.Frame(self.notebook)
        self.notebook.add(review_frame, text="📝 Code Review")
        
        # Navigation
        nav_frame = ttk.Frame(review_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(nav_frame, text="◀ Previous", 
                  command=self.previous_suggestion).pack(side=tk.LEFT)
        
        self.suggestion_label = ttk.Label(nav_frame, text="No suggestions loaded", 
                                         font=("Arial", 11, "bold"))
        self.suggestion_label.pack(side=tk.LEFT, padx=(20, 20))
        
        ttk.Button(nav_frame, text="Next ▶", 
                  command=self.next_suggestion).pack(side=tk.LEFT)
        
        # File information
        file_info_frame = ttk.LabelFrame(review_frame, text="📁 File Information", padding="5")
        file_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_info_label = ttk.Label(file_info_frame, text="No file selected", 
                                        font=("Arial", 10))
        self.file_info_label.pack(anchor=tk.W)
        
        # Code comparison - limit height to allow space for explanation
        comparison_frame = ttk.Frame(review_frame)
        comparison_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        comparison_frame.columnconfigure(0, weight=1)
        comparison_frame.columnconfigure(1, weight=1)
        comparison_frame.rowconfigure(0, weight=1)
        
        # Current code
        current_frame = ttk.LabelFrame(comparison_frame, text="📄 Current Code", padding="5")
        current_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        current_frame.columnconfigure(0, weight=1)
        current_frame.rowconfigure(0, weight=1)
        
        self.current_code_text = scrolledtext.ScrolledText(current_frame, 
                                                          height=8,  # Fixed height
                                                          wrap=tk.WORD, 
                                                          font=("Consolas", 10),
                                                          background="#fff8dc")
        self.current_code_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Suggested code
        suggested_frame = ttk.LabelFrame(comparison_frame, text="✨ Suggested Code", padding="5")
        suggested_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        suggested_frame.columnconfigure(0, weight=1)
        suggested_frame.rowconfigure(0, weight=1)
        
        self.suggested_code_text = scrolledtext.ScrolledText(suggested_frame, 
                                                           height=8,  # Fixed height
                                                           wrap=tk.WORD, 
                                                           font=("Consolas", 10),
                                                           background="#f0fff0")
        self.suggested_code_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Explanation section with proper scrolling
        explanation_frame = ttk.LabelFrame(review_frame, text="📋 Explanation", padding="5")
        explanation_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        explanation_frame.columnconfigure(0, weight=1)
        explanation_frame.rowconfigure(0, weight=1)
        
        self.explanation_text = scrolledtext.ScrolledText(explanation_frame, 
                                                         wrap=tk.WORD, 
                                                         font=("Arial", 10),
                                                         height=8,  # Proper height for scrolling
                                                         relief=tk.SUNKEN,
                                                         borderwidth=2)
        self.explanation_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(review_frame)
        action_frame.pack(pady=(10, 0))
        
        ttk.Button(action_frame, text="✅ Accept", 
                  command=self.accept_suggestion).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="❌ Reject", 
                  command=self.reject_suggestion).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="⏭️ Skip", 
                  command=self.skip_suggestion).pack(side=tk.LEFT)
        
    def create_analysis_tab(self):
        """Create the analysis results tab."""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="📊 Analysis")
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, 
                                                      wrap=tk.WORD, 
                                                      font=("Arial", 10))
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        
    def create_report_tab(self):
        """Create the report generation tab."""
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="📋 Reports")
        
        # Report options
        options_frame = ttk.LabelFrame(report_frame, text="Report Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Report type selection
        self.report_type_var = tk.StringVar(value="summary")
        ttk.Label(options_frame, text="Report Type:").pack(anchor=tk.W)
        
        report_options = ttk.Frame(options_frame)
        report_options.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Radiobutton(report_options, text="Summary Report", 
                       variable=self.report_type_var, value="summary").pack(anchor=tk.W)
        ttk.Radiobutton(report_options, text="Detailed Report", 
                       variable=self.report_type_var, value="detailed").pack(anchor=tk.W)
        ttk.Radiobutton(report_options, text="Applied Changes Report", 
                       variable=self.report_type_var, value="applied").pack(anchor=tk.W)
        
        # Generate button
        generate_frame = ttk.Frame(options_frame)
        generate_frame.pack(fill=tk.X)
        
        ttk.Button(generate_frame, text="📄 Generate Report", 
                  command=self.generate_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(generate_frame, text="💾 Export Report", 
                  command=self.export_report).pack(side=tk.LEFT)
        
        # Report display
        report_display_frame = ttk.LabelFrame(report_frame, text="Generated Report", padding="5")
        report_display_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.report_text = scrolledtext.ScrolledText(report_display_frame, 
                                                    wrap=tk.WORD, 
                                                    font=("Consolas", 9))
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
    def browse_project(self):
        """Browse for Rails project directory."""
        directory = filedialog.askdirectory(title="Select Rails Project Directory")
        if directory:
            self.project_path_var.set(directory)
            
    def choose_backup_location(self):
        """Choose backup location using file dialog."""
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="Select Backup Location")
        if folder:
            self.backup_location = folder
            messagebox.showinfo("Backup Location", f"Backup location set to:\n{folder}")
        
    def scan_project(self):
        """Scan the Rails project."""
        if self.is_scanning:
            messagebox.showinfo("Info", "Analysis already in progress...")
            return
            
        project_path = self.project_path_var.get().strip()
        if not project_path:
            messagebox.showwarning("Warning", "Please select a Rails project directory")
            return
            
        if not os.path.exists(project_path):
            messagebox.showerror("Error", f"Directory does not exist: {project_path}")
            return
            
        if not self.analyzer:
            messagebox.showerror("Error", "Analyzer not initialized")
            return
            
        # Start analysis in background
        self.is_scanning = True
        self.scan_button.config(text="⏳ Analyzing...", state='disabled')
        self.status_var.set("🔍 Analyzing project...")
        
        self.scanning_thread = threading.Thread(
            target=self._analyze_project_worker,
            args=(project_path,),
            daemon=True
        )
        self.scanning_thread.start()
        
    def _analyze_project_worker(self, project_path):
        """Worker thread for project analysis."""
        try:
            self.progress_queue.put({'type': 'status', 'text': '🔍 Scanning project files...'})
            
            # Find Ruby files
            ruby_files = []
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['vendor', 'node_modules', 'tmp', 'log', '.git']]
                for file in files:
                    if file.endswith(('.rb', '.erb')) or file in ['Gemfile', 'Rakefile']:
                        ruby_files.append(os.path.join(root, file))
            
            self.progress_queue.put({'type': 'status', 'text': f'📁 Found {len(ruby_files)} files to analyze'})
            
            # Analyze files with proper delay
            all_suggestions = []
            for i, file_path in enumerate(ruby_files):
                self.progress_queue.put({
                    'type': 'progress', 
                    'current': i + 1, 
                    'total': len(ruby_files),
                    'file': os.path.basename(file_path)
                })
                
                try:
                    # Get target version from dropdown
                    target_version = self.target_version_var.get()
                    
                    # Add small delay to show progress (not too fast)
                    import time
                    time.sleep(0.1)
                    
                    # Analyze with hybrid analyzer
                    results = self.analyzer.analyze_file(file_path, target_version)
                    
                    # Process suggestions with correct key mapping
                    for suggestion in results.get('suggestions', []):
                        # Map the analyzer output to GUI expected format
                        mapped_suggestion = {
                            'file_path': file_path,
                            'old_code': suggestion.get('original_code', ''),  # Correct mapping
                            'new_code': suggestion.get('refactored_code', ''), # Correct mapping  
                            'explanation': suggestion.get('explanation', ''),
                            'confidence': suggestion.get('confidence', 0.8),
                            'issue_type': suggestion.get('issue_type', 'Unknown'),
                            'line_number': suggestion.get('line_number', None),
                            'tier': suggestion.get('tier', 'unknown')
                        }
                        
                        # Debug what we're getting from the analyzer
                        print(f"   📋 Suggestion from {os.path.basename(file_path)}:")
                        print(f"      Type: {mapped_suggestion['issue_type']}")
                        print(f"      Old code: '{mapped_suggestion['old_code'][:50]}...' " if mapped_suggestion['old_code'] else "      Old code: EMPTY")
                        print(f"      New code: '{mapped_suggestion['new_code'][:50]}...' " if mapped_suggestion['new_code'] else "      New code: EMPTY")
                        
                        # Only add if we have actual changes (old != new) OR if it's a general suggestion
                        should_add = False
                        if mapped_suggestion['old_code'] and mapped_suggestion['new_code']:
                            if mapped_suggestion['old_code'].strip() != mapped_suggestion['new_code'].strip():
                                should_add = True
                                print(f"      ✅ Added: Has different old/new code")
                            else:
                                print(f"      ❌ Skipped: Old and new code are the same")
                        elif mapped_suggestion['explanation']:
                            # Add suggestions with explanations even if no code diff
                            should_add = True
                            print(f"      ✅ Added: Has explanation (no code diff needed)")
                        else:
                            print(f"      ❌ Skipped: No code diff and no explanation")
                            
                        if should_add:
                            all_suggestions.append(mapped_suggestion)
                        
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
                    # Add delay even on error to show progress
                    import time
                    time.sleep(0.05)
                    continue
            
            # Send completion
            print(f"\n🎯 Analysis Complete: Found {len(all_suggestions)} total suggestions")
            self.progress_queue.put({
                'type': 'complete',
                'suggestions': all_suggestions
            })
            
        except Exception as e:
            self.progress_queue.put({'type': 'error', 'text': str(e)})
            
    def check_progress_queue(self):
        """Check for progress updates."""
        try:
            while True:
                message = self.progress_queue.get_nowait()
                
                if message['type'] == 'status':
                    self.status_var.set(message['text'])
                elif message['type'] == 'progress':
                    # Show detailed progress with percentage
                    percent = int((message['current'] / message['total']) * 100)
                    status_text = f"🔍 Analyzing {message['current']}/{message['total']} ({percent}%): {message['file']}"
                    self.status_var.set(status_text)
                elif message['type'] == 'complete':
                    self.handle_analysis_complete(message['suggestions'])
                elif message['type'] == 'error':
                    self.status_var.set(f"❌ Error: {message['text']}")
                    messagebox.showerror("Error", f"Analysis failed: {message['text']}")
                    self.reset_scan_button()
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_progress_queue)
        
    def handle_analysis_complete(self, suggestions):
        """Handle completed analysis."""
        self.suggestions = suggestions
        self.current_suggestion_index = 0
        
        if suggestions:
            self.display_current_suggestion()
            self.notebook.select(0)  # Switch to code review tab
            
            # Show detailed completion status
            total_files = len(set(s['file_path'] for s in suggestions))
            self.status_var.set(f"✅ Analysis complete: {len(suggestions)} suggestions found in {total_files} files")
            
            # Update analysis tab with detailed breakdown
            analysis_text = f"🎯 Analysis Complete!\n\n"
            analysis_text += f"📊 Summary:\n"
            analysis_text += f"   • Total suggestions: {len(suggestions)}\n"
            analysis_text += f"   • Files with issues: {total_files}\n"
            analysis_text += f"   • Target Rails version: {self.target_version_var.get()}\n\n"
            
            # Group by issue type
            issue_types = {}
            for suggestion in suggestions:
                issue_type = suggestion.get('issue_type', 'Unknown')
                if issue_type not in issue_types:
                    issue_types[issue_type] = 0
                issue_types[issue_type] += 1
                
            analysis_text += "Issues by type:\n"
            for issue_type, count in issue_types.items():
                analysis_text += f"• {issue_type}: {count}\n"
                
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, analysis_text)
        else:
            self.status_var.set("✅ No issues found!")
            
        self.reset_scan_button()
        
    def display_current_suggestion(self):
        """Display the current suggestion."""
        if not self.suggestions or self.current_suggestion_index >= len(self.suggestions):
            self.clear_suggestion_display()
            return
            
        suggestion = self.suggestions[self.current_suggestion_index]
        
        # Update label
        total = len(self.suggestions)
        current = self.current_suggestion_index + 1
        self.suggestion_label.config(text=f"Suggestion {current} of {total}")
        
        # Update file information
        file_path = suggestion.get('file_path', 'Unknown file')
        issue_type = suggestion.get('issue_type', 'Unknown')
        confidence = suggestion.get('confidence', 'N/A')
        
        file_name = os.path.basename(file_path) if file_path != 'Unknown file' else 'Unknown file'
        file_info = f"📁 File: {file_name} | Type: {issue_type} | Confidence: {confidence}"
        
        # Add line information if available (you may need to extract this from the suggestion)
        if 'line_number' in suggestion:
            file_info += f" | Line: {suggestion['line_number']}"
        
        self.file_info_label.config(text=file_info)
        
        # Display code
        old_code = suggestion.get('old_code', '')
        new_code = suggestion.get('new_code', '')
        explanation = suggestion.get('explanation', '')
        
        self.current_code_text.delete(1.0, tk.END)
        self.current_code_text.insert(1.0, old_code if old_code else "No current code available")
        
        self.suggested_code_text.delete(1.0, tk.END)
        self.suggested_code_text.insert(1.0, new_code if new_code else "No suggested code available")
        
        # Display explanation
        self.explanation_text.delete(1.0, tk.END)
        if explanation:
            self.explanation_text.insert(1.0, explanation)
        else:
            # Create a basic explanation if none provided
            issue_type = suggestion.get('issue_type', 'Unknown')
            confidence = suggestion.get('confidence', 0.8)
            file_path = suggestion.get('file_path', '')
            basic_explanation = f"Issue Type: {issue_type}\nConfidence: {confidence:.1f}\nFile: {os.path.basename(file_path)}\n\nThis suggestion was generated by the Rails upgrade analyzer."
            self.explanation_text.insert(1.0, basic_explanation)
        
    def clear_suggestion_display(self):
        """Clear the suggestion display."""
        self.suggestion_label.config(text="No suggestions available")
        self.file_info_label.config(text="No file selected")
        self.current_code_text.delete(1.0, tk.END)
        self.suggested_code_text.delete(1.0, tk.END)
        self.explanation_text.delete(1.0, tk.END)
        
    def previous_suggestion(self):
        """Go to previous suggestion."""
        if self.suggestions and self.current_suggestion_index > 0:
            self.current_suggestion_index -= 1
            self.display_current_suggestion()
            
    def next_suggestion(self):
        """Go to next suggestion."""
        if self.suggestions and self.current_suggestion_index < len(self.suggestions) - 1:
            self.current_suggestion_index += 1
            self.display_current_suggestion()
            
    def accept_suggestion(self):
        """Accept the current suggestion."""
        if self.suggestions and self.current_suggestion_index < len(self.suggestions):
            messagebox.showinfo("Accept", "Suggestion accepted (feature not implemented)")
            self.next_suggestion()
            
    def reject_suggestion(self):
        """Reject the current suggestion."""
        if self.suggestions and self.current_suggestion_index < len(self.suggestions):
            messagebox.showinfo("Reject", "Suggestion rejected")
            self.next_suggestion()
            
    def skip_suggestion(self):
        """Skip the current suggestion."""
        self.next_suggestion()
        
    def generate_report(self):
        """Generate analysis report"""
        if not self.suggestions:
            messagebox.showwarning("No Data", "No analysis results available to generate report.")
            return
            
        report_type = self.report_type_var.get()
        
        if report_type == "Summary":
            report_content = self._generate_summary_report()
        elif report_type == "Detailed":
            report_content = self._generate_detailed_report()
        elif report_type == "Applied Changes":
            report_content = self._generate_applied_changes_report()
        else:
            report_content = "Invalid report type selected."
        
        # Display in text widget
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report_content)
        
    def _generate_summary_report(self):
        """Generate summary report"""
        from datetime import datetime
        
        total_suggestions = len(self.suggestions)
        file_count = len(set(s['file_path'] for s in self.suggestions))
        
        report = f"Rails Migration Analysis Summary\n"
        report += f"{'=' * 40}\n\n"
        report += f"Target Version: {self.target_version_var.get()}\n"
        report += f"Project Path: {self.project_path}\n"
        report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"Total Files with Issues: {file_count}\n"
        report += f"Total Suggestions: {total_suggestions}\n\n"
        
        # Group by file
        files_dict = {}
        for suggestion in self.suggestions:
            file_path = suggestion['file_path']
            if file_path not in files_dict:
                files_dict[file_path] = []
            files_dict[file_path].append(suggestion)
        
        if files_dict:
            report += "Files with Suggestions:\n"
            for file_path, suggestions in files_dict.items():
                report += f"  - {os.path.basename(file_path)}: {len(suggestions)} suggestions\n"
        
        return report
        
    def _generate_detailed_report(self):
        """Generate detailed report"""
        from datetime import datetime
        
        report = f"Rails Migration Analysis - Detailed Report\n"
        report += f"{'=' * 50}\n\n"
        report += f"Target Version: {self.target_version_var.get()}\n"
        report += f"Project Path: {self.project_path}\n"
        report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Group by file
        files_dict = {}
        for suggestion in self.suggestions:
            file_path = suggestion['file_path']
            if file_path not in files_dict:
                files_dict[file_path] = []
            files_dict[file_path].append(suggestion)
        
        for file_path, suggestions in files_dict.items():
            report += f"File: {os.path.basename(file_path)}\n"
            report += f"Full Path: {file_path}\n"
            report += f"{'-' * 60}\n"
            
            for i, suggestion in enumerate(suggestions, 1):
                report += f"\nSuggestion {i}:\n"
                report += f"  Type: {suggestion.get('issue_type', 'N/A')}\n"
                report += f"  Confidence: {suggestion.get('confidence', 'N/A')}\n"
                
                if suggestion.get('explanation'):
                    report += f"  Explanation: {suggestion['explanation']}\n"
                    
                if suggestion.get('old_code'):
                    report += f"  Current Code:\n{suggestion['old_code']}\n"
                if suggestion.get('new_code'):
                    report += f"  Suggested Code:\n{suggestion['new_code']}\n"
            
            report += f"\n{'=' * 60}\n\n"
        
        return report
        
    def _generate_applied_changes_report(self):
        """Generate applied changes report"""
        from datetime import datetime
        
        # This would track which suggestions were actually applied
        # For now, just return a placeholder
        report = f"Applied Changes Report\n"
        report += f"{'=' * 30}\n\n"
        report += f"Target Version: {self.target_version_var.get()}\n"
        report += f"Project Path: {self.project_path}\n"
        report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "Note: Applied changes tracking not yet implemented.\n"
        report += "This feature will track which suggestions were actually applied to your code.\n"
        report += "\nTo implement this feature, suggestions would be marked when:\n"
        report += "- User clicks 'Accept' on a suggestion\n"
        report += "- Code changes are automatically applied\n"
        report += "- Manual verification confirms the change was made\n"
        
        return report
        
    def export_report(self):
        """Export report to file"""
        if not self.report_text.get(1.0, tk.END).strip():
            messagebox.showwarning("No Report", "Please generate a report first.")
            return
            
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Report"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.report_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")
        
    def reset_scan_button(self):
        """Reset scan button state."""
        self.is_scanning = False
        self.scan_button.config(text="🔍 Analyze Project", state='normal')
        
    def run(self):
        """Run the GUI."""
        self.root.mainloop()

def main():
    """Main entry point for the Rails Migration Assistant GUI."""
    try:
        print("🚀 Starting Rails Migration Assistant...")
        app = RailsMigrationAssistantGUI()
        print("🎯 GUI loaded successfully!")
        app.run()
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        traceback.print_exc()
        # Try to show error in a dialog if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror(
                "Rails Migration Assistant Error",
                f"Failed to start application:\n\n{str(e)}\n\nCheck console for details."
            )
        except Exception:
            pass  # If even the error dialog fails, just print to console

if __name__ == "__main__":
    main()
