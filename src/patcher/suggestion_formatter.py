#!/usr/bin/env python3
"""
Write patch files from LLM JSON output.

Expected JSON shape (top-level):
{
  "file": "app/controllers/xyz.rb",
  "edits": [
    {
      "target_start_line": 10,
      "target_end_line": 12,
      "patch": "... unified diff or replacement ...",
      "rationale": "...",
      "sources": [ { "tag": "v6.0.0", "source_path": "guides/..." , "excerpt": "..." } ]
    }
  ]
}
"""

import json
from pathlib import Path
import datetime

def ensure_unicode(s):
    return s if isinstance(s, str) else str(s)

def make_patch_filename(base_dir: Path, original_file: str):
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    name = Path(original_file).name
    safe = name.replace("/", "_")
    fname = f"{ts}__{safe}.patch"
    return base_dir / fname

def write_unified_patch(original_path: Path, start_line: int, end_line: int, patch_text: str, out_path: Path):
    """
    Simplest approach: write patch as a unified diff that replaces the given line range
    with the provided replacement text (patch_text can be unified-diff already or full replacement).
    If patch_text is already a unified diff starting with '---', we will use it directly.
    """
    if patch_text.strip().startswith("---") or patch_text.strip().startswith("@@"):
        # assume it's already a unified diff - write directly
        out_path.write_text(patch_text, encoding="utf-8")
        return

    # otherwise create a minimal replacement unified diff
    original_lines = original_path.read_text(encoding="utf-8", errors="replace").splitlines()
    # clip start/end to [1..len]
    start = max(1, start_line)
    end = min(len(original_lines), end_line)
    # lines we will replace
    before = original_lines[:start-1]
    after = original_lines[end:]
    new_lines = patch_text.splitlines()

    # Compose a small unified diff using simple headers
    old_chunk = "\n".join(original_lines[start-1:end])
    new_chunk = "\n".join(new_lines)
    diff = []
    diff.append(f"*** Begin Patch for {original_path} ***")
    diff.append(f"--- original\t(N/A)")
    diff.append(f"+++ patched\t(N/A)")
    diff.append(f"@@ -{start},{end-start+1} +{start},{len(new_lines)} @@")
    diff.append(new_chunk)
    diff.append(f"*** End Patch ***")
    out_path.write_text("\n".join(diff), encoding="utf-8")

def write_patches_from_response(parsed_json, repo_path: Path, out_dir: Path):
    """
    parsed_json: the JSON object returned by the LLM (after parsing)
    repo_path: Path to the repo root (so we can resolve relative file paths)
    out_dir: directory to write patch files to
    Returns: list of written patch file paths (strings)
    """
    written = []
    # if top-level is a list, handle each element
    items = parsed_json if isinstance(parsed_json, list) else [parsed_json]

    for item in items:
        file_rel = item.get("file")
        if not file_rel:
            continue
        orig_path = repo_path / file_rel
        if not orig_path.exists():
            # write a note file to indicate missing target
            note_path = make_patch_filename(out_dir, file_rel.with_suffix(".missing.txt"))
            note_path.write_text(f"Target file not found: {orig_path}\nFull JSON:\n{json.dumps(item, indent=2, ensure_ascii=False)}", encoding="utf-8")
            written.append(str(note_path))
            continue
        edits = item.get("edits", [])
        for i, ed in enumerate(edits):
            start = ed.get("target_start_line", 1)
            end = ed.get("target_end_line", start)
            patch_text = ensure_unicode(ed.get("patch", ""))
            rationale = ensure_unicode(ed.get("rationale", ""))
            confidence = ed.get("confidence", 0.0)
            risk = ed.get("risk", "unknown")
            requires_review = ed.get("requires_human_review", True)
            sources = ed.get("sources", [])
            
            # create filename
            pf = make_patch_filename(out_dir, f"{file_rel.replace('/', '_')}_{i}")
            
            # include metadata header + safety warnings + patch
            header = {
                "target": str(file_rel),
                "start": start,
                "end": end,
                "rationale": rationale,
                "confidence": confidence,
                "risk": risk,
                "requires_human_review": requires_review,
                "sources": sources
            }
            
            # Add safety warnings in header
            safety_warning = ""
            if risk in ["medium", "high"]:
                safety_warning = f"\n⚠️  WARNING: {risk.upper()} RISK CHANGE - Requires careful review!"
            if requires_review:
                safety_warning += f"\n🔍 HUMAN REVIEW REQUIRED - Do not apply automatically!"
            if confidence < 0.7:
                safety_warning += f"\n❓ LOW CONFIDENCE ({confidence:.1f}) - Verify before applying!"
                
            body = [
                f"### METADATA\n{json.dumps(header, ensure_ascii=False, indent=2)}",
                f"### SAFETY CHECKLIST{safety_warning}",
                "[ ] Code review completed",
                "[ ] Tests pass (bundle exec rails test)",
                "[ ] Security implications reviewed", 
                "[ ] Backup created before applying",
                "### PATCH\n", 
                patch_text
            ]
            pf.write_text("\n".join(body), encoding="utf-8")
            written.append(str(pf))
    return written
