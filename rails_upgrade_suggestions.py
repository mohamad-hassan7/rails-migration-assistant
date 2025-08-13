#!/usr/bin/env python3
"""
Rails Upgrade Suggestions Generator

A command-line tool to generate Rails upgrade suggestions using the same logic as the GUI.
This is useful for testing and batch processing.

Usage:
  python rails_upgrade_suggestions.py "ApplicationRecord Rails 5"
  python rails_upgrade_suggestions.py "Turbo Rails 7 JavaScript" --output suggestions.json
"""

import sys
import os
import json
import argparse
from datetime import datetime

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

class RailsUpgradeSuggestionGenerator:
    def __init__(self, use_local_llm=False):
        index_path = "data/faiss_combined.index"
        meta_path = "data/meta_combined.jsonl"
        self.retriever = Retriever(index_path, meta_path)
        
        self.use_local_llm = use_local_llm
        
        if use_local_llm:
            print("🚀 Initializing Local LLM for secure processing...")
            self.llm = LocalLLM(use_4bit=True)
        else:
            print("🌐 Initializing Gemini API...")
            self.llm = GeminiLLM()
    
    def generate_suggestions(self, query, max_results=5):
        """Generate upgrade suggestions for a given query."""
        print(f"🔍 Searching for: {query}")
        
        # Search for relevant content
        results = self.retriever.search(query, top_k=10)
        
        if not results:
            print("❌ No relevant content found")
            return []
        
        print(f"✅ Found {len(results)} relevant results")
        print("🤖 Generating upgrade suggestions...")
        
        # Create context from search results
        context_parts = []
        for i, result in enumerate(results[:max_results]):
            text = result.get('text', '')
            meta = result.get('meta', {})
            source = meta.get('source', 'Unknown')
            context_parts.append(f"[Result {i+1} from {source}]:\n{text}\n")
            
        context = "\n".join(context_parts)
        
        # Generate suggestions based on LLM type
        try:
            if self.use_local_llm and hasattr(self.llm, 'generate_rails_suggestion'):
                # Use structured local LLM method
                suggestion = self.llm.generate_rails_suggestion(
                    query=query,
                    context=context,
                    max_tokens=1024
                )
                
                if suggestion:
                    suggestion['status'] = 'pending'
                    suggestion['timestamp'] = datetime.now().isoformat()
                    suggestion['query'] = query
                    print(f"✅ Generated 1 suggestion using Local LLM")
                    return [suggestion]
                else:
                    print("❌ Failed to generate suggestion with Local LLM")
                    return []
            else:
                # Use Gemini API with structured prompt
                prompt = f"""Based on the Rails upgrade context, generate ONE specific code upgrade suggestion for: "{query}"

Context:
{context[:2000]}

Respond with ONLY a clean JSON object in this exact format (no extra text, no markdown):

{{"suggestions":[{{"file_path":"app/models/example.rb","old_code":"# old code here","new_code":"# new code here","explanation":"Brief explanation","confidence":"high","rails_version":"7.0","change_type":"deprecation"}}]}}

Make the suggestion practical and actionable with real Ruby code."""

                response = self.llm.generate(prompt, max_new_tokens=3000)
                
                if response and response.strip():
                    try:
                        # Clean response
                        response = response.strip()
                        
                        # Remove markdown if present
                        if response.startswith('```'):
                            lines = response.split('\n')
                            response = '\n'.join(lines[1:-1]) if len(lines) > 2 else response
                        
                        # Find JSON object
                        start = response.find('{')
                        end = response.rfind('}') + 1
                        
                        if start >= 0 and end > start:
                            json_str = response[start:end]
                            data = json.loads(json_str)
                            
                            if 'suggestions' in data and data['suggestions']:
                                # Add metadata to each suggestion
                                for suggestion in data['suggestions']:
                                    suggestion['status'] = 'pending'
                                    suggestion['timestamp'] = datetime.now().isoformat()
                                    suggestion['query'] = query
                                    suggestion['generated_by'] = 'gemini_api'
                                    
                                print(f"✅ Generated {len(data['suggestions'])} suggestions using Gemini API")
                                return data['suggestions']
                    
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON Parse Error: {e}")
                        # Create a fallback suggestion
                        fallback = {
                            'file_path': 'unknown',
                            'old_code': '# Unable to parse specific code',
                            'new_code': '# Please review the raw response',
                            'explanation': f"Raw AI response: {response[:500]}...",
                            'confidence': 'low',
                            'rails_version': 'unknown',
                            'change_type': 'general',
                            'status': 'pending',
                            'timestamp': datetime.now().isoformat(),
                            'query': query,
                            'generated_by': 'gemini_api_fallback'
                        }
                        return [fallback]
                            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON response: {e}")
            print(f"Raw response: {response[:500]}...")
        except Exception as e:
            print(f"❌ Error generating suggestions: {e}")
            
        return []
    
    def display_suggestions(self, suggestions):
        """Display suggestions in a readable format."""
        if not suggestions:
            print("No suggestions generated.")
            return
            
        print("\n" + "="*80)
        print("GENERATED UPGRADE SUGGESTIONS")
        print("="*80)
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n📝 SUGGESTION {i}")
            print("-" * 40)
            print(f"📁 File: {suggestion.get('file_path', 'Unknown')}")
            print(f"🏷️  Type: {suggestion.get('change_type', 'general')}")
            print(f"🎯 Rails Version: {suggestion.get('rails_version', 'unknown')}")
            print(f"💪 Confidence: {suggestion.get('confidence', 'unknown')}")
            
            print(f"\n📜 CURRENT CODE:")
            print("```ruby")
            print(suggestion.get('old_code', 'No old code provided'))
            print("```")
            
            print(f"\n✨ SUGGESTED CODE:")
            print("```ruby")
            print(suggestion.get('new_code', 'No new code provided'))
            print("```")
            
            print(f"\n💡 EXPLANATION:")
            print(suggestion.get('explanation', 'No explanation provided'))
            
        print("\n" + "="*80)
    
    def save_suggestions(self, suggestions, output_file):
        """Save suggestions to a JSON file."""
        if not suggestions:
            print("No suggestions to save.")
            return
            
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'total_suggestions': len(suggestions),
            'suggestions': suggestions
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Suggestions saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving suggestions: {e}")

def main():
    parser = argparse.ArgumentParser(description='Generate Rails upgrade suggestions')
    parser.add_argument('query', help='Search query for upgrade suggestions')
    parser.add_argument('--output', '-o', help='Output file to save suggestions (JSON format)')
    parser.add_argument('--max-results', type=int, default=5, 
                       help='Maximum number of search results to use for context')
    parser.add_argument('--local', action='store_true',
                       help='Use local LLM instead of Gemini API for secure offline processing')
    
    args = parser.parse_args()
    
    generator = RailsUpgradeSuggestionGenerator(use_local_llm=args.local)
    suggestions = generator.generate_suggestions(args.query, args.max_results)
    
    # Display suggestions
    generator.display_suggestions(suggestions)
    
    # Save if output file specified
    if args.output:
        generator.save_suggestions(suggestions, args.output)

if __name__ == "__main__":
    main()
