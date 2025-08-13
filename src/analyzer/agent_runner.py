#!/usr/bin/env python3
"""
agent_runner.py

Usage examples:
# Run on a single file:
python -m src.analyzer.agent_runner --repo-path "C:\...todo-master" --target-file "app/controllers/tasks_controller.rb"

# Run on whole repo (scans app/controllers and app/models and attempts each)
python -m src.analyzer.agent_runner --repo-path "C:\...todo-master"

Prereqs:
- data/faiss.index, data/meta.jsonl, data/chunks.jsonl exist (run chunk/index steps)
- src/model/local_llm.py is working (you already tested with CodeGPT-small)
- src/retriever/retriever.py is present and index built
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# local project imports (adjust if your package structure differs)
from src.model.local_llm import LocalLLM
from src.model.gemini_llm import GeminiLLM
from src.retriever.retriever import Retriever
from src.patcher.suggestion_formatter import write_patches_from_response

CHUNKS_PATH = Path.cwd() / "data" / "chunks.jsonl"
INDEX_PATH = Path.cwd() / "data" / "faiss.index"
META_PATH = Path.cwd() / "data" / "meta.jsonl"

# Prompt templates for different models
GEMINI_PROMPT_TEMPLATE = """
You are a Rails upgrade expert. Analyze this Ruby on Rails file for compatibility issues when upgrading between Rails versions.

Rails Documentation Context:
{context_passages}

File to analyze: {file_path}
File content:
{file_content}

SAFETY RULES (must follow):
1. Never remove or disable security-related calls (CSRF, authentication, authorization) unless you provide:
   a) exact citation (tag + path + excerpt) proving removal is safe, and
   b) a fully working, tested replacement code snippet, and
   c) mark the edit as "requires_human_review": true.
2. Prefer adding targeted fixes (e.g., change `protect_from_forgery` options, or add `skip_before_action` for named actions) rather than deleting lines.
3. For each suggested edit include a `confidence` field (0.0–1.0) and a `risk` tag: "low" | "medium" | "high".

Please analyze this Rails file and provide structured output in JSON format:

{{
  "file": "{file_path}",
  "edits": [
    {{
      "target_start_line": [line_number],
      "target_end_line": [line_number], 
      "original_code": "[current code]",
      "patch": "[replacement code]",
      "rationale": "[why this change is needed]",
      "confidence": [0.0-1.0],
      "risk": ["low" | "medium" | "high"],
      "requires_human_review": [true/false],
      "sources": [
        {{
          "tag": "[version]",
          "source_path": "[doc path]", 
          "excerpt": "[relevant quote]"
        }}
      ]
    }}
  ],
  "summary": "[overall compatibility assessment]",
  "rails_versions_supported": "[version range]"
}}

Focus on:
- **Deprecated Methods**: Identify deprecated Rails methods with safe modern replacements
- **Breaking Changes**: Point out code that breaks in newer Rails versions with fixes
- **Security Updates**: Modernize security calls safely (never remove protection)
- **Best Practices**: Suggest improvements following current Rails conventions

Return only valid JSON."""

# Simplified prompt for local models
LOCAL_PROMPT_TEMPLATE = """
Analyze this Rails file for upgrade compatibility. Based on the documentation context, identify potential issues and suggest fixes.

Context (Rails upgrade documentation):
{context_passages}

File to analyze: {file_path}
File content:
{file_content}

ANALYSIS:
Issues found:
1. [Issue description]
   - Location: Line X
   - Fix: [Suggested change]
   - Source: [Rails version/guide reference]

2. [Next issue...]

Note: Focus on common Rails upgrade patterns like ApplicationRecord, deprecated methods, configuration changes.
"""

def load_chunks(chunks_path: Path):
    """Return dict id->text from chunks.jsonl (used for provenance excerpts)."""
    d = {}
    if not chunks_path.exists():
        print(f"[!] chunks file not found: {chunks_path}", file=sys.stderr)
        return d
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            d[obj["id"]] = obj["text"]
    return d

def choose_target_files(repo_path: Path):
    """Find candidate files under app/controllers and app/models (ruby files)."""
    candidates = []
    for sub in ("app/controllers", "app/models"):
        p = repo_path / sub
        if p.exists():
            for f in p.rglob("*.rb"):
                candidates.append(f)
    return candidates

def build_context_passages(retriever: Retriever, snippet: str, top_k=5):
    """Query retriever and format passages into string for prompt."""
    results = retriever.search(snippet, top_k=top_k)
    lines = []
    for i, r in enumerate(results):
        meta = r["meta"]
        excerpt = meta.get("source_path", "unknown")
        lines.append(f"--- Passage {i+1} (score={r['score']:.3f}) ---")
        lines.append(f"Tag: {meta.get('tag')}; Source: {meta.get('source_path')}")
        # We don't include full chunk text here to keep prompt smaller; include short snippet:
        lines.append(f"Excerpt: {SnippetExcerpt(meta)}")
        lines.append("")  # blank line
    return "\n".join(lines), results

def SnippetExcerpt(meta):
    # If meta contains other fields, try to include short excerpt; otherwise show path
    return meta.get("source_path", "")  # actual chunk text is accessible separately in chunks.jsonl

def extract_analysis_from_text(text: str):
    """Extract analysis information from LLM output - try JSON first, then fallback to text parsing"""
    
    # First, try to extract JSON from the response
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            json_str = json_match.group(0)
            parsed_json = json.loads(json_str)
            
            # Validate that it has the expected structure
            if "edits" in parsed_json:
                return parsed_json
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to parse JSON from LLM output: {e}")
    
    # Fallback: Extract analysis information from free text 
    analysis = {
        "file": "",
        "raw_analysis": text[:2000],  # Keep first 2000 chars
        "edits": [],
        "issues_found": [],
        "suggestions": [],
        "summary": "Text-based analysis (no structured JSON)",
        "rails_versions_supported": "Unknown"
    }
    
    # Try to find patterns in the text that indicate Rails-related content
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['rails', 'activerecord', 'applicationrecord', 'deprecated', 'issue', 'suggestion']):
            if len(line) > 10:  # Skip very short lines
                analysis["suggestions"].append(line)
    
    return analysis

def run_for_file(llm, retriever, chunks_map, repo_path: Path, target_file: Path, top_k=5, max_new_tokens=512):
    print(f"\n=== Processing {target_file} ===")
    file_rel = target_file.relative_to(repo_path)
    file_content = target_file.read_text(encoding="utf-8", errors="replace")
    
    # Create Rails-specific search queries based on file content
    rails_queries = []
    content_lower = file_content.lower()
    
    # Detect common Rails patterns and create targeted queries
    if 'activerecord' in content_lower or 'class' in content_lower:
        rails_queries.append("Rails 5 ApplicationRecord ActiveRecord::Base upgrade")
    if 'controller' in file_rel.name.lower():
        rails_queries.append("Rails controller upgrade changes deprecations")
    if 'find_by' in content_lower:
        rails_queries.append("Rails deprecated find_by methods upgrade")
    if 'before_filter' in content_lower:
        rails_queries.append("Rails before_filter before_action upgrade")
    
    # Default query if no specific patterns found
    if not rails_queries:
        rails_queries.append(f"Rails upgrade {file_rel.name}")
    
    # Get context from multiple queries
    all_results = []
    for query in rails_queries[:2]:  # Limit to top 2 queries
        results = retriever.search(query, top_k=3)
        all_results.extend(results)
    
    # Remove duplicates and get top results
    seen_ids = set()
    unique_results = []
    for r in all_results:
        if r["id"] not in seen_ids:
            seen_ids.add(r["id"])
            unique_results.append(r)
            if len(unique_results) >= top_k:
                break
    
    # Enrich with context from chunks
    enriched_sources = []
    for r in unique_results:
        meta = r["meta"]
        cid = r["id"]
        excerpt_text = chunks_map.get(cid, "")[:400].replace("\n", " ")
        enriched_sources.append({
            "id": cid,
            "score": r["score"],
            "tag": meta.get("tag"),
            "source_path": meta.get("source_path"),
            "excerpt": excerpt_text
        })
    
    print(f"Found {len(enriched_sources)} relevant documentation chunks")
    for i, s in enumerate(enriched_sources):
        print(f"  {i+1}. {s['tag']} - {s['source_path'][:50]}... (Score: {s['score']:.3f})")
    # Choose prompt template based on LLM type
    use_gemini_prompt = isinstance(llm, GeminiLLM)
    prompt_template = GEMINI_PROMPT_TEMPLATE if use_gemini_prompt else LOCAL_PROMPT_TEMPLATE
    
    # build the prompt
    prompt = prompt_template.format(
        context_passages="\n".join([f"{i+1}. Tag:{s['tag']} Path:{s['source_path']} Score:{s['score']:.3f}\nExcerpt: {s['excerpt']}" for i,s in enumerate(enriched_sources)]),
        file_path=str(file_rel),
        file_content=file_content[:15000]  # truncate to keep prompt reasonably sized; LLM can ask for more in followup in prod
    )
    print("Calling LLM (this may take a moment)...")
    raw = llm.generate(prompt, max_new_tokens=max_new_tokens)
    
    # Parse analysis from LLM output (adapted for CodeGPT's text generation)
    try:
        parsed = extract_analysis_from_text(raw)
        parsed["file"] = str(file_rel)
    except Exception as e:
        print("ERROR parsing LLM output:", e)
        print("Raw LLM output (first 2000 chars):\n", raw[:2000])
        raise

    # Write analysis to output file instead of generating patches
    out_dir = repo_path / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    analysis_file = out_dir / f"analysis_{file_rel.name}.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)
    
    # Also write a readable report
    report_file = out_dir / f"report_{file_rel.name}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"Rails Upgrade Analysis for {file_rel}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Retrieved Context (Top {len(enriched_sources)} matches):\n")
        for i, s in enumerate(enriched_sources):
            f.write(f"{i+1}. {s['tag']} - {s['source_path']} (Score: {s['score']:.3f})\n")
            f.write(f"   {s['excerpt'][:200]}...\n\n")
        
        f.write("\nLLM Analysis:\n")
        f.write("-" * 30 + "\n")
        f.write(raw)
        f.write("\n\nExtracted Suggestions:\n")
        f.write("-" * 30 + "\n")
        for suggestion in parsed.get("suggestions", []):
            f.write(f"• {suggestion}\n")
    
    print(f"Analysis written to: {analysis_file}")
    print(f"Report written to: {report_file}")
    
    return [str(analysis_file), str(report_file)]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-path", required=True, help="Path to target rails repo (local).")
    parser.add_argument("--target-file", help="Relative path to single target file (optional).")
    parser.add_argument("--top-k", type=int, default=5, help="Top-k retrieved passages.")
    parser.add_argument("--max-tokens", type=int, default=512, help="Max new tokens for LLM generation.")
    parser.add_argument("--use-gemini", action="store_true", help="Use Gemini API instead of local model.")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        print(f"Repo path not found: {repo_path}", file=sys.stderr)
        sys.exit(1)

    # verify index and chunks exist
    for p in (Path(INDEX_PATH), Path(META_PATH), Path(CHUNKS_PATH)):
        if not p.exists():
            print(f"[ERROR] Required data missing: {p}. Run chunk/index build first.", file=sys.stderr)
            sys.exit(1)

    print("Loading retriever and LLM (this may take a bit)...")
    retriever = Retriever(str(INDEX_PATH), str(META_PATH))
    chunks_map = load_chunks(CHUNKS_PATH)
    
    # Choose LLM based on command line argument
    if args.use_gemini:
        print("Using Gemini API...")
        llm = GeminiLLM()
    else:
        print("Using local model...")
        llm = LocalLLM()  # uses current model configured in src/model/local_llm.py

    targets = []
    if args.target_file:
        targ = repo_path / Path(args.target_file)
        if not targ.exists():
            print(f"Target file not found: {targ}", file=sys.stderr)
            sys.exit(1)
        targets = [targ]
    else:
        targets = choose_target_files(repo_path)
        if not targets:
            print("No candidate files found under app/controllers or app/models. Specify --target-file.", file=sys.stderr)
            sys.exit(1)
        # optional: limit to top N for demo
        targets = targets[:10]

    all_written = []
    for t in targets:
        written = run_for_file(llm, retriever, chunks_map, repo_path, t, top_k=args.top_k, max_new_tokens=args.max_tokens)
        all_written.extend(written)

    print("Done. Generated patches:", all_written)

if __name__ == "__main__":
    main()
