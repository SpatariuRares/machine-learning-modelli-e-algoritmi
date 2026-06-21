#!/usr/bin/env python3
import json
import argparse
import sys
import os

def make_markdown_cell(text):
    lines = [line + "\n" for line in text.split("\n")]
    if lines and lines[-1] == "\n":
        lines.pop()
    elif lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {"cell_type": "markdown", "metadata": {}, "source": lines}

def make_code_cell(text):
    lines = [line + "\n" for line in text.split("\n")]
    if lines and lines[-1] == "\n":
        lines.pop()
    elif lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines
    }

def match_cell(cell, target, match_type, cell_type_filter=None):
    cell_type = cell.get("cell_type", "")
    if cell_type_filter and cell_type != cell_type_filter:
        return False
    source_text = "".join(cell.get("source", [])).strip()
    target_clean = target.strip()
    
    if match_type == "prefix":
        return source_text.startswith(target_clean)
    elif match_type == "contains":
        return target_clean in source_text
    elif match_type == "exact":
        return source_text == target_clean
    return False

def process_enrichment(notebook_cells, spec_items):
    new_cells = []
    
    for cell in notebook_cells:
        matched_specs = []
        for spec in spec_items:
            if spec.get("action") == "append":
                continue
            
            # Extract matching rules
            target = spec.get("target", "")
            match_type = spec.get("match_type", "prefix")
            cell_type_filter = spec.get("cell_type_filter")
            
            if match_cell(cell, target, match_type, cell_type_filter):
                matched_specs.append(spec)
                
        if not matched_specs:
            new_cells.append(cell)
            continue
            
        # Process the first match
        spec = matched_specs[0]
        action = spec.get("action", "insert_after")
        new_cell_type = spec.get("cell_type", "markdown")
        source_data = spec.get("source", "")
        
        source_text = "".join(source_data) if isinstance(source_data, list) else source_data
        
        if new_cell_type == "markdown":
            enriched_cell = make_markdown_cell(source_text)
        else:
            enriched_cell = make_code_cell(source_text)
            
        if action == "replace":
            new_cells.append(enriched_cell)
        elif action == "insert_before":
            new_cells.append(enriched_cell)
            new_cells.append(cell)
        elif action == "insert_after":
            new_cells.append(cell)
            new_cells.append(enriched_cell)
            
    # Process append specifications
    for spec in spec_items:
        if spec.get("action") == "append":
            new_cell_type = spec.get("cell_type", "markdown")
            source_data = spec.get("source", "")
            source_text = "".join(source_data) if isinstance(source_data, list) else source_data
            
            if new_cell_type == "markdown":
                enriched_cell = make_markdown_cell(source_text)
            else:
                enriched_cell = make_code_cell(source_text)
            new_cells.append(enriched_cell)
            
    return new_cells

def main():
    parser = argparse.ArgumentParser(description="Enrich a Jupyter notebook with pedagogical contents.")
    parser.add_argument("-n", "--notebook", required=True, help="Path to the target notebook (.ipynb) file")
    parser.add_argument("-s", "--spec", required=True, help="Path to the JSON specifications file")
    parser.add_argument("-o", "--output", help="Path to save the enriched notebook (defaults to overwriting target)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.notebook):
        print(f"Error: Notebook file '{args.notebook}' not found.", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(args.spec):
        print(f"Error: Spec file '{args.spec}' not found.", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(args.notebook, "r", encoding="utf-8") as f:
            nb = json.load(f)
            
        with open(args.spec, "r", encoding="utf-8") as f:
            spec_items = json.load(f)
            
        if not isinstance(spec_items, list):
            print("Error: Spec file must contain a JSON list of specifications.", file=sys.stderr)
            sys.exit(1)
            
        nb["cells"] = process_enrichment(nb.get("cells", []), spec_items)
        
        output_path = args.output if args.output else args.notebook
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=2)
            
        print(f"Success: Notebook '{output_path}' enriched successfully.")
        
    except Exception as e:
        print(f"Error during enrichment: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
