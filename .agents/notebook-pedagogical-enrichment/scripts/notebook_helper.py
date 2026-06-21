#!/usr/bin/env python3
import sys
import json

def inspect_notebook(nb_path):
    try:
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
        
        print(f"Notebook: {nb_path}")
        print(f"Format: v{nb.get('nbformat')}.{nb.get('nbformat_minor')}")
        print(f"Total cells: {len(nb.get('cells', []))}")
        print("-" * 60)
        
        for i, cell in enumerate(nb.get("cells", [])):
            cell_type = cell.get("cell_type", "unknown")
            source_lines = cell.get("source", [])
            source_text = "".join(source_lines).strip()
            preview = source_text.split("\n")[0] if source_text else "[Empty]"
            print(f"Cell {i:02d} | Type: {cell_type:<10} | Preview: {preview[:80]}")
            
    except Exception as e:
        print(f"Error inspecting notebook: {e}", file=sys.stderr)

def clear_outputs(nb_path):
    try:
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
            
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "code":
                cell["outputs"] = []
                cell["execution_count"] = None
                
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=2)
        print(f"Cleared all outputs in {nb_path} successfully.")
    except Exception as e:
        print(f"Error clearing outputs: {e}", file=sys.stderr)

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  notebook_helper.py inspect <path_to_notebook.ipynb>")
        print("  notebook_helper.py clear-outputs <path_to_notebook.ipynb>")
        sys.exit(1)
        
    cmd = sys.argv[1]
    nb_path = sys.argv[2]
    
    if cmd == "inspect":
        inspect_notebook(nb_path)
    elif cmd == "clear-outputs":
        clear_outputs(nb_path)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
