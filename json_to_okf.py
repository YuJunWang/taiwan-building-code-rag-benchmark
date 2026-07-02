import json
import os
import re

def clean_filename(name):
    # Remove invalid characters for filenames and replace spaces
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.replace(" ", "_")
    return name.strip()

def main():
    json_path = "building_regulations.json"
    output_dir = "okf_knowledge"

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    law_title = data.get("title", "Unknown_Law")
    law_dir = os.path.join(output_dir, clean_filename(law_title))
    os.makedirs(law_dir, exist_ok=True)

    articles = data.get("articles", [])
    
    for item in articles:
        chapter = item.get("chapter", "").strip()
        article_no = item.get("article_no", "").strip()
        content = item.get("content", "").strip()
        
        # Clean article number for filename (e.g., "本條文有附件 第 1 條" -> extract "第 1 條")
        match = re.search(r'(第\s*\d+(?:-\d+)?\s*條)', article_no)
        if match:
            clean_article_no = match.group(1)
        else:
            clean_article_no = article_no
            
        filename = clean_filename(clean_article_no) + ".md"
        
        if chapter:
            chapter_dir = os.path.join(law_dir, clean_filename(chapter))
            os.makedirs(chapter_dir, exist_ok=True)
            filepath = os.path.join(chapter_dir, filename)
        else:
            filepath = os.path.join(law_dir, filename)

        # Build YAML frontmatter (OKF format)
        md_content = f"""---
title: "{clean_article_no}"
law: "{law_title}"
chapter: "{chapter}"
tags: ["{law_title}", "{clean_article_no}"]
---

# {clean_article_no}

{content}
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

    print(f"Successfully converted {len(articles)} articles to OKF format in '{output_dir}'.")

if __name__ == "__main__":
    main()
