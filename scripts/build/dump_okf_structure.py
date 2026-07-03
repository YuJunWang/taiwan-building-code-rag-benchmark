import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET_DIR = os.path.join(BASE_DIR, "data", "databases", "okf_knowledge")

def parse_simple_yaml_and_fallback(filepath):
    metadata = {}
    fallback = ""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith("---"):
                return metadata, content[:100].strip()
            parts = content.split("---", 2)
            if len(parts) < 3:
                return metadata, ""
            yaml_content = parts[1]
            body_content = parts[2].strip()
            
            # Remove main title header (e.g. "# 第181條")
            body_content = re.sub(r'^#\s+.*$', '', body_content, flags=re.MULTILINE).strip()
            # Clean up newlines for summary snippet
            fallback = re.sub(r'\s+', ' ', body_content)[:100].strip()
            if len(body_content) > 100:
                fallback += "..."
            
            # Simple line-by-line parsing for title and summary
            for line in yaml_content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                match = re.match(r'^(\w+)\s*:\s*(.*)$', line)
                if match:
                    key = match.group(1)
                    val = match.group(2).strip()
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    elif val.startswith("'") and val.endswith("'"):
                        val = val[1:-1]
                    metadata[key] = val
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return metadata, fallback

def dump_structure():
    structure = {}
    for root, dirs, files in os.walk(TARGET_DIR):
        # We calculate relative path from TARGET_DIR
        rel_path = os.path.relpath(root, TARGET_DIR)
        if rel_path == ".":
            # Target root folder itself
            continue
            
        subdirs = [d for d in dirs if d != "主題索引"]
        articles = []
        
        for file in files:
            if file.endswith('.md') and file != '_index.md':
                file_path = os.path.join(root, file)
                meta, fallback = parse_simple_yaml_and_fallback(file_path)
                title = meta.get('title', file.replace('.md', ''))
                summary = meta.get('summary', '').strip()
                if not summary:
                    summary = fallback
                articles.append({
                    "filename": file,
                    "title": title,
                    "summary": summary
                })
        
        # Only add if it contains subdirs or articles
        if subdirs or articles:
            structure[rel_path] = {
                "folder_name": os.path.basename(root),
                "subdirs": subdirs,
                "articles": articles
            }
            
    scratch_dir = os.path.join(BASE_DIR, "scratch")
    if not os.path.exists(scratch_dir):
        os.makedirs(scratch_dir)
        
    output_path = os.path.join(scratch_dir, "okf_structure.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"Dumped structure to {output_path}")

if __name__ == "__main__":
    dump_structure()
