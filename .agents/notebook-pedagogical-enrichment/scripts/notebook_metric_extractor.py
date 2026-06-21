#!/usr/bin/env python3
import json
import argparse
import sys
import os
import tempfile
import subprocess

def extract_metrics(nb_path):
    # Determine the directory for the temporary file
    nb_dir = os.path.dirname(os.path.abspath(nb_path))
    
    # Create a temporary file in the same directory to prevent path/relative-import issues
    with tempfile.NamedTemporaryFile(suffix=".ipynb", dir=nb_dir, delete=False) as f:
        temp_path = f.name
        
    try:
        print(f"Executing {nb_path} to collect exact metrics...")
        
        # Run nbconvert inside the same virtual environment using sys.executable
        cmd = [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            nb_path,
            "--output",
            temp_path
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print("Error: Notebook execution failed.", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)
            
        with open(temp_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
            
        print("\n" + "=" * 60)
        print(f" EXECUTION METRICS FOR: {nb_path}")
        print("=" * 60 + "\n")
        
        for i, cell in enumerate(nb.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
                
            source_lines = cell.get("source", [])
            source_text = "".join(source_lines).strip()
            if not source_text:
                continue
                
            outputs = cell.get("outputs", [])
            if not outputs:
                continue
                
            # Print a concise preview of the code
            code_preview = "\n  ".join(source_text.split("\n")[:3])
            if len(source_text.split("\n")) > 3:
                code_preview += "\n  ..."
                
            print(f"Cell {i:02d} Code:\n  {code_preview}\n")
            print("Outputs:")
            
            for out in outputs:
                out_type = out.get("output_type")
                
                if out_type == "stream":
                    # stdout/stderr streams
                    text_lines = out.get("text", [])
                    text = "".join(text_lines) if isinstance(text_lines, list) else out.get("text", "")
                    prefix = f"  [{out.get('name', 'stream')}]: "
                    indented = "\n".join([f"    {line}" for line in text.strip().split("\n")])
                    print(f"{prefix}\n{indented}")
                    
                elif out_type in ("execute_result", "display_data"):
                    # cell returned values or rich output
                    data = out.get("data", {})
                    if "text/plain" in data:
                        text_lines = data["text/plain"]
                        text = "".join(text_lines) if isinstance(text_lines, list) else data["text/plain"]
                        indented = "\n".join([f"    {line}" for line in text.strip().split("\n")])
                        print(f"  [result]:\n{indented}")
                        
                elif out_type == "error":
                    # errors during execution
                    ename = out.get("ename", "Error")
                    evalue = out.get("evalue", "")
                    traceback = "\n".join(out.get("traceback", []))
                    print(f"  [error] {ename}: {evalue}\n{traceback}")
                    
            print("-" * 60)
            
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def main():
    parser = argparse.ArgumentParser(description="Execute a notebook and extract code execution outputs/metrics.")
    parser.add_argument("notebook", help="Path to the target notebook (.ipynb) file")
    args = parser.parse_args()
    
    if not os.path.exists(args.notebook):
        print(f"Error: Notebook file '{args.notebook}' not found.", file=sys.stderr)
        sys.exit(1)
        
    extract_metrics(args.notebook)

if __name__ == "__main__":
    main()
